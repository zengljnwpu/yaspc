#!/usr/bin/env python

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
    
    labelFlag = 0

    ''' add the ENTRY block '''
    block = BasicBlock.BasicBlock(0)
    blockList.append(block)

    ''' 第一个指令所在的块 '''
    block = BasicBlock.BasicBlock(1)
    blockList.append(block)
    blockDict[1] = block
    
    ''' 下一个指令的块号 '''
    number = 2
        
    i = 0
    for inst in inst_list:
        i += 1
        
        new_block = False
        new_inst = True
        
        if i == 1:
            """the first instruction of program"""
            
            if isinstance(inst, instruction.LabelInst):
                """ 当前指令是Label指令，要注意的是后续的也有可能还是Label指令，要特殊处理 """
                labelFlag = 1
                new_inst = False
  
            elif isinstance(inst, instruction.CJumpInst):
                """ 
                当前指令的条件跳转指令，跳转的目的指令是下一个基本块的开始指令，
                同时改指令的下一条指令也是新的基本块的开始指令 
                """
                
                new_block = True
                labelFlag = 0

            elif isinstance(inst, instruction.JumpInst):
                """ 
                当前指令是无条件跳转指令，跳转的目的指令是一个新基本块的开始指令，
                而下一个指令不一定是新基本块的开始指令
                """
                block = None
                labelFlag = 0
            
        else:
            """ 不是第一条指令 """
            if isinstance(inst, instruction.LabelInst):
                """ 
                当前指令是Label指令，
                若前面的指令不是Label指令，则很大可能(但不是一定)本Lable指令是新基本块的开始，可新创建一个基本块；
                若前面的指令是Label指令，只需要在Label一览中记录即可
                """
                if labelFlag == 0:
                    new_block = True
                
                labelFlag = 1
                
                new_inst = False
                continue
            elif isinstance(inst, instruction.CJumpInst):
                """ 
                当前指令是有条件跳转指令
                """
                new_block = True
                labelFlag = 1

            elif isinstance(inst, instruction.JumpInst) or isinstance(inst, instruction.RetureInst):
                """
                当前指令是无条件跳转指令，下一条指令可能不是新基本块的开始 
                """
                
                # print "gotoLabel", inst.gotoLabel
                block = None
                labelFlag = 0
        
        # end if i==0
        
        if new_inst and block is not None:
            """add the inst to current block, unless the block is not none"""
            block.add(inst)
            labelFlag = 0
                    
        if new_block:
            ''' 如果需要新追加一个基本块，则分配一个 '''
            
            block = BasicBlock.BasicBlock(number)
            blockList.append(block)
            blockDict[number] = block
            
            if labelFlag:
                labelDict[inst.labelname] = number
                
            number += 1

            
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

    return blockList










