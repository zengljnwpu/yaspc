#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Date: 2017/6/30
Author: hellolzc axiqia

VariableList:
key: variablename
value: {
      "initvalue": 0(0),
      "line_number": 2(-1),
      "const": false(false),
      "var_type": "integer*"(None),
      X                           "object": "instruction",
      X                          "variablename": "n",
      X                           "name": "variable_definition",
      X                           "number": 1,
      "is_private": false(false)
      "var_reduce": [a list of pos where the variable is defined(killed)]
      "used" :  [a list of pos where the variable is used]
    }

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

class Variable(object):
    def __init__(self, var_name, var_type, is_const, is_private, init_val = None, line_num = None):
        self.name = var_name
        self.type = var_type
        self.is_const = is_const
        self.is_private = is_private
        self.init_val = init_val
        self.line_num = line_num
    
        
class VariableList(object):
    """
    变量列表
    """
    def __init__(self):
        self.dict = dict()

    def update_according_to_varlist(self, varlist):
        """
        varlist : function or program variable list
        """
        for item in varlist:
            var_name = item["variablename"]
            initvalue = item["initvalue"]
            line_number = item["line_number"]
            const = item["const"]
            var_type = item["var_type"]
            is_private = item["is_private"]
            self.add_a_item(var_name, initvalue, line_number, const, var_type, is_private)

    def add_a_item(self, var_name, initvalue, line_number, const, var_type, is_private):
        """add_a_item according_to_varlist
        """
        self.dict[var_name] = {
            "initvalue": initvalue,
            "line_number": line_number,
            "const": const,
            "var_type": var_type,
            "is_private": is_private,
            "var_reduce": [],
            "used" :  []
        }

    def update_according_to_instlist(self, instlist):
        """instlist : function or program body
        """
        pass
        # for inst in instlist:
        #     # BinaryInst
        #     if isinstance(inst, instruction.BinaryInst):
        #         pass
        #     # UnaryInst
        #     elif isinstance(inst, instruction.UnaryInst):
        #         var = inst.variable.name

        #     # StoreInst
        #     elif isinstance(inst, instruction.StoreInst):
        #         var = inst.address.name
        #         block_def_var[var] = inst.pos
        # if self.dict.has_key(var_name):
        #     pass


