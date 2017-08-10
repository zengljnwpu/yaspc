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
