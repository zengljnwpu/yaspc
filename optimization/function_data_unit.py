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
        # protected:
        # 基本块列表
        # block_list 和 _inst_list 当一个存在的时候，另一个必须为None
        self._block_list = None
        # 指令列表
        self._inst_list = None
        # 变量信息字典
        # key: variable name
        # value: var_type
        #        is_private : True/False
        #        const : True/False
        #        line_number
        #        initvalue
        #        var_reduce
        self._var_table = dict()

    def set_inst_list(self, inst_list):
        """重置指令列表，并清空基本块列表
        """
        self._inst_list = inst_list
        self._block_list = None

    def get_inst_list(self):
        """返回指令列表，指令列表为None时返回None
        """
        if self._inst_list is None:
            print("Error: instList is None.")
            return None
        return self._inst_list

    def set_block_list(self, block_list):
        """重置基本块列表，并清空指令列表
        """
        self._block_list = block_list
        self._inst_list = None

    def get_block_list(self):
        """返回基本块列表，基本块列表为None时返回None
        """
        if self._block_list is None:
            print("Error: blockList is None.")
            return None
        return self._block_list

    def get_inst_by_pos(self, pos):
        """根据pos信息查找指令，
        注意，如果指令被重新编号，之前计算出的pos即失效
        """
        if self._inst_list is not None:
            for inst in self._inst_list:
                if inst.pos == pos:
                    return inst
        if self._block_list is not None:
            for block in self._block_list:
                for inst in block.instList:
                    if inst.pos == pos:
                        return inst

    def set_var_table(self, var_table):
        self._var_table = var_table

    def get_var_table(self):
        return self._var_table

    def add_var_info(self, var_name, var_info_dict):
        """为变量信息表添加信息
        """
        if var_name not in self._var_table:
            self._var_table[var_name] = dict()

        for key in var_info_dict:
            if key == "var_type":
                self._var_table[var_name][key] = var_info_dict[key]
            elif key == "is_private":
                self._var_table[var_name][key] = var_info_dict[key]
            elif key == "const":
                self._var_table[var_name][key] = var_info_dict[key]
            elif key == "line_number":
                self._var_table[var_name][key] = var_info_dict[key]
            elif key == "initvalue":
                self._var_table[var_name][key] = var_info_dict[key]
            elif key == "var_reduce":
                self._var_table[var_name][key] = var_info_dict[key]

    def get_var_info(self, var_name, property_name):
        """从变量信息表得到指定变量信息
        """
        if var_name in self._var_table:
            return self._var_table[var_name][property_name]

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

        # print("===================BasicBlock==================")
        # for block in blockList:
        #     print(block.blockNum, ":")
        #     for inst in block.instList:
        #         print("\t", inst.pos, inst)
        # print("===================LabelDict===================")
        # for key, val in labelDict.items():
        #     print(key, val)
        # print("===============================================")


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

        # print("============PredecessorSuccessor==================")
        # for ith, inst in enumerate(inst_list):
        #     ith
        #     print(inst.pos, inst)
        # for block in blockList:
        #     print(block.blockNum, ":")
        #     for inst in block.instList:
        #         print("\t", inst)
        #     if len(block.succBasicBlock) != 0:
        #         for succblock in block.succBasicBlock:
        #             print("succblock: %d:%s" % (succblock[0].blockNum, str(succblock[1])))
        #     if len(block.preBasicBlock) != 0:
        #         for preblock in block.preBasicBlock:
        #             print("preblock", preblock.blockNum)


    def ConstructBlockList(self):
        """Construct basic block list
        Remove the unused label,
        split the basic block and
        link the succeed basic block and precursor basic block
        """

        blockDict = {}      # key is the number of block, and map to block object
        labelDict = {}      # key is the label of instruction, and map to block object
        blockList = []

        if self._inst_list is None:
            print("Error: instList is None.")
            return

        self.__SplitBasicBlock(self._inst_list, blockDict, labelDict, blockList)
        self.__LinkBasicBlock(self._inst_list, blockDict, labelDict, blockList)

        self._block_list = blockList
        self._inst_list = None

        if DEBUG:
            print("@ FunctionDataUnit:ConstructBlockList()")
            self.show_basic_blocks()


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
        # if DEBUG:
        #     print ("============LinearInstructionList==================")
        #     for inst in inst_list:
        #         print('%3d\t%s'%(inst.pos, str(inst)))
        return inst_list


    def DestructBlockList(self):
        """Destruct basic block list
        """

        if self._block_list is None:
            print("Error: blockList is None.")
            return

        self._inst_list = self.__BlockList_to_InstList(self._block_list)
        self._block_list = None

        if DEBUG:
            print("@ FunctionDataUnit:DestructBlockList()")
            self.show_instructions()


    def show_instructions(self):
        """显示指令列表
        """
        if self._inst_list is None:
            print("Error: instList is None.")
            return
        print("    +===================== Instruction List =============================+")
        for inst in self._inst_list:
            disp_str = '%3d    %s' % (inst.pos, str(inst))
            print('    | %-67s|'%disp_str)
        print("    +====================================================================+")

    def show_basic_blocks(self):
        """显示基本块列表
        """
        if self._block_list is None:
            print("Error: blockList is None.")
            return

        print("    +======================= BasicBlock List ============================+")
        for block in self._block_list:
            print("    + B%-3d --------------------------------------------------------------+"%block.blockNum)

            # 显示当前块的前序基本块
            for preblock in block.preBasicBlock:
                print("    | preblock: %-56s |" % str(preblock.blockNum))
            #print("|-------------------------------------------------------------------|")

            # 显示该块的所有指令
            for inst in block.instList:
                disp_str = "%3d  %s"%(inst.pos, str(inst))
                print("    |        %-60s|"%disp_str)
            #print("|-------------------------------------------------------------------|")

            # 显示当前块的后继基本块
            for succblock in block.succBasicBlock:
                disp_str = "%d:%s" % (succblock[0].blockNum, str(succblock[1]))
                print("    | succblock: %-55s |"%disp_str)

            if block.blockNum == -1:
                print("    +====================================================================+")
            else:
                print("    +--------------------------------------------------------------------+")



    def instlist_renumbering(self):
        '''给指令列表中的指令pos重新编号
        '''
        if self._inst_list is None:
            print("Error: instList is None.")
            return
        for ith, inst in enumerate(self._inst_list):
            inst.pos = ith + 1
