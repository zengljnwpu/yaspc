#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci) 
# Created : 2017/8/12

'''
优化部分的一个完整示例
'''

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse

# 将yaspc所在路径加入path，确保import能正常运行
import sys
sys.path.append('../..')

from optimization import program_optimizer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add optional arguments #not positional arguments
    parser.add_argument(
        '-i',
        dest='input_file_name',
        type=str,
        default='dsq.newir.json',
        help='Input IR File name (default is dsq.newir.json)'
    )
    parser.add_argument(
        '-o',
        dest='output_file_name',
        type=str,
        default='dsq.irout.json',
        help='Output IR File name (default is dsq.irout.json)'
    )

    # add conflicting options
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument('--control_flow', action="store_true",
                        help='optimize control flow (default)')
    group1.add_argument('--no_control_flow', action="store_true",
                        help='do not optimize control flow')

    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument('--reach_defination', action="store_true",
                        help='optimize reach defination (default)')
    group2.add_argument('--no_reach_defination', action="store_true",
                        help='do not optimize reach defination')

    group3 = parser.add_mutually_exclusive_group()
    group3.add_argument('--loop', action="store_true",
                        help='optimize loop (default)')
    group3.add_argument('--no_loop', action="store_true",
                        help='do not optimize loop')

    # parse arguments
    args = parser.parse_args()
    # set default value
    control_flow_flag = not args.no_control_flow
    reach_defination_flag = not  args.no_reach_defination
    loop_optimization_flag = not args.no_loop

    prog_opt = program_optimizer.ProgramOptimizer()
    prog_opt.read(args.input_file_name)
    prog_opt.optimize(control_flow_flag, reach_defination_flag, loop_optimization_flag)
    prog_opt.write(args.output_file_name)
