#!/bin/env python

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

def encode_body():
    '''encode function body
    and return labels
    '''
    pass

def test_module():
    '''
    run a example of IR and print instructions list
    now is only support main function
    '''
    with open('dsq.ir.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    #print(ir_str)
    #print(ir_json)
    #print(json.dumps(ir_json, sort_keys=True, indent=4))
    #print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    inst_list = decode_body(ir_json['functionlist'][0]['body'])
    print('function 0 body parse successfully.\n')
    for inst in inst_list:
        print(inst.line_number, "\t", inst)

if __name__ == '__main__':
    test_module()
