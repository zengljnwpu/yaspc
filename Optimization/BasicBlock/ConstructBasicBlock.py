#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:38:08 2017

@author: axiqia hellolzc(lzc80234@qq.com)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from Optimization.IR_IO import instruction
from Optimization.BasicBlock import BasicBlock
from Optimization.Peephole import PeepholeOptimization

DEBUG = False


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

    ''' new the basic block '''
    number = 1
    i = 0
    labelFlag = 0

    ''' add the ENTRY block '''
    block = BasicBlock.BasicBlock()
    block.blockNum = 0
    blockList.append(block)

    for inst in inst_list:
        i += 1
        if i == 1:
            """the first instruction of program"""
            block = BasicBlock.BasicBlock(number)
            number += 1
            blockList.append(block)
            blockDict[block.blockNum] = block

            if isinstance(inst, instruction.LabelInst):
                """ the first instruction is a label
                    and label is branch destination
                    and not a successive label inst
                    map label to block no.
                """
                labelDict[inst.labelname] = block.blockNum
                labelFlag = 1
                continue

            if isinstance(inst, instruction.CJumpInst):
                """ the first instruction is a conditional inst
                    malloc a new block for the following insts
                """
                block.instList.append(inst)

                block = BasicBlock.BasicBlock(number)
                number += 1
                blockList.append(block)
                blockDict[block.blockNum] = block

                labelFlag = 0

                continue

            if isinstance(inst, instruction.JumpInst):
                """ non-conditional branch inst, the next inst do not belong to block"""
                block.instList.append(inst)
                block = None
                labelFlag = 0

                continue
        else:
            # i!=0  not the first instruction
            if isinstance(inst, instruction.LabelInst):
                """ the label instruction, map the label to number of block"""
                if labelFlag == 0:
                    block = BasicBlock.BasicBlock(number)
                    number += 1
                    blockList.append(block)

                blockDict[block.blockNum] = block
                labelDict[inst.labelname] = block.blockNum
                # if block != None: block.instList.append(inst)
                # print inst.label

                labelFlag = 1
                continue

            if isinstance(inst, instruction.CJumpInst):
                """the conditional branch inst"""
                if block != None:
                    block.instList.append(inst)

                # print "gotoLabel", inst.gotoLabel
                block = BasicBlock.BasicBlock(number)
                number += 1
                blockList.append(block)

                blockDict[block.blockNum] = block

                labelFlag = 1
                continue

            if isinstance(inst, instruction.JumpInst) or isinstance(inst, instruction.RetureInst):
                """ non-conditional branch inst, the next inst do not belong to block"""
                if block != None: block.instList.append(inst)
                # print "gotoLabel", inst.gotoLabel
                block = None
                labelFlag = 0
                continue
        # end if i==0
        if block != None:
            """add the inst to current block, unless the block is not none"""
            block.instList.append(inst)
            labelFlag = 0

    ''' add the EXIT block to blockList'''
    block = BasicBlock.BasicBlock()
    block.blockNum = -1
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
    """Link basic block among each other 
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
        if i == 0:
            """ the succblock of ENTRY is 1th block"""
            block.succBasicBlock.add((blockList[1], "follow"))
            blockList[1].preBasicBlock.add(block)
            continue
        if i == len(blockList) - 1:
            break
        inst = block.instList[-1]

        if isinstance(inst, instruction.JumpInst):
            """non-conditional inst, the succblock is only label successor"""
            number = labelDict[inst.label]
            jumpBlock = blockDict[number]
            jumpBlock.preBasicBlock.add(block)
            block.succBasicBlock.add((jumpBlock, "label"))
            continue

        if isinstance(inst, instruction.CJumpInst):
            '''conditional inst, the succblock is label successor and next block'''
            """ then label """
            then_number = labelDict[inst.thenlabel]
            # successor
            cjumpBlock = blockDict[then_number]
            block.succBasicBlock.add((cjumpBlock, "thenlabel"))
            # pre
            cjumpBlock.preBasicBlock.add(block)

            """ else label """
            else_number = labelDict[inst.elselabel]
            # successor
            cjumpBlock = blockDict[else_number]
            block.succBasicBlock.add((cjumpBlock, "elselabel"))
            # pre
            cjumpBlock.preBasicBlock.add(block)

            continue

        if isinstance(inst, instruction.RetureInst):
            jumpBlock = blockList[-1]
            jumpBlock.preBasicBlock.add(block)
            block.succBasicBlock.add((jumpBlock, "return"))
            continue

        if i + 1 < len(blockList) - 1:
            block.succBasicBlock.add((blockList[i + 1], "follow"))
            blockList[i + 1].preBasicBlock.add(block)

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

    return blockList










