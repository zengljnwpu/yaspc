#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:38:08 2017

@author: axiqia hellolzc(lzc80234@qq.com)
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock


DEBUG = True


def ConstructBlockList(instList):
    block = None
    number = 1
    blockDict = {}      # key is the number of instruction, and map to inst
    labelDict = {}      # key is the label of instruction, and map to block
    blockList = []
    labelSet = set()    # a set for valid label

    ''' find the valid label '''
    for inst in instList:
        if isinstance(inst, instruction.CJumpInst):
            labelSet.add(inst.gotoLabel)
        elif isinstance(inst, instruction.JumpInst):
            labelSet.add(inst.gotoLabel)

    ''' new the basic block '''
    i = 0
    labelFlag = 0
    ''' the ENTRY block '''
    block = BasicBlock.BasicBlock()
    block.blockNum = 0
    blockList.append(block)

    for inst in instList:
        i += 1
        if i == 1:
            """the first instruction of program"""
            block = BasicBlock.BasicBlock(number)
            blockList.append(block)
            blockDict[number] = block
            number += 1

            if (isinstance(inst, instruction.LabelInst)) and (inst.label in labelSet) :
                """ the first instruction is a label
                    and label is branch destination
                    and not a successive label inst
                    map label to block no.
                """
                #if block != None: block.instList.append(inst)
                labelDict[inst.label] = block.blockNum
                labelFlag = 1
                continue

            if isinstance(inst, instruction.CJumpInst):
                """ the first instruction is a conditional inst
                    malloc a new block for the following insts
                """
                block.instList.append(inst)

                block = BasicBlock.BasicBlock(number)
                blockList.append(block)
                blockDict[number] = block
                number += 1
                labelFlag = 0

                continue

            if isinstance(inst, instruction.JumpInst):
                """ non-conditional branch inst, the next inst do not belong to block"""
                block.instList.append(inst)
                block = None
                labelFlag = 0

                continue
        else: #i!=0  not the first instruction
            if (isinstance(inst, instruction.LabelInst)) and (inst.label in labelSet):
                """ the label instruction, map the label to number of block"""
                if labelFlag == 0: block = BasicBlock.BasicBlock(number)
                blockList.append(block)

                blockDict[number] = block
                labelDict[inst.label] = block.blockNum
                #if block != None: block.instList.append(inst)
                #print inst.label
                number += 1
                labelFlag = 1
                continue

            if isinstance(inst, instruction.CJumpInst):
                """the conditional branch inst"""
                if block != None: block.instList.append(inst)
                #print "gotoLabel", inst.gotoLabel
                block = BasicBlock.BasicBlock(number)
                blockList.append(block)

                blockDict[number] = block
                number += 1
                labelFlag = 0
                continue

            if isinstance(inst, instruction.JumpInst) or isinstance(inst, instruction.RetureInst):
                """ non-conditional branch inst, the next inst do not belong to block"""
                if block != None: block.instList.append(inst)
                #print "gotoLabel", inst.gotoLabel
                block = None
                labelFlag = 0
                continue
        #end if i==0
        if block != None:
            """add the inst to current block, unless the block is not none"""
            block.instList.append(inst)
            labelFlag = 0

    ''' the EXIT block '''
    block = BasicBlock.BasicBlock()
    block.blockNum = -1
    blockList.append(block)

    if(DEBUG):
        print("===================BasicBlock==================")
        for block in blockList:
            print(block.blockNum, ":")
            for inst in block.instList:
                print("\t", inst.context)
        print("===================LabelDict===================")
        for key, val in labelDict.items():
            print( key, val)
        print("===============================================")

    for i, block in enumerate(blockList):
        '''add jump target for every block'''
        if i == 0:
            """ the succblock of ENTRY is 1th block"""
            block.succBasicBlock.add(blockList[1])
            continue
        if i == len(blockList)-1:
            break
        inst = block.instList[-1]

        if isinstance(inst, instruction.JumpInst):
            """non-conditional inst, the succblock is only label successor"""
            number = labelDict[inst.gotoLabel]
            jumpBlock = blockDict[number]
            jumpBlock.preBasicBlock.add(block)
            block.succBasicBlock.add(jumpBlock)
            continue

        if isinstance(inst, instruction.CJumpInst):
            '''conditional inst, the succblock is label successor and next block'''
            number = labelDict[inst.gotoLabel]
            # successor
            cjumpBlock = blockDict[number]
            block.succBasicBlock.add(cjumpBlock)
            if i+1 < len(blockList)-1:
                followBlock = blockList[i+1]
                block.succBasicBlock.add(followBlock)
            #pre
            cjumpBlock.preBasicBlock.add(block)
            if i+1 < len(blockList)-1:
                followBlock.preBasicBlock.add(block)
            continue

        if isinstance(inst, instruction.RetureInst):
            jumpBlock = blockList[-1]
            jumpBlock.preBasicBlock.add(block)
            block.succBasicBlock.add(jumpBlock)
            continue

        if i+1 < len(blockList)-1:
            block.succBasicBlock.add(blockList[i+1])
            blockList[i+1].preBasicBlock.add(block)

    if DEBUG:
        print ("============PredecessorSuccessor==================")
        for block in blockList:
            print(block.blockNum, ":")
            for inst in block.instList:
                print("\t", inst.context)
            if len(block.succBasicBlock) != 0:
                for succblock in block.succBasicBlock:
                    print("succblock:", succblock.blockNum)
            if len(block.preBasicBlock) != 0:
                for preblock in block.preBasicBlock:
                    print ("preblock", preblock.blockNum)
    return blockList

















