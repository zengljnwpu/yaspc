# -*- coding: utf-8 -*-

"""
Created on Fri May 12 10:54:38 2017

@author: hellolzc axiqia
"""

from optimization import instruction

class BasicBlock(object):
    """
    Basic block class
    这个类几乎没有封装，当成结构体用了。。。
    """
    # 设计的很糟糕，建议专门设计一个图的数据结构来存block
    def __init__(self, number=0):
        ''' 前序基本块集合
        集合中保存的是BasicBlock对象
        '''
        self.preBasicBlock = set()

        ''' 后继基本块集合
        集合中保存的是元组(BasicBlock对象, 描述字符串<"thenlabel"/"elselabel"/"label"/"return"/ "follow">)
        '''
        self.succBasicBlock = set()

        ''' 基本块号 '''
        self.blockNum = number

        ''' 基本块所包含的指令一览 '''
        self.instList = []

        ''' 变量一览 '''
        self.var_list = set()

    def add_succ(self, element):
        ''' 为基本块增加后继
        element 是 (BasicBlock对象, 描述字符串<"thenlabel"/"elselabel"/"label"/"follow"/"return">)
        '''
        self.succBasicBlock.add(element)

    def add_prev(self, element):
        ''' 为基本块增加前序
        element 是 BasicBlock对象
        '''
        self.preBasicBlock.add(element)

    def add_inst(self, inst):
        ''' 为基本块增加指令 '''
        self.instList.append(inst)

    def get_inst_number(self):
        """ return the amount of instructions"""
        return len(self.instList)

    def get_first_inst(self):
        """ return first instruction """
        if len(self.instList) >= 1:
            return self.instList[0]

        return None

    def get_last_inst(self):
        """return last instruction"""

        if len(self.instList) >= 1:
            return self.instList[-1]

        return None

    def gen_block_label_inst(self):
        """generate block labelInst from blockNum"""

        label_name = self.gen_block_label_string()
        if len(self.instList) >= 1:
            line_number = self.get_first_inst().line_number
        else:
            line_number = 0
        block_label_inst = instruction.LabelInst('label_definition', line_number=line_number,
                                                 labelname=label_name)
        return block_label_inst

    def gen_block_label_string(self):
        """generate block label string from blockNum"""

        if self.blockNum == -1:
            label_name = 'LabelBlockExit'
        else:
            label_name = 'LabelBlock%d' % self.blockNum
        return label_name

    def set_succ_block_by_str(self, discription, block):
        """根据描述找到对应的后继基本块，并用block替换
        描述字符串包括"thenlabel"/"elselabel"/"label"/"follow"/"return"
        """
        for succ_block in self.succBasicBlock:
            if succ_block[1] == discription:
                succ_block = block

    def get_succ_block_by_str(self, discription):
        """根据描述找到对应的后继基本块，并用返回它
        描述字符串包括"thenlabel"/"elselabel"/"label"/"follow"/"return"
        """
        for succ_block in self.succBasicBlock:
            if succ_block[1] == discription:
                return succ_block[0]

    def set_succ_then_block(self, block):
        """如果最后一条指令是条件跳转，找到then对应的后继基本块，并用block替换
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            self.set_succ_block_by_str('thenlabel', block)

    def get_succ_then_block(self):
        """如果最后一条指令是条件跳转，返回then对应的基本块
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            for succ_block in self.succBasicBlock:
                if succ_block[1] == 'thenlabel':
                    return succ_block[0]

        return None

    def set_succ_else_block(self, block):
        """如果最后一条指令是条件跳转，找到else对应的后继基本块，并用block替换
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            self.set_succ_block_by_str('elselabel', block)

    def get_succ_else_block(self):
        """if last instruction is cjump,
            return else block
            else return None
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            for succ_block in self.succBasicBlock:
                if succ_block[1] == 'elselabel':
                    return succ_block[0]

        return None

    def set_succ_unique_block(self, block):
        """如果只有一个后继，找到对应的后继基本块，并用block替换
        """
        if len(self.succBasicBlock) == 1:
            unique_succ = tuple(self.succBasicBlock)[0]
            unique_succ[0] = block

    def get_succ_unique_block(self):
        """if there is only one succBlock
            return the unique block
            else return None
        """
        if len(self.succBasicBlock) == 1:
            unique_succ_block = tuple(self.succBasicBlock)[0][0]
            return unique_succ_block

        return None

