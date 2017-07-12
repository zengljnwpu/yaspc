#!/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci) , axiqia
# Created : 2017/5/24

'''
read .json and get instruction lists
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import re
from Optimization.IR_IO import instruction

##################################################################
# TAC IR Format:
# Instruction: Three adress format
#       three-address code (often abbreviated to TAC or 3AC) is an intermediate code used by
#       optimizing compilers to aid in the implementation of code-improving transformations.
#       Each TAC instruction has at most three operands and is typically a combination of
#       assignment and a binary operator.
# No space allowed in any member
# e.g.
#   cjump   cond thenlabel elselabel
#   jump    label
#   label_definition      labelname
#   variable_definition   variablename var_type
#   load    adress value
#   store   adress value
#   bin     op left right value
#   uni     op variable value
#   call    functionname parameterlist value
#   return  ret
###################################################################
def __get_entity_from_str(entity_str):
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

def parse_single_inst_from_TAC(inst_string):
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
        cond = __get_entity_from_str(split[1])
        if cond is None:
            print('wrong cjump instruction: %s'%inst_string)
            return None
        return instruction.CJumpInst(split[0], cond=cond, thenlabel=split[2], elselabel=split[3])

    # JumpInst Format:  jump    label
    elif split[0] == 'jump':
        return instruction.JumpInst(split[0], label=split[1])

    # BinaryInst Format:  bin     op left right value
    elif split[0] == 'bin':
        left = __get_entity_from_str(split[2])
        right = __get_entity_from_str(split[3])
        value = __get_entity_from_str(split[4])
        if left is None or right is None or value is None:
            print('wrong bin instruction: %s'%inst_string)
            return None
        return instruction.BinaryInst(split[0], op=split[1], left=left, right=right, value=value)

    # UnaryInst Format:  uni     op variable value
    elif split[0] == 'uni':
        variable = __get_entity_from_str(split[2])
        value = __get_entity_from_str(split[3])
        print(variable)
        print(value)
        if variable is None or value is None:
            print('wrong uni instruction: %s'%inst_string)
            return None
        return instruction.UnaryInst(split[0], op=split[1], variable=variable, value=value)

    # LoadInst Format:  load    adress value
    elif split[0] == 'load':
        address = __get_entity_from_str(split[1])
        value = __get_entity_from_str(split[2])
        if address is None or value is None:
            print('wrong load instruction: %s'%inst_string)
            return None
        return instruction.LoadInst(split[0], address=address, value=value)

    # StoreInst Format:  store   adress value
    elif split[0] == 'store':
        address = __get_entity_from_str(split[1])
        value = __get_entity_from_str(split[2])
        if address is None or value is None:
            print('wrong load instruction: %s'%inst_string)
            return None
        return instruction.StoreInst(split[0], address=address, value=value)

    # CallInst Format:  call    functionname parameterlist value
    elif split[0] == 'call':
        # TODO: parameterlist is not support now
        value = __get_entity_from_str(split[3])
        if value is None:
            print('wrong call instruction: %s'%inst_string)
            return None
        return instruction.CallInst(split[0], functionname=split[1], parameterlist=split[2], value=value)

    # RetureInst Format:  return  ret
    elif split[0] == 'return':
        ret = __get_entity_from_str(split[1])
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

def decode_TAC_list(tac_list):
    '''decode function body, Three adress format,
    return instruction list
    '''
    inst_list = []
    for ith, inst_dict in enumerate(tac_list):
        inst = parse_single_inst_from_TAC(inst_dict)
        if inst is None:
            continue
        inst.pos = ith + 1
        inst_list.append(inst)
    return inst_list

#################################
# JSON style IR Format:
#     see IR.md
#################################
def parse_single_inst_from_json(inst_dict):
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

def encode_single_inst_from_json(one_inst):
    '''
    Read a Instruction Object and generate a instruction dict (json format)
    '''
    return one_inst.to_dict()

def decode_variablelist(variablelist):
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

def generate_labellist(inst_list):
    """traverse instruction list to generate labellist
    e.g：
    "labellist": [{ "object": "label",  "name": "forstartlabel1",  "pos": 2 }, ...]
    """
    labellist = []
    for inst in inst_list:
        if isinstance(inst, instruction.LabelInst):
            name = inst.labelname
            pos = inst.pos
            labellist.append({"object": "label", "name": name, "pos": pos})
    return labellist

def decode_body(body_list):
    '''decode function body,
    return instruction list
    '''
    inst_list = []
    for ith, inst_dict in enumerate(body_list):
        inst = parse_single_inst_from_json(inst_dict)
        inst.pos = ith + 1
        inst_list.append(inst)
    return inst_list

def encode_body(inst_list):
    '''encode function body
    and return body_list(json format)
    '''
    body_list = []
    for inst in inst_list:
        body_list.append(encode_single_inst_from_json(inst))
    return body_list

def renumbering(inst_list):
    '''numbering for instruction list again
    '''
    for ith, inst in enumerate(inst_list):
        inst.pos = ith + 1
    return inst_list
