#/bin/env python

# Author : axiqia, lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/12
'''
read input.txt and print basicblock.json
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import re
import json
import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock
import yaspc.BasicBlock.ConstructBasicBlock as ConstructBasicBlock
import yaspc.IR_IO.irParser as irParser
import yaspc.BasicBlock.ud as ud
import yaspc.BasicBlock.PeepholeOptimization as PeepholeOptimization


def main():
    '''
    run a example of parser Three-address code and generate Basicblock list
    '''
    with open('udtest.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    # print(ir_str)
    # print(ir_json)
    # print(json.dumps(ir_json, sort_keys=True, indent=4))
    # print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    inst_list = irParser.decode_body(ir_json['functionlist'][0]['body'])
    print('function 0 body parse successfully.\n')
    for ith, inst in enumerate(inst_list):
        #inst.pos = ith
        inst.ud = set()
        print(inst.pos, inst)
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    inst_list = PeepholeOptimization.control_flow_optimization(block_list, inst_list)
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    #var_reduce = ud.reach_def_iteration(block_list)
    #ud.ud_set(block_list, var_reduce)
    #ud.constant_propagation(block_list, var_reduce, inst_list)
    ud.live_variable_analysis(block_list)

if __name__ == '__main__':
    main()
