#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:54:38 2017

@author: hellolzc axiqia
"""

import yaspc.Optimization.Instruction.instruction as instruction

class BasicBlock:
    def __init__(self, number=0):
        self.preBasicBlock = set()
        self.succBasicBlock = set()
        self.blockNum = number
        self.instList = []
        self.var_list = set()

    def get_first_inst(self):
        """return first instruction"""
        if len(self.instList) >= 1:
            return self.instList[0]
        else:
            return None

    def get_last_inst(self):
        """return last instruction"""
        if len(self.instList) >= 1:
            return self.instList[-1]
        else:
            return None

    def gen_block_label_inst(self):
        '''generate block labelInst from blockNum'''
        label_name = self.gen_block_label_string()
        if len(self.instList) >= 1:
            line_number = self.get_first_inst().line_number
        else:
            line_number = 0
        block_label_inst = instruction.LabelInst('label_definition', line_number=line_number,
                                                 labelname=label_name)
        return block_label_inst

    def gen_block_label_string(self):
        '''generate block label string from blockNum'''
        if self.blockNum == -1:
            label_name = 'LabelBlockExit'
        else:
            label_name = 'LabelBlock%d'%self.blockNum
        return label_name

    def get_succ_then_block(self):
        """if last instruction is cjump,
            return then block
            else return None
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            for succ_block in self.succBasicBlock:
                if succ_block[1]=='thenlabel':
                    return succ_block[0]
        else:
            return None

    def get_succ_else_block(self):
        """if last instruction is cjump,
            return else block
            else return None
        """
        if isinstance(self.get_last_inst(), instruction.CJumpInst):
            for succ_block in self.succBasicBlock:
                if succ_block[1] == 'elselabel':
                    return succ_block[0]
        else:
            return None

    def get_succ_unique_block(self):
        """if there is only one succBlock
            return the unique block
            else return None
        """
        if len(self.succBasicBlock) == 1:
            # there is a little danteng
            unique_succ_block = [item for item in self.succBasicBlock][0][0]
            return unique_succ_block
        else:
            return None

