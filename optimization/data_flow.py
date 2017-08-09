# -*- coding: utf-8 -*-

"""
Created : 2017/8/7
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from optimization import instruction
from optimization import function_optimizer

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class DataFlowOptimizer(function_optimizer.FunctionOptimizer):
    """DataFlowOptimizer class
    """
    def __init__(self):
        super(DataFlowOptimizer, self).__init__()

    def do_constant_propagation(self):
        """Do the constant value propagation
        """
        self.analysis_reach_definition()
        block_list = self.data_unit.blockList
        var_reduce = self.data_unit.var_reduce
        inst_list = self.data_unit.instList
        self.__constant_propagation(block_list, var_reduce, inst_list)

    def __constant_propagation(self, block_list, var_reduce, inst_list):
        """Do the constant value propagation

        :type block_list: list
        :param block_list: a basic block list

        :type var_reduce: dict
        :param var_reduce: which key is left variable and
                            value is a set where the variable is defined in each block

        :type inst_list: list
        :param inst_list: a list of instructions

        """

        change = True
        while change:
            change = False
            for block in block_list:
                for inst in block.instList:
                    """ there is a unique definition of each operand V
                        that reaches current instruction,
                        and definition is the form store c to V for a constant c,
                        then we can replace V with c
                    """
                    if isinstance(inst, instruction.BinaryInst):
                        left_ud = inst.left_ud
                        right_ud = inst.right_ud
                        if len(left_ud) == 1 and isinstance(inst_list[left_ud[0]], instruction.StoreInst):
                            inst.left = self.__new_entity_value("value", inst_list[left_ud[0]].value.value)
                        if len(right_ud) == 1 and isinstance(inst_list[right_ud[0]], instruction.StoreInst):
                            inst.right = self.__new_entity_value("value", inst_list[right_ud[0]].value.value)
                    elif isinstance(inst, instruction.UnaryInst):
                        var_ud = inst.var_ud
                        if len(var_ud) == 1 and isinstance(inst_list[var_ud[0]], instruction.StoreInst):
                            inst.left = self.__new_entity_value("value", inst_list[var_ud[0]].value.value)

        if(DEBUG):
            print("==============constant_propagation===============")
            for inst in inst_list:
                print(inst)
