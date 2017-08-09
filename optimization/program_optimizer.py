# -*- coding: utf-8 -*-

"""
Created : 2017/8/9
Author: hellolzc axiqia
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import re

from optimization import optimization_manager

DEBUG = False

def set_debug_print(debug_print):
    """set DEBUG
    """
    global DEBUG
    DEBUG = debug_print

class ProgramOptimizer(object):
    """优化整体入口
    """
    def __init__(self):
        self.__function_list = list()
        self.__program_json = None

    def read(self, input_file_name):
        """读取JSON格式IR
        """
        # 打开输入的JSON IR，转换成JSON流
        with open(input_file_name, 'r') as input_file:
            ir_str = input_file.read()
            self.__program_json = json.loads(ir_str)

        # 将函数加入函数列表，0号位置放program的主函数
        opt_manager = optimization_manager.FunctionOptimizationManager()
        self.__function_list.append(opt_manager)
        opt_manager.decode_function_json(self.__program_json)
        for function_no, function_json in enumerate(self.__program_json['functionlist']):
            opt_manager = optimization_manager.FunctionOptimizationManager()
            self.__function_list.append(opt_manager)
            opt_manager.decode_function_json(function_json)


    def write(self, output_file_name):
        """输出JSON格式IR
        """
        # 更新JSON IR，0号位置放的是program的主函数
        for opt_no, opt_manager in enumerate(self.__function_list):
            function_json = opt_manager.encode_function_json()
            if opt_no == 0:
                self.__program_json = function_json
                self.__program_json['functionlist'] = []
            else:
                self.__program_json['functionlist'].append(function_json)

        # 把优化后的JSON文件写到JSON IR文件中
        with open(output_file_name, 'w') as output_file:
            ir_str = json.dumps(self.__program_json, sort_keys=True, indent=4)
            output_file.write(ir_str)

    def read_tac(self, input_file_name):
        """读取TAC格式IR
        """
        # 打开输入的TAC IR，将函数分割开
        with open(input_file_name, 'r') as input_file:
            lines = input_file.readlines()


        line_no = 0
        file_len = len(lines)
        # 跳过开头的语句
        while True:
            if line_no > file_len:
                print("No Function in this file.")
                return
            inst_string = lines[line_no]
            split = re.split(r'\s+', inst_string)
            if split[0] == 'function':
                break
            line_no = line_no + 1

        # 找出每一个函数
        while True:
            func_start = line_no
            while True:
                line_no = line_no + 1
                if line_no == file_len:
                    break
                inst_string = lines[line_no]
                split = re.split(r'\s+', inst_string)
                if split[0] == 'function':
                    break
            func_end = line_no

            #将函数加入函数列表
            opt_manager = optimization_manager.FunctionOptimizationManager()
            self.__function_list.append(opt_manager)
            opt_manager.decode_function_tac(lines[func_start:func_end])

            if line_no == file_len:
                break


    def optimize(self, control_flow=False, reach_defination=False, optimize_loop=False):
        """
        optimize a program
        """
        # 遍历Program程序中的所有函数或过程，根据指定的选项进行优化
        for opt_manager in self.__function_list:
            opt_manager.optimize(control_flow, reach_defination, optimize_loop)
