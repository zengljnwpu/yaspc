#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 14:38:08 2017

@author: axiqia zhaoci
"""
import sys
sys.path.append("..")
import Instruction.instruction as instruction
import BasicBlock
'''
def ConstructInstList():
    instList = []
    inst = instruction.BinaryInst()
    instList.append(inst)
    return instList
'''
def ConstructBlockList(instList):
    #instList = ConstructInstList()

    block = None
    number = 0
    blockDict = {}      #key is the number of instruction, and map to inst
    labelDict = {}      #key is the label of instruction, and map to block
    blockList = []
    i = -1                    #
    for inst in instList:
        i += 1
        if i == 0:
            """the first instruction of program"""
            block = BasicBlock.BasicBlock()
            block.no = number
            blockDict[number] = block
            number += 1

            blockList.append(block)

        if isinstance(inst, instruction.LabelInst):
            """ the label instruction, map the label to number of block"""
            block = BasicBlock.BasicBlock()
            block.no = number
            blockDict[number] = block
            number += 1

            blockList.append(block)
            labelDict[inst.label] = block.no

        if isinstance(inst, instruction.CJumpInst):
            """the conditional branch inst"""
            block.instList.append(inst)

            block = BasicBlock.BasicBlock()
            block.no = number
            number += 1
            blockDict[number] = block
            continue

        if isinstance(inst, instruction.JumpInst):
            """ non-conditional branch inst, the next inst do not belong to block"""
            block.instList.append(inst)
            block = None
            continue

        if block != None:
            """add the inst to current block, unless the block is not none"""
            block.instList.append(inst)
    i = 0
    for block in blockList:
        i += 1
        inst = block.instList[-1]
        if isinstance(inst, instruction.JumpInst):
            """non-conditional inst, the succblock is only label successor"""
            number = labelDict[inst.gotLabel]
            succBlock = blockDict[number]
            succBlock.preBasicBlock.append(block)
            block.ssuccBasicBlock.append(succBlock)
            continue

        if isinstance(inst, instruction.CJumpInst):
            '''conditional inst, the succblock is label successor and next block'''
            number = labelDict[inst.gotoLabel]
            # There is a error here
            succBlock = blockDict[number]

            #add block
            succBlock.preBasicBlock.add(block)
            blockList[i+1].preBasicBlock.add(block)

            block.succBasicBlock.add(succBlock)
            block.succBasicBlock.add(blockList[i+1])
            continue

        block.succBasicBlock.add(blockList[i+1])
        blockList[i+1].preBasicBlock.add(block)





















