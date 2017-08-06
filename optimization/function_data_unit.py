# -*- coding: utf-8 -*-

"""
Created : 2017/8/6
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy

from optimization import instruction
from optimization import basicblock

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class FunctionDataUnit(object):
    """
    FunctionDataUnit class
    """
    def __init__(self):
        self.blockList = None
        self.instList = None
        self.var_reduce = None
        self.labelList = None

    def __SplitBasicBlock(self, inst_list, blockDict, labelDict, blockList):
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
        block = basicblock.BasicBlock(block_number)
        blockList.append(block)
        block = None

        for inst in inst_list:
            """ block是None，预示着一个新基本块的开始 """
            if block is None:
                block_number = block_number + 1
                block = basicblock.BasicBlock(block_number)

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
                    block = basicblock.BasicBlock(block_number)

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
        block = basicblock.BasicBlock(-1)
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


    def __LinkBasicBlock(self, inst_list, blockDict, labelDict, blockList):
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


    def ConstructBlockList(self):
        """Construct basic block list
        Remove the unused label,
        split the basic block and
        link the succeed basic block and precursor basic block
        """

        blockDict = {}      # key is the number of block, and map to block object
        labelDict = {}      # key is the label of instruction, and map to block object
        blockList = []

        if self.instList is None:
            print("Error: instList is None.")
            return

        self.__SplitBasicBlock(self.instList, blockDict, labelDict, blockList)
        self.__LinkBasicBlock(self.instList, blockDict, labelDict, blockList)

        self.blockList = blockList
        self.instList = None


    def __BlockList_to_InstList(self, block_list):
        """deconstruct basicblock
        """
        inst_list = []

        for curblock in block_list:
            # ENTRY BLOCK
            if curblock.blockNum == 0:
                continue
            
            # 先给所有block入口加label，之后可以在窥孔优化中删除
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

        # pos需要重新编号，以便于之后生成labellist
        for ith, inst in enumerate(inst_list):
                inst.pos = ith + 1
        if DEBUG:
            print ("============LinearInstructionList==================")
            for inst in inst_list:
                print('%3d\t%s'%(inst.pos, str(inst)))
        return inst_list

    def __generate_labellist(self, inst_list):
        """遍历instruction list获得labellist
        格式举例：
        "labellist": [{ "object": "label",  "name": "forstartlabel1",  "pos": 2 }, ...]
        """
        labellist = []
        for inst in inst_list:
            if isinstance(inst, instruction.LabelInst):
                name = inst.labelname
                pos = inst.pos
                labellist.append({"object": "label", "name": name, "pos": pos})
        return labellist

    def DestructBlockList(self):
        """Destruct basic block list
        """

        if self.blockList is None:
            print("Error: blockList is None.")
            return

        self.instList = self.__BlockList_to_InstList(self.blockList)
        self.labelList = self.__generate_labellist(self.instList)

        self.blockList = None


    def show_instructions(self):
        if self.instList is None:
            print("Error: instList is None.")
            return
        for ith, inst in enumerate(self.instList):
            ith
            print(inst.pos, inst)

    def show_basic_blocks(self):
        if self.blockList is None:
            print("Error: blockList is None.")
            return

        for block in self.blockList:
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
