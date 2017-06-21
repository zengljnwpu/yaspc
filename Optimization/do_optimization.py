#!/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci) , axiqia
# Created : 2017/6/19

'''
read .json and get instruction lists
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import argparse

from yaspc.Optimization.Instruction import instruction
from yaspc.Optimization.BasicBlock import ConstructBasicBlock
from yaspc.Optimization.BasicBlock import DestructBasicBlock
from yaspc.Optimization.IR_IO import irParser
from yaspc.Optimization.BasicBlock import PeepholeOptimization
from yaspc.Optimization.BasicBlock import ud
from yaspc.Optimization.BasicBlock import loop

def do_optimization(input_body_json, control_flow=False, reach_defination=False, optimize_loop=False, debug_print=True):
    """optimize a body of a function or a program (JSON format object)
    return optimized body and updated label list (JSON format object)
    """
    inst_list = irParser.decode_body(input_body_json)
    if debug_print:
        for inst in inst_list:
            print('%3d\t%s'%(inst.pos, str(inst)))
    print('\nConstrusting basicblock...')
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)

    if control_flow:
        print('\nOptimizing control flow...')
        inst_list = PeepholeOptimization.control_flow_optimization(block_list, inst_list)
        block_list = ConstructBasicBlock.ConstructBlockList(inst_list)

    if reach_defination:
        print('\nAnalyzing reach defination...')
        var_reduce = ud.reach_def_iteration(block_list)
        ud.ud_set(block_list, var_reduce)
        ud.constant_propagation(block_list, var_reduce, inst_list)
        ud.live_variable_analysis(block_list)

    if optimize_loop:
        print('\nAnalyzing loop...')
        loop.do_loop_optimization(block_list)

    print('\nGenerating New IR...')
    inst_list = DestructBasicBlock.BlockList_to_InstList(block_list)
    inst_list = PeepholeOptimization.remove_unused_label(inst_list)
    new_labellist = DestructBasicBlock.generate_labellist(inst_list)
    inst_list_json = irParser.encode_body(inst_list)
    labellist_json = new_labellist

    if debug_print:
        print ("============LinearInstructionList==================")
        for inst in inst_list:
            print('%3d\t%s'%(inst.pos, str(inst)))
        print ("=================LabelList=========================")
        print(json.dumps(labellist_json, sort_keys=True, indent=4))
    return inst_list_json, labellist_json


def main(input_file_name, output_file_name, control_flow=False, reach_defination=False, loop=False):
    '''
    The main function of all optimization
    '''
    print('Welcome!')
    print('INPUT: %s \tOUTPUT %s'%(input_file_name, output_file_name))
    print('Selction: \n\tcontrol_flow: %d'%control_flow)
    print('\treach_defination: %d'%reach_defination)
    print('\tloop: %d\n'%loop)
    with open(input_file_name, 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    #print(ir_str)
    #print(ir_json)
    #print(json.dumps(ir_json, sort_keys=True, indent=4))
    #print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    #print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    for function_no, function_json in enumerate(ir_json['functionlist']):
        print('parsing function %s body ...\n'%function_json["name"])
        new_body, new_labellist = do_optimization(function_json['body'], control_flow, \
                                                  reach_defination, loop, debug_print=True)
        print('function %d body parsed successfully.\n'%function_no)
        function_json['body'] = new_body
        function_json['labellist'] = new_labellist

    print('parsing main function body ...\n')
    new_body, new_labellist = do_optimization(ir_json['body'], control_flow, \
                                              reach_defination, loop, debug_print=True)
    print('program body parsed successfully.\n')
    ir_json['body'] = new_body
    ir_json['labellist'] = new_labellist

    print('Write output file...\n')
    with open(output_file_name, 'w') as output_file:
        ir_str = json.dumps(ir_json, sort_keys=True, indent=4)
        output_file.write(ir_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_file_name',
        type=str,
        default='IR_IO/dsq.ir.json',
        help='Input IR File name'
    )
    parser.add_argument(
        '--output_file_name',
        type=str,
        default='IR_IO/dsq.irout.json',
        help='Output IR File name'
    )
    parser.add_argument(
        '--control_flow',
        type=int,
        default=1,
        help='1: optimize control flow'
    )
    parser.add_argument(
        '--reach_defination',
        type=int,
        default=1,
        help='1: optimize reach defination'
    )
    parser.add_argument(
        '--loop',
        type=int,
        default=1,
        help='1: optimize loop'
    )
    FLAGS, unparsed = parser.parse_known_args()
    main(FLAGS.input_file_name, FLAGS.output_file_name, bool(FLAGS.control_flow),\
         bool(FLAGS.reach_defination), bool(FLAGS.loop))


