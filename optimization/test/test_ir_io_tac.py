#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci)
# Created : 2017/8/10

'''
read .tac.txt and get instruction lists
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.append('../..')

from optimization import program_optimizer

# 为了演示，将下列模块DEBUG输出打开
from optimization import function_data_unit
from optimization import optimization_manager
function_data_unit.set_debug_print(True)
function_data_unit.set_debug_print(True)

def test_module():
    '''
    run a example of IR and print instructions list
    '''
    prog_opt = program_optimizer.ProgramOptimizer()
    prog_opt.read_tac('IR_TAC_example.tac.txt')
    prog_opt.optimize()
    prog_opt.write('/tmp/out.txt')

if __name__ == '__main__':
    test_module()
