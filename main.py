'''
Command line interface for frontend.
'''
from __future__ import absolute_import, print_function

import sys
import os

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter

from frontend import log
from frontend import compiler

from frontend import explain

from backend.ir.ir import import_ir
from backend.sys_dep.x86.code_generator import *

import json

from Optimization import do_optimization

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


def run(argv=None):
    sys.setrecursionlimit(50000)

    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__date__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = 'frontend - LLVM-based Pascal 1973 compiler'

    try:
        # Setup argument parser
        parser = ArgumentParser(
            prog=program_name, description=program_shortdesc, formatter_class=RawTextHelpFormatter)
        parser.add_argument("-t", "--syntax-tree", dest="tree",
                            action="store_true", help="print the syntax tree to stdout")

        parser.add_argument("-C", "--json-code", dest="json_code", metavar="PATH",
                            action="store", help="translate json IR to ASM PATH")
        
        parser.add_argument("-F", "--json-frontend", dest="json_frontend", metavar="PATH",
                            action="store", help="generate json IR to PATH")

        parser.add_argument("-P", "--json-opt", dest="json_opt", metavar="PATH",
                            action="store", help="generate json IR to PATH")
        
        parser.add_argument("-A", "--json-asm", dest="json_asm", metavar="PATH",
                            action="store", help="translate PAS to ASM")

        parser.add_argument("-S", "--emit-llvm", dest="ir_code", metavar="PATH",
                            action="store", help="save LLVM-IR (plain text) to PATH")
        parser.add_argument("-b", "--bit-code", dest="bit_code", metavar="PATH",
                            action="store", help="save LLVM-IR (bit code) to PATH")
        parser.add_argument("-o", "--object-code", dest="obj_code",
                            metavar="PATH", action="store", help="save object code to PATH")
        parser.add_argument("-O", "--optimize", dest="optimize", metavar="LEVEL", action="store", choices=[
                            '0', '1', '2', '3'], default='0', 
                            help="run various optimizations on the LLVM-IR code")
        parser.add_argument('-a', '--asm', dest='asm_code', metavar='PATH',
                            action='store', help='save native assembly code to PATH')
        parser.add_argument('-e', '--executable', dest='exe', metavar='PATH',
                            action='store', help='generate executable file using clang and save to PATH')

        parser.add_argument("-T", "--triple", dest="triple", action="store", default=None,
                            help="define the target triple, e.g. x86_64-pc-linux or i686-pc-win32")
        parser.add_argument("-mcpu", dest="cpu", default=None,
                            help='target specific cpu type')

        parser.add_argument("-v", "--verbosity",
                            dest="verbosity", action="count", default=0)
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)
        parser.add_argument(dest="file", metavar="file")


        # Process arguments
        args = parser.parse_args()

        if args.verbosity:
            log.set_verbosity(args.verbosity)
        else:
            log.set_verbosity(0)


        llvm_ir = (args.ir_code or args.bit_code or
                      args.obj_code or args.asm_code or
                      args.exe)

        if llvm_ir or args.json_frontend or args.json_asm or args.tree:
            current_compiler = compiler.Compiler(args.file)
            current_compiler.analyze()

        if args.tree:
            current_compiler.print_tree()

        if llvm_ir:
            current_compiler.synthesize(args.triple, args.cpu)

            if args.opt:
                current_compiler.optimize(int(args.opt))

            if args.ir_code:
                current_compiler.save_ir(args.ir_code)

            if args.bit_code:
                current_compiler.save_bit_code(args.bit_code)

            if args.obj_code:
                current_compiler.save_obj_code(args.obj_code)

            if args.asm_code:
                current_compiler.save_asm_code(args.asm_code)

            if args.exe:
                current_compiler.save_executable(args.exe)

        else:
            if args.json_frontend:
                ir_json = explain.explain()
                ir_json.programExplain(current_compiler.ast)
                ir_json.store(args.json_frontend)

            optimize_level = int(args.optimize)
            if optimize_level != 0:
                if args.json_frontend:
                    opt_input_file = args.json_frontend
                    opt_output_file = args.json_frontend
                else:
                    opt_input_file = args.file
                    opt_output_file = args.file
                # set default value
                control_flow_flag = False
                reach_defination_flag = False
                loop_optimization_flag = False
                if optimize_level >= 3:
                    loop_optimization_flag = True
                if optimize_level >= 2:
                    reach_defination_flag = True
                if optimize_level >= 1:
                    control_flow_flag = True
                # do optimization
                do_optimization.main(
                        opt_input_file, opt_output_file, control_flow_flag,
                        reach_defination_flag, loop_optimization_flag)

            '''
            if args.json_asm:
            '''
            
            if args.json_code:
                with open (args.file, "r") as json_ir_file:
                    json_file_str = json_ir_file.read()
                    data = json.loads(json_file_str)
                    json_ir = import_ir(data)
                    asm = CodeGenerator (None, Type.INT32)
                    json_new_file = asm.generate(json_ir)
                    json_file_str = json_new_file.to_source()
                    print (json_file_str)

        return 0

    except KeyboardInterrupt:
        return 0
