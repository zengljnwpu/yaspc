'''
Command line interface for frontend.
'''
from __future__ import absolute_import, print_function

import sys
import os

from frontend import log
from frontend import compiler

from argparse import ArgumentParser
from argparse import RawTextHelpFormatter
from frontend import explain

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
        parser = ArgumentParser(prog=program_name, description=program_shortdesc, formatter_class=RawTextHelpFormatter)
        parser.add_argument("-t", "--syntax-tree", dest="tree", action="store_true", help="print the syntax tree to stdout")
        parser.add_argument("-S", "--emit-llvm", dest="ir_code", metavar="PATH", action="store", help="save LLVM-IR (plain text) to PATH")
        parser.add_argument("-b", "--bit-code", dest="bit_code", metavar="PATH", action="store", help="save LLVM-IR (bit code) to PATH")
        parser.add_argument("-o", "--object-code", dest="obj_code", metavar="PATH", action="store", help="save object code to PATH")
        parser.add_argument("-O", "--optimize", dest="opt", metavar="LEVEL", action="store", choices=['0', '1', '2', '3'], default='0', help="run various optimizations on the LLVM-IR code")
        parser.add_argument('-a', '--asm', dest='asm_code', metavar='PATH', action='store', help='save native assembly code to PATH')
        parser.add_argument('-e', '--executable', dest='exe', metavar='PATH', action='store', help='generate executable file using clang and save to PATH')

        parser.add_argument("-T", "--triple", dest="triple", action="store", default=None, help="define the target triple, e.g. x86_64-pc-linux or i686-pc-win32")
        parser.add_argument("-mcpu", dest="cpu", default=None, help='target specific cpu type')

        parser.add_argument("-v", "--verbosity", dest="verbosity", action="count", default=0)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument(dest="file", metavar="file")

        # Process arguments
        args = parser.parse_args()

        if args.verbosity:
            log.set_verbosity(args.verbosity)
        else:
            log.set_verbosity(0)

        c = compiler.Compiler(args.file)

        c.analyze()

        if args.tree:
            c.print_tree()

        synthesize = (args.ir_code or args.bit_code or
                      args.obj_code or args.asm_code or
                      args.exe)


        a = explain.explain()
        a.programEplain(c.ast, c.ctx)
        a.store()

        if synthesize:
            c.synthesize(args.triple, args.cpu)

        if args.opt and synthesize:
            c.optimize(int(args.opt))

        if args.ir_code:
            c.save_ir(args.ir_code)

        if args.bit_code:
            c.save_bit_code(args.bit_code)

        if args.obj_code:
            c.save_obj_code(args.obj_code)
        
        if args.asm_code:
            c.save_asm_code(args.asm_code)

        if args.exe:
            c.save_executable(args.exe)

        return 0

    except KeyboardInterrupt:
        return 0
