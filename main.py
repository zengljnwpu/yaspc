# -*- coding: utf-8 -*-

'''
Command line interface for yaspc.
'''
from __future__ import absolute_import, print_function

import sys
import os
import json

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

from frontend import log
from frontend import compiler

from frontend import explain

from backend.ir.ir import import_ir
from backend.sys_dep.x86.code_generator import CodeGenerator
from backend.asm.inttype import IntType

from optimization import do_optimization

__version__ = 0.4
__date__ = '2017-06-02'

DEBUG = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''

    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg

def analysisarg(argv):
    """ 对输入的参数进行解析 """

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__date__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = 'Pascal 1973 compiler'

    # Setup argument parser
    parser = ArgumentParser(
        prog=program_name,
        description=program_shortdesc,
        formatter_class=RawTextHelpFormatter)

    parser.add_argument("-t", "--syntax-tree", dest="tree",
                        action="store_true", help="print the syntax tree to stdout")

    parser.add_argument("-C", "--json-backend", dest="json_backend",
                        action="store_true", help="translate json IR to ASM")

    parser.add_argument("-F", "--json-frontend", dest="json_frontend",
                        action="store_true", help="translate PAS to json IR")

    parser.add_argument("-A", "--json-asm", dest="json_asm",
                        action="store_true", help="translate json IR to ASM")

    parser.add_argument("-S", "--emit-llvm", dest="ir_code",
                        action="store_true", help="save LLVM-IR (plain text)")
    parser.add_argument("-b", "--bit-code", dest="bit_code",
                        action="store_true", help="save LLVM-IR (bit code)")
    parser.add_argument("-o", "--object-code", dest="obj_code",
                        action="store_true", help="save object code")
    parser.add_argument("-O", "--optimize", dest="optimize", metavar="LEVEL", action="store",
                        choices=['0', '1', '2', '3'], default='0',
                        help="run various optimizations on the LLVM-IR code")
    parser.add_argument('-a', '--asm', dest='asm_code',
                        action='store_true', help='save native assembly code')
    parser.add_argument('-e', '--executable', dest='exe',
                        action='store_true', help='generate executable file using clang and save')

    parser.add_argument("-T", "--triple", dest="triple", action="store", default=None,
                        help="define the target triple, e.g. x86_64-pc-linux or i686-pc-win32")

    parser.add_argument("-mcpu", dest="cpu", default=None,
                        help='target specific cpu type')

    parser.add_argument("-v", "--verbosity",
                        dest="verbosity", action="count", default=0)
    parser.add_argument('-V', '--version', action='version',
                        version=program_version_message)
    parser.add_argument(dest="ifile", metavar="ifile")
    parser.add_argument(dest="ofile", metavar="ofile")

    # Process arguments
    args = parser.parse_args()

    return args

def json_optimize(level, input_file, output_file):
    '''
    对JSON格式的IR依据指定的优化级别level进行优化
    @param level: 优化级别
    @param input_file: 输入的JSON文件
    @param output_file: 输出的JSON文件 
    '''

    if level != 0:
        # set default value
        control_flow_flag = False
        reach_defination_flag = False
        loop_optimization_flag = False
        if level >= 3:
            loop_optimization_flag = True
        if level >= 2:
            reach_defination_flag = True
        if level >= 1:
            control_flow_flag = True

        # do optimization
        do_optimization.optimize_exec(
            input_file,
            output_file,
            control_flow_flag,
            reach_defination_flag,
            loop_optimization_flag)


def json_backend(input_file, output_file):
    """ 对JSON格式的IR进行后端处理，把JSON格式的IR转换为汇编语言ASM """

    with open(input_file, "r") as json_ir_file:
        ''' 打开JSON格式的IR文件，转换成JSON流 '''
        json_file_str = json_ir_file.read()
        json_file_data = json.loads(json_file_str)

        json_ir = import_ir(json_file_data, output_file)

        # 对JSON文件格式的IR进行后端处理，产生汇编代码
        asm = CodeGenerator(None, IntType.INT32)
        json_new_file = asm.generate(json_ir)

        json_file_str = json_new_file.to_source()

        # 把转换后的汇编程序写到文件中
        with open(output_file, 'w') as json_output_file:
            json_output_file.write(json_file_str)


def run(argv=None):
    """ 主函数的流程 """
    sys.setrecursionlimit(50000)

    try:

        args = analysisarg(argv)

        if args.verbosity:
            log.set_verbosity(args.verbosity)
        else:
            log.set_verbosity(0)

        input_file = args.ifile
        output_file = args.ofile

        llvm_ir = (args.ir_code or args.bit_code or
                   args.obj_code or args.asm_code or
                   args.exe)

        if llvm_ir or args.json_frontend or args.json_asm or args.tree:
            current_compiler = compiler.Compiler(input_file)
            current_compiler.analyze()

        if args.tree:
            current_compiler.print_tree()

        if llvm_ir:
            current_compiler.synthesize(args.triple, args.cpu)

            if args.optimize:
                current_compiler.optimize(int(args.optimize))

            # 后面的选项同时只有一个有效，若没有指定，则默认按照LLVM IR输出
            if args.ir_code:
                current_compiler.save_ir(output_file)
            elif args.bit_code:
                current_compiler.save_bit_code(output_file)
            elif args.obj_code:
                current_compiler.save_obj_code(output_file)
            elif args.asm_code:
                current_compiler.save_asm_code(output_file)
            elif args.exe:
                current_compiler.save_executable(output_file)
            else:
                current_compiler.save_ir(output_file)

        else:

            # 若只进行前端操作，则进行词法、语法和语义处理，产生中间表示语言IR（JSON格式）
            if args.json_frontend:
                ir_json = explain.explain()
                ir_json.programExplain(current_compiler.ast)
                ir_json.store(output_file)

            # 优化作为可选项，进行优化。若不指定，则优化级别为0
            optimize_level = int(args.optimize)
            if optimize_level != 0:

                # 若前端指定，则优化的输入和输出文件都是前端的输出文件
                if args.json_frontend:
                    opt_input_file = output_file
                    opt_output_file = output_file
                else:
                    opt_input_file = input_file
                    opt_output_file = output_file

                json_optimize(optimize_level, opt_input_file, opt_output_file)

            if args.json_backend:

                # 若前端指定，则后端的输入和输出文件都是前端的输出文件
                if args.json_frontend:
                    backend_input_file = output_file
                    backend_output_file = output_file
                else:
                    backend_input_file = input_file
                    backend_output_file = output_file

                json_backend(backend_input_file, backend_output_file)

        return 0

    except KeyboardInterrupt:
        return 0
