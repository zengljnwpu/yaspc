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

import yaspc.Instruction.instruction as instruction


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
    inst_dict = one_inst.__dict__.copy()
    # remember remove items which shouldn't be in IR
    inst_dict.pop('pos', False)
    return inst_dict

def generate_labellist(inst_list):
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

def encode_labellist(labellist):
    '''encode function labellist
    and return labellist(json format)
    '''
    label_list_json = []
    for label in labellist:
        label_list_json.append(label.__dict__)
    return label_list_json


