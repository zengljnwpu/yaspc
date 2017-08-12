# -*- coding: utf-8 -*-

"""
Created : 2017/8/6
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from optimization import instruction
from optimization import basicblock
from optimization import function_data_unit

DEBUG = False

DEF_INST = (instruction.BinaryInst, instruction.UnaryInst,\
            instruction.StoreInst, instruction.LoadInst)

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class FunctionOptimizer(object):
    """FunctionOptimizer basic class
    """
    def __init__(self):
        self.data_unit = function_data_unit.FunctionDataUnit()

    def analysis_reach_definition(self):
        """分析到达定值
        """
        blockList = self.data_unit.get_block_list()
        var_reduce = self.__reach_def_iteration(blockList)
        for key in var_reduce:
            self.data_unit.add_var_info(key, {"var_reduce":var_reduce[key]})
        self.__ud_set(blockList, var_reduce)

    def __ud_set(self, block_list, var_reduce):
        """Calculates the "use-define" chain of variables in each instruction.

        :type block_list: list
        :param block_list: a basic block list 
        
        :type var_reduce: dict
        :param var_reduce: which key is left variable and 
                            value is a set where the variable is defined in each block
        
        Note: add left_ud, right_ud or var_ud properties which is a set of for every instruction
            var_ud is a list of set (block.in_set & var_reduce before this instruction in this block)
            会给指令增加 left_ud, right_ud 或 var_ud属性，这几个属性都是set类型，记录了到达该指令的定值位置，
            定值位置用inst.pos表示
        """
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list)-1:
                continue
            # block_def_var records the definition of a variable in a block
            block_def_var = dict()
            for inst in block.instList:
                # BinaryInst
                if isinstance(inst, instruction.BinaryInst):
                    """ Regardless of whether the operand is constant or variable,
                        a property right_ud is added to the instruction dynamically
                    """
                    inst.left_ud = []
                    if inst.left.is_variable() is True:
                        left_var = inst.left.name
                        if left_var in block_def_var.keys():
                            def_num = block_def_var[left_var]
                            inst.left_ud = [def_num]
                        else:
                            inst.left_ud = list(block.in_set & var_reduce[left_var])

                    inst.right_ud = []
                    if inst.right.is_variable() is True:
                        right_var = inst.right.name

                        if right_var in block_def_var.keys():
                            def_num = block_def_var[right_var]
                            inst.right_ud = [def_num]
                        else:
                            inst.right_ud = list(block.in_set & var_reduce[right_var])

                    block_def_var[inst.value.name] = inst.pos
                # UnaryInst
                elif isinstance(inst, instruction.UnaryInst):
                    inst.var_ud = []
                    if inst.variable.is_variable() is True:
                        var = inst.variable.name
                        if inst.variable.name in block_def_var.keys():
                            inst.var_ud = (block_def_var[var])
                        else:
                            inst.var_ud = list(block.in_set & var_reduce[left_var])
                    block_def_var[inst.value.name] = inst.pos
                # LoadInst
                elif isinstance(inst, instruction.LoadInst):
                    inst.address_ud = []
                    if inst.address.is_variable() is True:
                        address = inst.address.name
                        if inst.address.name in block_def_var.keys():
                            inst.address_ud = (block_def_var[address])
                        else:
                            if address not in var_reduce:
                                var_reduce[address] = set((-1,))
                            inst.address_ud = list(block.in_set & var_reduce[address])
                    var = inst.value.name
                    block_def_var[var] = inst.pos
                # StoreInst
                elif isinstance(inst, instruction.StoreInst):
                    var = inst.address.name
                    block_def_var[var] = inst.pos

        if DEBUG:
            print("===========UD SET==============")
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                print("B%d:\t" % block.blockNum)
                for inst in block.instList:
                    if isinstance(inst, instruction.BinaryInst):
                        print(inst.pos, ":\t", inst.left_ud, "\t", inst.right_ud)
                    elif isinstance(inst, instruction.LoadInst):
                        print(inst.pos, ":\t", inst.address_ud)
                    elif isinstance(inst, instruction.UnaryInst):
                        print(inst.pos, ":\t", inst.var_ud)
                print()


    def __reach_def_iteration(self, block_list):
        """Calculate reaching-definition of every block, return where the left value was defined
        
        :type: block_list: list
        :param: block_list: a list of basic block
        
        :return: var_reduce: Record where the left value was defined
                key : left value 
                value : a set with positions where the key variable is defined in each block
        Note: add properties of gen_set, kill_set, in_set, out_set for every block.
        """

        # record all left value to a set and map it to the position line
        for (block_index, block) in enumerate(block_list):
            # a dictionary which key is the left value of a instruction
            # and value is position where it's last definition
            block.var_dict = dict()

            # a set of left value of every instruction in a block
            # init gen_set and kill_set for every block
            block.var_set = set()
            for inst in block.instList:
                # only considerate the last gen of the same variable
                if isinstance(inst, DEF_INST):   # BinaryInst UnaryInst StoreInst
                    if isinstance(inst, instruction.StoreInst):
                        block.var_dict[inst.address.name] = inst.pos
                        block.var_set.add(inst.address.name)
                    else:
                        block.var_dict[inst.value.name] = inst.pos
                        block.var_set.add(inst.value.name)
            block.gen_set = set(block.var_dict.values())
            block.kill_set = set()

        # init var_reduce
        var_reduce = dict()
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list)-1:
                continue
            for (key, value) in block.var_dict.items():
                var_reduce[key] = set()

        # calculate var_reduce
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list)-1:
                continue
            for (key, value) in block.var_dict.items():
                var_reduce[key].add(value)
        if DEBUG:
            print("===========variable reduce==============")
            for var, def_set in var_reduce.items():
                print(var, end="\tdefine line:")
                for def_num in def_set:
                    print(def_num, end="\t")
                print()
            print("===========GEN SET of blocks==============")
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                print("B%d:\t" % block.blockNum, end="")
                for gen_num in block.gen_set:
                    print(gen_num, end="\t")
                print()

        # calculate kill set of blocks
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            for var in block.var_set:
                block.kill_set = block.kill_set | var_reduce[var]
            block.kill_set = block.kill_set - block.gen_set

        if DEBUG:
            print("===========KILL SET of blocks==============")
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                print("B%d:\t" % block.blockNum, end="")
                for kill_num in block.kill_set:
                    print(kill_num, end="\t")
                print()

        # calculate in_set and out_set of every block
        for (block_index, block) in enumerate(block_list):
            block.in_set = set()
            block.out_set = block.gen_set

        # start iteration
        # We denote the data-flow values immediately before and immediately after
        # each basic block B by IN [ B ] and OUT [ B ], respectively.
        # The constraints involving IN [ B ] and OUT [ B ] can be derived from
        # those involving IN [ s ]and OUT [ s ] for the various statements s in B as follows.
        #
        # 参考《Compilers Principles, Techniques, and Tools - 2nd Edition - Alfred V. Aho》
        # Figure 9-14 Iterative algorithm to compute reaching denitions
        change = True
        while change:
            change = False
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                new_in = set()
                for pre_block in block.preBasicBlock:
                    new_in = new_in | pre_block.out_set
                if new_in != block.in_set:
                    change = True
                    block.in_set = new_in
                    block.out_set = (block.in_set - block.kill_set) | block.gen_set

        if DEBUG:
            print("===========IN SET of blocks==============")
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                print("B%d:\t" % block.blockNum, end="")
                for in_num in sorted(block.in_set):
                    print(in_num, end="\t")
                print()
            print("===========OUT SET of blocks==============")
            for (block_index, block) in enumerate(block_list):
                if block_index == 0 or block_index == len(block_list) - 1:
                    continue
                print("B%d:\t" % block.blockNum, end="")
                for in_num in sorted(block.out_set):
                    print(in_num, end="\t")
                print()
        return var_reduce


    def __new_entity_value(self, entity_type, value):
        return instruction.Value('value', entity_type, value)


    def analysis_live_variable(self):
        """Do live variable analysis of every basic block

        Note: add live_def_set, live_use_set, live_in_set,
                and live_out_set which type is a set for every block
        """
        block_list = self.data_unit.get_block_list()

        for block in block_list:
            # live_def_set: a set with variable which is defined in the block and not used before the definition
            # live_use_set: a set with variable which is used in the block and not defined before the using
            # live_in_set: a set with variable which is live before the block
            # live_out_set: a set with variable which is live after the block
            block.live_def_set = set()
            block.live_use_set = set()
            block.live_in_set = set()
            block.live_out_set = set()

            # calculate live_def_set and live_use_set of every block
            for inst in block.instList:
                if isinstance(inst, instruction.BinaryInst):
                    """ left operand is a const value,
                        or left operand is a const value which should not consider
                    """
                    if inst.left.is_variable() is True:
                        left_var = inst.left.name
                        if left_var not in block.live_def_set:
                            block.live_use_set.add(left_var)
                    if inst.right.is_variable() is True:
                        right_var = inst.right.name
                        if right_var not in block.live_def_set:
                            block.live_use_set.add(right_var)
                    if inst.value.is_variable() is True:
                        value = inst.value.name
                        if value not in block.live_use_set:
                            block.live_def_set.add(value)

                elif isinstance(inst, instruction.UnaryInst):
                    if inst.variable.is_variable():
                        var = inst.variable.name
                        if var not in block.live_def_set:
                            block.live_use_set.add(var)
                    if inst.value.is_variable():
                        value = inst.value.name
                        if value not in block.live_use_set:
                            block.live_def_set.add(value)
        if DEBUG:
            for block in block_list:
                print(block.blockNum, "def:", block.live_def_set, ";\t", block.live_use_set)

        # calculate live_out_set and live_in_set of every block
        change = True
        while change:
            change = False
            for block in block_list[::-1]:
                for succblock in block.succBasicBlock:
                    block.live_out_set = block.live_out_set | succblock[0].live_in_set
                new_in = (block.live_out_set-block.live_def_set) | block.live_use_set
                if new_in != block.live_in_set:
                    change = True
                    block.live_in_set = new_in

