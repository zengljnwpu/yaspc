#/bin/env python
# -*- coding: utf-8 -*-
# Author : axiqia, lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/12
'''
read input.txt and print basicblock.json
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import json
import yaspc.Optimization.Instruction.instruction as instruction
import yaspc.Optimization.BasicBlock.BasicBlock as BasicBlock
import yaspc.Optimization.BasicBlock.ConstructBasicBlock as ConstructBasicBlock
import yaspc.Optimization.BasicBlock.DestructBasicBlock as DestructBasicBlock
import yaspc.Optimization.IR_IO.irParser as irParser
import yaspc.Optimization.BasicBlock.ud as ud
import yaspc.Optimization.BasicBlock.PeepholeOptimization as PeepholeOptimization
import yaspc.Optimization.BasicBlock.loop as loop


def main():
    '''
    run a example of parser Three-address code and generate Basicblock list
    '''
    with open('looptest.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    # print(ir_str)
    # print(ir_json)
    # print(json.dumps(ir_json, sort_keys=True, indent=4))
    # print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    # print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    #inst_list = irParser.decode_body(ir_json['functionlist'][0]['body'])
    inst_list = irParser.decode_body(ir_json['body'])
    print('function 0 body parsed successfully.\n')
    for inst in inst_list:
        inst.ud = set()
        print(inst.pos, inst)
    print('\nConstrusting basicblock...')
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    print('\noptimizing control flow...')
    #inst_list = PeepholeOptimization.control_flow_optimization(block_list, inst_list)
    #block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    print('\nAnalyzing reach defination...')
    #var_reduce = ud.reach_def_iteration(block_list)
    #ud.ud_set(block_list, var_reduce)
    #ud.constant_propagation(block_list, var_reduce, inst_list)
    #ud.live_variable_analysis(block_list)

    print('\nAnalyzing loop...')
    loop.do_loop_optimization(block_list)
    #DestructBasicBlock.BlockList_to_InstList(block_list)

if __name__ == '__main__':
    main()
