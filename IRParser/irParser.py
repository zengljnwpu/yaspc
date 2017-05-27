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
    TODO: need support for more instruction
    '''
    if inst_dict['name'] == 'variable_definition':
        return instruction.AllocaInst(**inst_dict)
    elif inst_dict['name'] == 'cjump':
        return instruction.CJumpInst(**inst_dict)
    elif inst_dict['name'] == 'jump':
        return instruction.JumpInst(**inst_dict)
    elif inst_dict['name'] == 'bin':
        return instruction.BinaryInst(**inst_dict)
    elif inst_dict['name'] == 'uni':
        return instruction.UnaryInst(**inst_dict)
    elif inst_dict['name'] == 'load':
        return instruction.LoadInst(**inst_dict)
    elif inst_dict['name'] == 'store':
        return instruction.StoreInst(**inst_dict)
    elif inst_dict['name'] == 'call':
        return instruction.CallInst(**inst_dict)
    elif inst_dict['name'] == 'return':
        return instruction.RetureInst(**inst_dict)
    elif inst_dict['name'] == 'label_definition':
        return instruction.LabelInst(**inst_dict)
    else:
        print('unkown instruction: %s'%inst_dict['name'])


def test_module():
    '''
    run a example of IR and print instructions list
    now is only support main function
    '''
    inst_list = []
    with open('dsq.ir.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    #print(ir_str)
    #print(ir_json)
    #print(json.dumps(ir_json, sort_keys=True, indent=4))
    #print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    for inst_dict in ir_json['functionlist'][0]['body']:
        inst_dict.pop('object')
        inst_list.append(parse_single_inst_from_json(inst_dict))
    print('function 0 body parse successfully.\n')
    for inst in inst_list:
        print(inst)

if __name__ == '__main__':
    test_module()
