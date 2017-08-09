# -*- coding: utf-8 -*-

"""
Created : 2017/8/8
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import re
import json

from optimization import instruction
from optimization import function_data_unit
from optimization import function_optimizer
from optimization import data_flow
from optimization import peephole

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class FunctionOptimizationManager(object):
    """以函数为一个单位管理优化
    """
    def __init__(self):
        # 存储优化用到的数据
        self.__data_unit = function_data_unit.FunctionDataUnit()
        # 存储function的完整的json格式的IR
        self.__function_json = dict()
        self.__data_flow_opt = data_flow.DataFlowOptimizer()
        self.__control_flow_opt = peephole.ControlFlowOptimizer()
        # TODO: add loop_opt

    def optimize(self, control_flow, reach_defination, optimize_loop):
        """optimize a function
        """
        if DEBUG:
            self.__data_unit.show_instructions()

        # 初始化优化器
        self.__data_flow_opt.data_unit = self.__data_unit
        self.__control_flow_opt.data_unit = self.__data_unit

        # 划分基本块
        if DEBUG:
            print('optimization:', '\nConstrusting basicblock...')
        self.__data_unit.ConstructBlockList()

        # 消除到达不了的代码，否则后面分析循环会出错
        self.__control_flow_opt.dead_code_elimination()

        # 若控制流指定时，则进行控制流优化
        if control_flow:
            if DEBUG:
                print('optimization', '\nOptimizing control flow...')
            #self.__control_flow_opt.control_flow_optimization()

        # 若数据流指定时，则进行数据流优化
        if reach_defination:
            if DEBUG:
                print('optimization', '\nAnalyzing reach defination...')
            self.__data_flow_opt.do_constant_propagation()

        # 若指定循环优化，则进行循环优化
        if optimize_loop:
            if DEBUG:
                print('optimization', '\nAnalyzing loop...')
            # TODO: complete it

        # 基本块转换为指令序列
        self.__data_unit.DestructBlockList()
        # 转换过程中可能生成无用label，故删去
        self.__control_flow_opt.remove_unused_label()


#######################################
# JSON style IR Format:
#     see IR.md
#######################################
    def decode_function_json(self, function_json):
        '''decode function, JSON style
        '''
        self.__function_json = function_json
        input_body_json = function_json['body']
        input_variablelist_json = function_json['variablelist']
        inst_list = self.__decode_variablelist(input_variablelist_json) + \
            self.__decode_function_body_json(input_body_json)

        self.__data_unit.set_inst_list(inst_list)
        self.__data_unit.instlist_renumbering()
        

    def encode_function_json(self):
        '''encode function, JSON style
        '''
        inst_list = self.__data_unit.get_inst_list()
        body_json = self.__encode_function_body_json(inst_list)
        labellist_json = self.__generate_labellist_json(inst_list)

        if DEBUG:
            print('optimization:', "============LinearInstructionList==================")
            self.__data_unit.show_instructions()
            print('optimization:', "=================LabelList=========================")
            print('optimization:', json.dumps(labellist_json, sort_keys=True, indent=2))

        self.__function_json['body'] = body_json
        self.__function_json['labellist'] = labellist_json
        return self.__function_json


    @classmethod
    def __decode_variablelist(cls, variablelist):
        '''decode function variablelist,
        generate store instructions,
        return instruction list
        '''
        inst_list = []
        for ith, var_dict in enumerate(variablelist):
            var_name = var_dict["variablename"]
            initvalue = var_dict["initvalue"]
            line_number = var_dict["line_number"]
            const = var_dict["const"]
            var_type = var_dict["var_type"]
            is_private = var_dict["is_private"]

            address = instruction.Variable("variable", var_type, var_name, is_private, const)
            value = instruction.Value("value", var_type, initvalue)

            inst = instruction.StoreInst('store', line_number=line_number, address=address, value=value)
            inst.pos = ith + 1
            inst_list.append(inst)
        return inst_list

    @classmethod
    def __generate_labellist_json(cls, inst_list):
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

    @classmethod
    def __decode_function_body_json(cls, body_list):
        '''decode function body,
        return instruction list
        '''
        inst_list = []
        for ith, inst_dict in enumerate(body_list):
            inst = cls.__parse_single_inst_from_json(inst_dict)
            inst.pos = ith + 1
            inst_list.append(inst)
        return inst_list

    @classmethod
    def __encode_function_body_json(cls, inst_list):
        '''encode function body
        and return body_list(json format)
        '''
        body_list = []
        for inst in inst_list:
            body_list.append(cls.__encode_single_inst_from_json(inst))
        return body_list

    @classmethod
    def __parse_single_inst_from_json(cls, inst_dict):
        '''
        Read a instruction dict (json format) and generate a Instruction Object
        '''
        inst_dict_cp = inst_dict.copy()
        assert inst_dict_cp['object'] == 'instruction', 'object error!'
        inst_dict_cp.pop('object', False)
        if inst_dict_cp['name'] == 'variable_definition':
            return instruction.AllocaInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'cjump':
            return instruction.CJumpInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'jump':
            return instruction.JumpInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'bin':
            return instruction.BinaryInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'uni':
            return instruction.UnaryInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'load':
            return instruction.LoadInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'store':
            return instruction.StoreInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'call':
            return instruction.CallInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'return':
            return instruction.RetureInst(**inst_dict_cp)
        elif inst_dict_cp['name'] == 'label_definition':
            return instruction.LabelInst(**inst_dict_cp)
        else:
            print('unkown instruction: %s'%inst_dict_cp['name'])

    @classmethod
    def __encode_single_inst_from_json(cls, one_inst):
        '''
        Read a Instruction Object and generate a instruction dict (json format)
        '''
        return one_inst.to_dict()


#######################################
# TAC IR Format:
#     see IR_TAC.md
#######################################
    def decode_function_tac(self, function_tac):
        """decode function, TAC format
        """
        inst_list = self.__decode_tac_list(function_tac[1:])
        self.__data_unit.set_inst_list(inst_list)

    @classmethod
    def __decode_tac_list(cls, tac_list):
        '''decode function body, Three adress format,
        return instruction list
        '''
        inst_list = []
        for ith, inst_dict in enumerate(tac_list):
            inst = cls.__parse_single_inst_from_tac(inst_dict)
            if inst is None:
                continue
            inst.pos = ith + 1
            inst_list.append(inst)
        return inst_list


    @classmethod
    def __parse_single_inst_from_tac(cls, inst_string):
        '''
        Read a instruction and generate a Instruction Object
        Return None if wrong
        Attention: value entity is processed as integer
        '''
        # AllocaInst Format:  variable_definition   variablename var_type
        split = re.split(r'\s+', inst_string)
        if split[0] == 'variable_definition':
            return instruction.AllocaInst(split[0], variablename=split[1], var_type="int32")

        # CJumpInst Format:  cjump   cond thenlabel elselabel
        elif split[0] == 'cjump':
            cond = cls.__get_entity_from_str(split[1])
            if cond is None:
                print('wrong cjump instruction: %s'%inst_string)
                return None
            return instruction.CJumpInst(split[0], cond=cond, thenlabel=split[2], elselabel=split[3])

        # JumpInst Format:  jump    label
        elif split[0] == 'jump':
            return instruction.JumpInst(split[0], label=split[1])

        # BinaryInst Format:  bin     op left right value
        elif split[0] == 'bin':
            left = cls.__get_entity_from_str(split[2])
            right = cls.__get_entity_from_str(split[3])
            value = cls.__get_entity_from_str(split[4])
            if left is None or right is None or value is None:
                print('wrong bin instruction: %s'%inst_string)
                return None
            return instruction.BinaryInst(split[0], op=split[1], left=left, right=right, value=value)

        # UnaryInst Format:  uni     op variable value
        elif split[0] == 'uni':
            variable = cls.__get_entity_from_str(split[2])
            value = cls.__get_entity_from_str(split[3])
            print(variable)
            print(value)
            if variable is None or value is None:
                print('wrong uni instruction: %s'%inst_string)
                return None
            return instruction.UnaryInst(split[0], op=split[1], variable=variable, value=value)

        # LoadInst Format:  load    adress value
        elif split[0] == 'load':
            address = cls.__get_entity_from_str(split[1])
            value = cls.__get_entity_from_str(split[2])
            if address is None or value is None:
                print('wrong load instruction: %s'%inst_string)
                return None
            return instruction.LoadInst(split[0], address=address, value=value)

        # StoreInst Format:  store   adress value
        elif split[0] == 'store':
            address = cls.__get_entity_from_str(split[1])
            value = cls.__get_entity_from_str(split[2])
            if address is None or value is None:
                print('wrong load instruction: %s'%inst_string)
                return None
            return instruction.StoreInst(split[0], address=address, value=value)

        # CallInst Format:  call    functionname parameterlist value
        elif split[0] == 'call':
            # TODO: parameterlist is not support now
            value = cls.__get_entity_from_str(split[3])
            if value is None:
                print('wrong call instruction: %s'%inst_string)
                return None
            return instruction.CallInst(split[0], functionname=split[1], parameterlist=split[2], value=value)

        # RetureInst Format:  return  ret
        elif split[0] == 'return':
            ret = cls.__get_entity_from_str(split[1])
            if ret is None:
                print('wrong ret instruction: %s'%inst_string)
                return None
            return instruction.RetureInst(split[0], ret=ret)

        # LabelInst Format:  label_definition      labelname
        elif split[0] == 'label_definition':
            return instruction.LabelInst(split[0], labelname=split[1])

        else:
            print('unkown instruction: %s'%inst_string)
            return None

    @classmethod
    def __get_entity_from_str(cls, entity_str):
        """Entity:
        Attention: entity is processed as "int32"
            var(variable) : int
            val(value)    : integer
        e.g.
            var:i
            val:1
        """
        var_entity_dict = {"object": "variable", "type": "int32", "name": "%0"}
        val_entity_dict = {"object": "value", "type": "int32", "value": 0}
        if entity_str.find(':') == -1:
            print('wrong entity format: %s'%entity_str)
            return None
        if entity_str[0:3] == 'var':
            var_entity_dict['name'] = entity_str[4:]
            return instruction.Variable(**var_entity_dict)
        elif entity_str[0:3] == 'val':
            val_entity_dict['value'] = int(entity_str[4:])
            return instruction.Value(**val_entity_dict)
        else:
            print('wrong entity format: %s'%entity_str)
            return None