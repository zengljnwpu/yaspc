#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci) , axiqia
# Created : 2017/6/19

'''
The main entrance of all optimization codes
read a json IR and write a optimized json IR
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

from frontend import log
from Optimization.BasicBlock import ConstructBasicBlock
from Optimization.BasicBlock import DestructBasicBlock
from Optimization.IR_IO import irParser
from Optimization.Peephole import PeepholeOptimization
from Optimization.DataFlow import ud
from Optimization.Loop import loop

def optimize_a_function(function_json, control_flow=False, \
    reach_defination=False, optimize_loop=False, debug_print=True):
    """
    optimize a body of a function or a program (JSON format object)
    return optimized body and updated label list (JSON format object)
    """

    input_body_json = function_json['body']
    input_variablelist_json = function_json['variablelist']
    inst_list = irParser.decode_variablelist(input_variablelist_json) + \
        irParser.decode_body(input_body_json)
    inst_list = irParser.renumbering(inst_list)
    
    if debug_print:
        for inst in inst_list:
            log.d('optimization', '%3d\t%s' % (inst.pos, str(inst)))
    
    # 划分基本快
    log.i('optimization', '\nConstrusting basicblock...')
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)

    # 若控制流指定时，则进行控制流优化
    if control_flow:
        log.i('optimization', '\nOptimizing control flow...')
        inst_list = PeepholeOptimization.control_flow_optimization(
            block_list, inst_list)
        block_list = ConstructBasicBlock.ConstructBlockList(inst_list)

    if reach_defination:
        log.i('optimization', '\nAnalyzing reach defination...')
        var_reduce = ud.reach_def_iteration(block_list)
        ud.ud_set(block_list, var_reduce)
        ud.constant_propagation(block_list, var_reduce, inst_list)
        ud.live_variable_analysis(block_list)

    # 若指定循环优化，则进行循环优化
    if optimize_loop:
        log.i('optimization', '\nAnalyzing loop...')
        loop.do_loop_optimization(block_list)

    log.i('optimization', '\nGenerating New IR...')
    inst_list = DestructBasicBlock.BlockList_to_InstList(block_list)
    inst_list = PeepholeOptimization.remove_unused_label(inst_list)
    new_labellist = DestructBasicBlock.generate_labellist(inst_list)
    inst_list_json = irParser.encode_body(inst_list)
    labellist_json = new_labellist

    log.d('optimization', "============LinearInstructionList==================")
    for inst in inst_list:
        log.d('optimization', '%3d\t%s' % (inst.pos, str(inst)))
    log.d('optimization', "=================LabelList=========================")
    log.d('optimization', json.dumps(labellist_json, sort_keys=True, indent=4))
    return inst_list_json, labellist_json


def optimize_a_program(program_json, control_flow=False, \
    reach_defination=False, optimize_loop=False):

    """
    optimize a program (JSON format object)
    return optimized program (JSON format object)
    """
    # 遍历Program程序中的所有函数或过程，根据指定的选项进行优化
    for function_no, function_json in enumerate(program_json['functionlist']):
        log.i('optimization',
              '\n---------------------------------------------------------')
        log.i('optimization', '\nparsing the body of function "%s" ...\n' %
              function_json["name"])
        
        new_body, new_labellist = optimize_a_function(function_json, control_flow, \
            reach_defination, optimize_loop, debug_print=True)

        log.i('optimization', 'function %d body parsed successfully.\n' %
              function_no)
        function_json['body'] = new_body
        function_json['labellist'] = new_labellist

    log.i('optimization', '\n---------------------------------------------------------')
    log.i('optimization', '\nparsing the body of main function ...\n')

    new_body, new_labellist = optimize_a_function(program_json, control_flow, \
        reach_defination, optimize_loop, debug_print=True)

    log.i('optimization', 'program body parsed successfully.\n')
    program_json['body'] = new_body
    program_json['labellist'] = new_labellist

    return program_json


def optimize_exec(input_file_name, output_file_name, \
    control_flow=False, reach_defination=False, optimize_loop=False):
    '''
    The main function of all optimization
    '''
    log.i('optimization', '\nWelcome!')
    log.i('optimization', 'INPUT: %s \tOUTPUT %s' %
          (input_file_name, output_file_name))
    log.i('optimization', 'Selction: \n\toptimize control flow: %s' % control_flow)
    log.i('optimization', '\toptimize reach defination: %s' % reach_defination)
    log.i('optimization', '\toptimize loop: %s\n' % optimize_loop)

    # 打开输入的JSON IR，转换成JSON流
    with open(input_file_name, 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)

    # log.i('optimization', json.dumps(ir_json, sort_keys=True, indent=4))
    ir_json = optimize_a_program(ir_json, control_flow, reach_defination, optimize_loop)
    log.i('optimization', '\n---------------------------------------------------------')

    # 把优化后的JSON文件写到JSON IR文件中
    log.i('optimization', '\nWrite output file...\n')
    with open(output_file_name, 'w') as output_file:
        ir_str = json.dumps(ir_json, sort_keys=True, indent=4)
        output_file.write(ir_str)
