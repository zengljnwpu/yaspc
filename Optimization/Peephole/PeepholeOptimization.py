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

from yaspc.Optimization.IR_IO import instruction

DEBUG = True

def remove_unused_label(inst_list):
    """remove unused label"""
    # remove a JumpInst if its target is followed label
    new_inst_list = []
    for inst_no, inst in enumerate(inst_list):
        if isinstance(inst, instruction.JumpInst):
            if inst_no+1 < len(inst_list) and inst.label == inst_list[inst_no+1].labelname:
                continue
        new_inst_list.append(inst)
    inst_list = new_inst_list
    # find the valid label
    used_label_set = set()    # a set for valid label
    for inst in inst_list:
        if isinstance(inst, instruction.CJumpInst):
            used_label_set.add(inst.thenlabel)
            used_label_set.add(inst.elselabel)
        elif isinstance(inst, instruction.JumpInst):
            used_label_set.add(inst.label)
    # remove unused label
    new_inst_list = []
    for inst in inst_list:
        if isinstance(inst, instruction.LabelInst):
            if not inst.labelname in used_label_set:
                continue
        new_inst_list.append(inst)
    return new_inst_list


def control_flow_optimization(block_list, inst_list):
    """控制流优化"""
    for block in block_list[::-1]:
        """
            find unconditional jump instruction and has been labeled
        """
        if len(block.instList) == 1 and isinstance(block.instList[0], instruction.JumpInst):
            label = block.instList[0].label
            for preblock in block.preBasicBlock:
                preinst = preblock.instList[-1]
                if isinstance(preinst, instruction.JumpInst):
                    preinst.label = label
                elif isinstance(preinst, instruction.CJumpInst):
                    for pre_succ in preblock.succBasicBlock:
                        if pre_succ[0] == block:
                            if pre_succ[1] == "thenlabel":
                                preinst.thenlabel = label
                                change = False
                            else:
                                preinst.elselabel = label
                                change = False

    if DEBUG:
        for ith, inst in enumerate(inst_list):
            #inst.pos = ith
            print(inst.pos, inst)
        print ("============Opti:PredecessorSuccessor==================")
        for block in block_list:
            print(block.blockNum, ":")
            for inst in block.instList:
                print("\t", inst)
            if len(block.succBasicBlock) != 0:
                for succblock in block.succBasicBlock:
                    print("succblock: %d:%s" % (succblock[0].blockNum, str(succblock[1])))
            if len(block.preBasicBlock) != 0:
                for preblock in block.preBasicBlock:
                    print("preblock", preblock.blockNum)
    return inst_list
