#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: hellolzc(lzc80234@qq.com) axiqia
# Date: 2017/5/30
"""
输入basicblock list，输出instruction list
注意要更新ir中的labellist
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock
import copy

DEBUG = True


def BlockList_to_InstList(block_list):
    """deconstruct basicblock
    """
    inst_list = []

    for curblock in block_list:
        # ENTRY BLOCK
        if curblock.blockNum == 0:
            continue
        # 先给所有block入口加label，之后可以考虑在窥孔优化中删除
        block_label_inst = curblock.gen_block_label_inst()
        inst_list.append(block_label_inst)
        # EXIT BLOCK
        if curblock.blockNum == -1:
            continue
        # 根据最后一条语句做判断
        inst_list.extend(curblock.instList)
        # make a shallow copy 防止修改对原来的指令造成影响
        last_inst = copy.copy(curblock.get_last_inst())
        if isinstance(last_inst, instruction.CJumpInst):
            # 修改条件跳转语句的label(string类型)
            last_inst.thenlabel = curblock.get_succ_then_block().gen_block_label_string()
            last_inst.elselabel = curblock.get_succ_else_block().gen_block_label_string()
        elif isinstance(last_inst, instruction.JumpInst):
            # 修改无条件跳转语句的label(string类型)
            last_inst.label = curblock.get_succ_unique_block().gen_block_label_string()
        else:
            # 不做处理
            pass
        inst_list[-1] = last_inst
    if DEBUG:
        print ("============LinearInstructionList==================")
        for ith, inst in enumerate(inst_list):
            # pos需要重新编号，以便于之后生成labellist
            inst.pos = ith + 1
            print('%3d\t%s'%(inst.pos, str(inst)))
    return inst_list
