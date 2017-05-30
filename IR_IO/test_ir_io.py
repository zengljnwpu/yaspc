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
import yaspc.BasicBlock.ConstructBasicBlock as ConstructBasicBlock
import yaspc.BasicBlock.DestructBasicBlock as DestructBasicBlock
import yaspc.IR_IO.irParser as irParser

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
    #print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    inst_list = irParser.decode_body(ir_json['functionlist'][0]['body'])
    print('function 0 body parse successfully.\n')
    for inst in inst_list:
        print('%3d\t%s'%(inst.pos, str(inst)))

    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    #ud.ud_set(block_list, var_reduce)
    #ud.constant_propagation(block_list, var_reduce, inst_list)
    #ud.live_variable_analysis(block_list)
    inst_list = DestructBasicBlock.BlockList_to_InstList(block_list)
    new_labellist = DestructBasicBlock.generate_labellist(inst_list)
    print(json.dumps(new_labellist, sort_keys=True, indent=4))

if __name__ == '__main__':
    test_module()
