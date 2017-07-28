#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窥孔优化
@Time : 17-5-29 1:23pm
@Author : axiqia hellolzc
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Optimization.IR_IO import instruction

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

def show_instructions(inst_list):
    for ith, inst in enumerate(inst_list):
        ith
        print(inst.pos, inst)

def show_basic_blocks(block_list):

    for block in block_list:
        print(block.blockNum, ":")

        # 显示该块的所有指令
        for inst in block.instList:
            print("\t", inst)

        # 显示当前块的后继基本块
        for succblock in block.succBasicBlock:
            print("succblock: %d:%s" % (succblock[0].blockNum, str(succblock[1])))

        # 显示当前块的前序基本块
        for preblock in block.preBasicBlock:
            print("preblock", preblock.blockNum)

def get_used_labels(inst_list):
    ''' 遍历所有的指令查找跳转的Label一览 '''

    used_labels = set()

    for inst in inst_list:
        if isinstance(inst, instruction.CJumpInst):
            used_labels.add(inst.thenlabel)
            used_labels.add(inst.elselabel)
        elif isinstance(inst, instruction.JumpInst):
            used_labels.add(inst.label)

    return  used_labels

def remove_unused_label(inst_list):
    """remove unused label"""

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
    used_label_set = get_used_labels(inst_list)

    # remove unused label
    new_inst_list = []
    for inst in inst_list:

        # 若当前指令为Label指令，并且该Label没有被使用，则忽略之
        if isinstance(inst, instruction.LabelInst) and \
            not inst.labelname in used_label_set:
            continue

        new_inst_list.append(inst)

    return new_inst_list

def replace_preblock_label(block, label):
    '''
    遍历其前序基本块，查看前序基本块的最后指令
    若最后的指令为无条件跳转指令，则跳转的Label修改为当前基本块中指令的Label
    若最后的指令为有条件跳转指令，则更改其中为当前指令Label的分支Label
    '''

    for preblock in block.preBasicBlock:
        preinst = preblock.instList[-1]
        if isinstance(preinst, instruction.JumpInst):
            preinst.label = label
        elif isinstance(preinst, instruction.CJumpInst):
            for pre_succ in preblock.succBasicBlock:
                if pre_succ[0] == block:
                    if pre_succ[1] == "thenlabel":
                        preinst.thenlabel = label
                    else:
                        preinst.elselabel = label


def control_flow_optimization(block_list, inst_list):
    """控制流优化
    注意：做完控制流优化后基本块需要重新构建
    """

    for block in block_list[::-1]:
        """
            find unconditional jump instruction and has been labeled
        """
        if len(block.instList) == 1 and isinstance(block.instList[0], instruction.JumpInst):
            ''' 当前基本块中只有一条指令并且该指令为无条件跳转指令 '''

            ''' 取当前无条件跳转指令的转向Label '''
            label = block.instList[0].label

            '''
            遍历其前序基本块，查看前序基本块的最后指令
            若最后的指令为无条件跳转指令，则跳转的Label修改为当前基本块中指令的Label
            若最后的指令为有条件跳转指令，则更改其中为当前指令Label的分支Label
            '''
            replace_preblock_label(block, label)

    if DEBUG:
        show_instructions(inst_list)
        print ("============Opti:PredecessorSuccessor==================")
        show_basic_blocks(block_list)

    return inst_list

def dead_code_elimination(block_list):
    """删除到达不了的基本块
    返回更新过的block_list
    """
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

    return block_list
