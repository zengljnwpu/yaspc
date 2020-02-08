#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Fri May 12 14:38:08 2017

@author: axiqia hellolzc(lzc80234@qq.com)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from optimization.IR_IO import instruction
from optimization.BasicBlock import BasicBlock
from optimization.Peephole import PeepholeOptimization

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print


def SplitBasicBlock(inst_list, blockDict, labelDict, blockList):
    """Split instructions into different basic block
    Construct a list of block named blockList,
    every block has a block num, and we map the num to the block named blockDict
    the first block num is 0, which is the ENTRY block,
    the last block num is -1, which is the EXIT block and we can index by -1 in python,
    it's must be noted that there is no labelInst in every block,
    and we map the label name of labelInst to block num named labelDict

    :type inst_list: list
    :param inst_list: a list of instructions

    :type blockDict: dict
    :param blockDict: key is the number of block, and map to block object

    :type labelDict: dict
    :param labelDict: key is the label of instruction, and map to block object

    :type blockList: list
    :param blockList: a list of basic block
    """

    ''' add the ENTRY block '''
    block_number = 0
    block = BasicBlock.BasicBlock(block_number)
    blockList.append(block)
    block = None

    for inst in inst_list:
        """ block是None，预示着一个新基本块的开始 """
        if block is None:
            block_number = block_number + 1
            block = BasicBlock.BasicBlock(block_number)

        if isinstance(inst, instruction.LabelInst):
            """ 当前指令是Label指令，要注意的是后续的也有可能还是Label指令，要特殊处理 """
            """
            若Label指令是第一条指令，或该Label指令之前还是Label指令，block中的指令数量一定为0,
            若大于0,则说明该Label指令是一个新的基本块的开始
            """
            if block.get_inst_number() > 0:
                blockList.append(block)
                blockDict[block_number] = block
                block_number = block_number + 1
                block = BasicBlock.BasicBlock(block_number)

            labelDict[inst.labelname] = block_number

        elif isinstance(inst, (instruction.CJumpInst, instruction.JumpInst)):
            """
            当前指令的跳转指令，跳转的目的指令是下一个基本块的开始指令，
            同时该指令的下一条指令也是新的基本块的开始指令，即该指令是该基本块的结束
            """
            block.add_inst(inst)
            blockList.append(block)
            blockDict[block_number] = block
            block = None
        
        else:
            """ 对于普通指令，直接添加就好
            """
            block.add_inst(inst)

    """ 结尾的基本块 """
    if block is not None:
        blockList.append(block)
        blockDict[block_number] = block

    ''' add the EXIT block to blockList'''
    block = BasicBlock.BasicBlock(-1)
    blockList.append(block)

    if DEBUG:
        print("===================BasicBlock==================")
        for block in blockList:
            print(block.blockNum, ":")
            for inst in block.instList:
                print("\t", inst.pos, inst)
        print("===================LabelDict===================")
        for key, val in labelDict.items():
            print(key, val)
        print("===============================================")


def LinkBasicBlock(inst_list, blockDict, labelDict, blockList):
    """
    Link basic block among each other

    For every block in block list,
        the last instruction must be a JumpInst, CJumpInst, or ReturnInst
    so we can index labelDict by label name to get the succBasicBlock' blockNum,
    and index blockDict by the blockNum to get the block,
    then we can get preBasicBlock of the succBasicBlock

    :type inst_list: list
    :param inst_list: a list of instructions

    :type blockDict: dict
    :param blockDict: key is the number of block, and map to block object

    :type labelDict: dict
    :param labelDict: key is the label of instruction, and map to block object

    :type blockList: list
    :param blockList: a list of basic block
    """

    for i, block in enumerate(blockList):
        '''add jump target for every block'''

        if block.blockNum == 0:
            """ 第一个基本块肯定是Entry块，后续的肯定是第一个基本块 """
            block.add_succ((blockList[1], "follow"))
            blockList[1].add_prev(block)
            continue
        elif block.blockNum == -1:
            """ 最后一个尾基本块 """
            break

        """ 其它正常指令的基本块 """

        """ 查看基本块的最后一条指令 """
        inst = block.instList[-1]

        if isinstance(inst, instruction.JumpInst):
            """non-conditional inst, the succblock is only label successor"""

            """ 取得当前指令跳转的目标，查找目标地址指令 """
            number = labelDict[inst.label]
            if number is None:
                """ 如果不存在，则弹出异常，这说明指令序列有问题 """
                break

            jumpBlock = blockDict[number]
            jumpBlock.add_prev(block)
            block.add_succ((jumpBlock, "label"))
            continue

        if isinstance(inst, instruction.CJumpInst):
            '''
            当前指令为有条件跳转指令，后继有两个，一个为真(thenLabel)，一个为假(elseLabel),
            前序一个
            '''

            """ 取得当前指令跳转的目标(真和假共两个，thenLabel, elseLabel)，查找目标地址指令 """
            """ then label """
            then_number = labelDict[inst.thenlabel]
            if then_number is None:
                """ 如果不存在，则弹出异常，这说明指令序列有问题 """
                break

            # successor
            cjumpBlock = blockDict[then_number]
            block.add_succ((cjumpBlock, "thenlabel"))
            # pre
            cjumpBlock.add_prev(block)

            """ else label """
            else_number = labelDict[inst.elselabel]
            if else_number is None:
                """ 如果不存在，则弹出异常，这说明指令序列有问题 """
                break

            # successor
            cjumpBlock = blockDict[else_number]
            block.add_succ((cjumpBlock, "elselabel"))
            # pre
            cjumpBlock.add_prev(block)

            continue

        if isinstance(inst, instruction.RetureInst):
            """
            当前指令为返回指令，其后继块为尾部块(-1)
            """
            jumpBlock = blockList[-1]
            jumpBlock.add_prev(block)
            block.add_succ((jumpBlock, "return"))
            continue

        """
        其它指令为顺序执行相关的指令，当前基本块的后继是下一个基本块，后继的前一个基本块为当前block
        此时，这里的i值肯定不是是最后一个，因最后一个是尾部Block
        """
        block.add_succ((blockList[i + 1], "follow"))
        blockList[i + 1].add_prev(block)

    if DEBUG:
        print("============PredecessorSuccessor==================")
        for ith, inst in enumerate(inst_list):
            ith
            print(inst.pos, inst)
        for block in blockList:
            print(block.blockNum, ":")
            for inst in block.instList:
                print("\t", inst)
            if len(block.succBasicBlock) != 0:
                for succblock in block.succBasicBlock:
                    print("succblock: %d:%s" % (succblock[0].blockNum, str(succblock[1])))
            if len(block.preBasicBlock) != 0:
                for preblock in block.preBasicBlock:
                    print("preblock", preblock.blockNum)


def ConstructBlockList(inst_list):
    """Construct basic block list
    Remove the unused label,
    split the basic block and
    link the succeed basic block and precursor basic block

    :type inst_list: list
    :param inst_list: a list of every instruction

    :return: blockList: a list of basic block
    """
    ''' remove the invalid label '''
    inst_list = PeepholeOptimization.remove_unused_label(inst_list)

    blockDict = {}      # key is the number of block, and map to block object
    labelDict = {}      # key is the label of instruction, and map to block object
    blockList = []

    SplitBasicBlock(inst_list, blockDict, labelDict, blockList)
    LinkBasicBlock(inst_list, blockDict, labelDict, blockList)
    blockList = PeepholeOptimization.dead_code_elimination(blockList)

    return blockList










