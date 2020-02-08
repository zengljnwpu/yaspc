#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : axiqia, lzc80234@qq.com (liuzhaoci)
# Created : 2017/8/12
'''
测试并演示所有优化部分
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# 将yaspc所在路径加入path，确保import能正常运行
import sys
sys.path.append('../..')

from optimization import program_optimizer

# 为了演示，将下列模块DEBUG输出打开
from optimization import function_data_unit
from optimization import optimization_manager
from optimization import data_flow
from optimization import peephole
from optimization import loop
optimization_manager.set_debug_print(True)
function_data_unit.set_debug_print(False)
data_flow.set_debug_print(True)
peephole.set_debug_print(True)
loop.set_debug_print(True)

def main():
    '''
    run a example TAC IR and optimize it
    '''
    input_file_name = 'udtest.tac.txt'
    print("read file %s ..." % input_file_name)

    prog_opt = program_optimizer.ProgramOptimizer()
    prog_opt.read_tac(input_file_name)
    prog_opt.optimize(control_flow=True, reach_defination=True, optimize_loop=True)
    # prog_opt.write('/tmp/out.txt')

if __name__ == '__main__':
    main()
