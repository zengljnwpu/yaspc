#!/usr/bin/env python
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
from yaspc.Optimization.BasicBlock import ConstructBasicBlock
from yaspc.Optimization.BasicBlock import DestructBasicBlock
from yaspc.Optimization.IR_IO import irParser
from yaspc.Optimization.DataFlow import ud
from yaspc.Optimization.Peephole import PeepholeOptimization
from yaspc.Optimization.Loop import loop


def main():
    '''
    run a example of parser Three-address code and generate Basicblock list
    '''
    with open('udtest.tac.txt', 'r') as input_file:
        ir_strs = input_file.readlines()
    print(ir_strs)
    print('=====================================')
    inst_list = irParser.decode_TAC_list(ir_strs)
    print('TAC parsed successfully.\n')
    for inst in inst_list:
        print('%3d\t%s'%(inst.pos, str(inst)))
    print('=====================================')
    # with open('udtest.json', 'r') as input_file:
    #     ir_str = input_file.read()
    #     ir_json = json.loads(ir_str)
    #inst_list = irParser.decode_body(ir_json['functionlist'][0]['body'])
    # print('function 0 body parsed successfully.\n')
    # for inst in inst_list:
    #     print(inst.pos, inst)
    print('\nConstrusting basicblock...')
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    if False:
        print('\noptimizing control flow...')
        inst_list = PeepholeOptimization.control_flow_optimization(block_list, inst_list)
        block_list = ConstructBasicBlock.ConstructBlockList(inst_list)
    if False:
        print('\nAnalyzing reach defination...')
        var_reduce = ud.reach_def_iteration(block_list)
        ud.ud_set(block_list, var_reduce)
        ud.constant_propagation(block_list, var_reduce, inst_list)
        ud.live_variable_analysis(block_list)
    if True:
        print('\nAnalyzing loop...')
        loop.do_loop_optimization(block_list)
    print('\nOptimized instructions:')
    inst_list = DestructBasicBlock.BlockList_to_InstList(block_list)
    for inst in inst_list:
        print(' %d\t%s'%(inst.pos, str(inst)))

if __name__ == '__main__':
    main()
