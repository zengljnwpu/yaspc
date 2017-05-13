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
    '''TODO: There is a big logical problem here which need fix'''
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
            blockList.append(block)
            blockDict[number] = block
            number += 1
            
            if isinstance(inst, instruction.LabelInst):
                """the first instruction is a label, only map labe to block no."""
                labelDict[inst.label] = block.blockNum
                
                
            if isinstance(inst, instruction.CJumpInst): 
                """ the first instruction is a conditional inst
                    malloc a new block for the following insts
                """
                block.instList.append(inst)
                block = BasicBlock.BasicBlock(number)
                blockList.append(block)
                blockDict[number] = block
                number += 1
                
                continue
            
            if isinstance(inst, instruction.JumpInst):
                """ non-conditional branch inst, the next inst do not belong to block"""
                block.instList.append(inst)
                block = None    
                
                continue
            
        if isinstance(inst, instruction.LabelInst):
            """ the label instruction, map the label to number of block"""
            block = BasicBlock.BasicBlock(number)
            blockList.append(block)
            
            blockDict[number] = block
            labelDict[inst.label] = block.blockNum
            #print inst.label
            number += 1

            

        if isinstance(inst, instruction.CJumpInst):
            """the conditional branch inst"""
            block.instList.append(inst)
            #print "gotoLabel", inst.gotoLabel
            block = BasicBlock.BasicBlock(number)
            blockList.append(block)
            
            blockDict[number] = block
            number += 1

            continue

        if isinstance(inst, instruction.JumpInst):
            """ non-conditional branch inst, the next inst do not belong to block"""
            block.instList.append(inst)
            #print "gotoLabel", inst.gotoLabel
            block = None
            continue

        if block != None:
            """add the inst to current block, unless the block is not none"""
            block.instList.append(inst)
  
    
    #debug 
    for block in blockList:
        print block.blockNum, ":"
        for inst in block.instList:
            print "\t", inst.context
    for key, val in labelDict.items():
        print key, val
            
    i = 0
    for block in blockList:
        
        inst = block.instList[-1]
        if isinstance(inst, instruction.JumpInst):
            """non-conditional inst, the succblock is only label successor"""
            number = labelDict[inst.gotoLabel]
            jumpBlock = blockDict[number]
            jumpBlock.preBasicBlock.add(block)
            block.succBasicBlock.add(jumpBlock)
            i = i+1
            continue

        if isinstance(inst, instruction.CJumpInst):
            '''conditional inst, the succblock is label successor and next block'''
            number = labelDict[inst.gotoLabel]
            # successor
            cjumpBlock = blockDict[number]
            block.succBasicBlock.add(cjumpBlock)
            if i+1 < len(blockList):
                followBlock = blockList[i+1]
                block.succBasicBlock.add(followBlock)
            
            #pre
            cjumpBlock.preBasicBlock.add(block)
            if i+1 < len(blockList):
                followBlock.preBasicBlock.add(block)
            i = i+1
            continue
        if i+1 < len(blockList):
            block.succBasicBlock.add(blockList[i+1])
            blockList[i+1].preBasicBlock.add(block)
        i = i+1

    #debug
    for block in blockList:
        print block.blockNum, ":"
        for inst in block.instList:
            print "\t", inst.context
        if len(block.succBasicBlock) != 0:
            for succblock in block.succBasicBlock:
                print "succblock:" ,succblock.blockNum
        if len(block.preBasicBlock) != 0:
            for preblock in block.preBasicBlock:
                print "preblock", preblock.blockNum

            

















