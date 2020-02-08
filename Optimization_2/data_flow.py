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
        if DEBUG:
            function_optimizer.set_debug_print(True)
        self.analysis_reach_definition()
        function_optimizer.set_debug_print(False)
        block_list = self.data_unit.get_block_list()
        self.__constant_propagation(block_list)

    def __constant_propagation(self, block_list):
        """Do the constant value propagation
        # TODO: 定值传播处理的指令类型，需要加
        # 定值传播需要迭代进行，才能传播充分

        :type block_list: list
        :param block_list: a basic block list
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
                        if len(left_ud) == 1:
                            left_def_inst = self.data_unit.get_inst_by_pos(left_ud[0])
                            if isinstance(left_def_inst, instruction.StoreInst):
                                inst.left = left_def_inst.value
                        if len(right_ud) == 1:
                            right_def_inst = self.data_unit.get_inst_by_pos(right_ud[0])
                            if isinstance(right_def_inst, instruction.StoreInst):
                                inst.right = right_def_inst.value
                    elif isinstance(inst, instruction.UnaryInst):
                        var_ud = inst.var_ud
                        var_def_inst = self.data_unit.get_inst_by_pos(var_ud[0])
                        if len(var_ud) == 1 and isinstance(var_def_inst, instruction.StoreInst):
                            inst.left = var_def_inst.value

