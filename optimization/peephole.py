# -*- coding: utf-8 -*-

"""
Created : 2017/8/7
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from optimization import instruction
from optimization import function_optimizer

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class ControlFlowOptimizer(function_optimizer.FunctionOptimizer):
    """ControlFlowOptimizer class
    """
    def __init__(self):
        super(ControlFlowOptimizer, self).__init__()

    def __get_used_labels(self):
        ''' 遍历所有的指令查找跳转的Label一览 '''
        inst_list = self.data_unit.get_inst_list()

        used_labels = set()

        for inst in inst_list:
            if isinstance(inst, instruction.CJumpInst):
                used_labels.add(inst.thenlabel)
                used_labels.add(inst.elselabel)
            elif isinstance(inst, instruction.JumpInst):
                used_labels.add(inst.label)

        return  used_labels

    def remove_unused_label(self):
        """remove unused label"""
        inst_list = self.data_unit.get_inst_list()

        # remove a JumpInst if its target is followed label
        new_inst_list = []
        for inst_no, inst in enumerate(inst_list):

            '''
            如果当前指令是无条件跳转指令并且下一条指令刚好是跳转的目的地指令(Label)，可忽略掉该无条件跳转指令
            '''
            if isinstance(inst, instruction.JumpInst) and ((inst_no + 1) < len(inst_list)) and \
                isinstance(inst, instruction.LabelInst) and  inst.label == inst_list[inst_no + 1].labelname:
                continue

            ''' 其它指令则保留 '''
            new_inst_list.append(inst)

        inst_list = new_inst_list

        # 遍历所有的指令查找跳转的Label一览
        used_label_set = self.__get_used_labels()

        # remove unused label
        new_inst_list = []
        for inst in inst_list:

            # 若当前指令为Label指令，并且该Label没有被使用，则忽略之
            if isinstance(inst, instruction.LabelInst) and \
                not inst.labelname in used_label_set:
                continue

            new_inst_list.append(inst)

        return new_inst_list

    @classmethod
    def __replace_preblock_target(cls, block, label, new_succ):
        '''
        遍历其前序基本块，修改其后继为new_succ
        查看前序基本块的最后指令，
            若最后的指令为无条件跳转指令，则跳转的Label修改为当前基本块中指令的Label
            若最后的指令为有条件跳转指令，则更改其中为当前指令Label的分支Label

        '''

        for preblock in block.preBasicBlock:
            preinst = preblock.instList[-1]
            if isinstance(preinst, instruction.JumpInst):
                preinst.label = label
                # TODO:
            elif isinstance(preinst, instruction.CJumpInst):
                for pre_succ in preblock.succBasicBlock:
                    if pre_succ[0] == block:
                        if pre_succ[1] == "thenlabel":
                            preinst.thenlabel = label
                        else:
                            preinst.elselabel = label

    @classmethod
    def __control_flow_optimization(cls, block_list):
        """控制流优化
        """

        for block in block_list[::-1]:
            """
                find unconditional jump instruction and has been labeled
            """
            if len(block.instList) == 1 and isinstance(block.instList[0], instruction.JumpInst):
                ''' 当前基本块中只有一条指令并且该指令为无条件跳转指令
                '''

                ''' 取当前无条件跳转指令的转向Label和唯一后继 '''
                label = block.instList[0].label
                unique_succ = block.get_succ_unique_block()

                '''
                不妨设当前基本块为B2，前驱为B1(可能有多个,记为B1',B1'')，后继为B3(只有一个)
                1. 遍历其前序基本块，查看前序基本块的最后指令
                 *若B1最后的指令为无条件跳转指令，则跳转的Label修改为当前基本块B2中指令的Label
                 *若B1最后的指令为有条件跳转指令，则更改其中为当前指令Label的分支Label
                2. 修改前序基本块的后继，将出现的B2改为B3，接着：
                 *在B2中的前驱中删掉B1
                 *在B3的前驱中加上B1
                这样，B1到达B2的弧被改成B1到B3
                处理了当前基本块B2所有前驱后，B2变得不可达，调用dead_code_elimination删除它
                '''
                cls.__replace_preblock_target(block, label, unique_succ)
                # TODO:


    def control_flow_optimization(self):
        """控制流优化
        注意：做完控制流优化后基本块需要重新构建
        TODO:控制流优化同时使用了instList和blockList，instList和blockList这两个不应该同时存在的，需要重写控制流优化
        """
        pass

    def dead_code_elimination(self):
        """删除到达不了的基本块
        返回更新过的block_list
        """
        block_list = self.data_unit.get_block_list()
        # 循环直到找不到死节点为止
        loop_change_flag = True
        while loop_change_flag:
            loop_change_flag = False
            new_block_list = []
            for block in block_list:
                if block.blockNum != 0 and block.blockNum != -1:
                    if len(block.preBasicBlock) == 0:
                        # 到达不了的节点不加入new_block_list中，且如果死节点有后继，删除后继基本块的相关信息
                        loop_change_flag = True
                        for succ_block, _ in block.succBasicBlock:
                            succ_block.preBasicBlock.remove(block)
                        if DEBUG:
                            print("delete block %d"%block.blockNum)
                        continue
                new_block_list.append(block)
            block_list = new_block_list
        #return block_list
        self.data_unit.set_block_list(block_list)
