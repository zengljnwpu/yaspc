'''
yaspc front end for LLVM.
'''
from __future__ import absolute_import, print_function

import sys
import os
import datetime
import subprocess

import llvmlite.binding as llvm

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

from frontend import lexer
from frontend import parser
from frontend import typecheck
from frontend import visitor
from frontend import log
from frontend import codegen


class Compiler(object):

    def __init__(self, filename):
        self.ctx = None
        self.llmod = None
        self.ir = None
        self.tm = None
        self.filename = filename
        basename = os.path.basename(filename)
        filename = os.path.splitext(basename)
        self.name = filename[0]

    def analyze(self):
        log.d("compiler", "Parsing source code")

        l = lexer.lexer()
        p = parser.parser()

        def get_character_stream(filename):
            if filename == '-':
                chars = sys.stdin.read()
            else:
                fd = open(filename, "rb")
                chars = fd.read()
                fd.close()

            # python 3
            if not isinstance(chars, str):
                chars = chars.decode()

            return chars

        data = get_character_stream(self.filename)

        self.ast = p.parse(input=data, lexer=l, tracking=True)

        if not self.ast:
            sys.exit(1)

        v = typecheck.TypeSetVisitor()
        self.ast.accept(v)
        v = typecheck.FixBuiltinCallbyRefVisitor()
        self.ast.accept(v)


    def print_tree(self):
        if self.ast is not None:
            log.d("compiler", "Printing syntax tree for %s" % self.filename)
            self.ast.accept(visitor.PrintVisitor())


    def synthesize(self, triple, cpu):
        log.d("compiler", "Generating code")
        v = codegen.CodegenVisitor()
        self.ast.accept(v)
        self.ctx = v.ctx

        if self.ctx is None or self.ctx.module is None:
            return

        if not cpu: cpu = 'generic'
        
        target = llvm.Target.from_default_triple()
        if triple is not None:
            target = llvm.Target.from_triple(triple)
        self.tm = target.create_target_machine(cpu=cpu)
        self.ctx.module.target = str(target.triple)
        self.ctx.module.data_layout = str(self.tm.target_data)

        self.ir = "; Generated by frontend from %s at %s\n%s" % (
            self.filename, datetime.datetime.now().strftime("%c"),
            self.ctx.module)

        self.llmod = llvm.parse_assembly(self.ir)

        self.llmod.verify()


    def optimize(self, level=0):
        log.i("compiler", "Optimizing code at level %d" % level)

        pmb = llvm.PassManagerBuilder()
        pm = llvm.ModulePassManager()

        pmb.opt_level = level
        pmb.populate(pm)

        pm.run(self.llmod)

    
    def save_ir(self, out):
        if self.ir is None:
            return
        
        if out == '-':
            print(self.ir)
        else:
            f = open(out, "wb")
            f.write(self.ir.encode())
            f.close()


    def save_bit_code(self, out):
        if self.llmod is None:
            return

        bc = self.llmod.as_bitcode()

        if out == '-':
            os.write(sys.stdout.fileno(), bc)
        else:
            f = open(out, "wb")
            f.write(bc)
            f.close()


    def save_obj_code(self, out):
        if self.tm is None or self.llmod is None:
            return

        obj = self.tm.emit_object(self.llmod)

        if out == '-':
            os.write(sys.stdout.fileno(), obj)
        else:
            f = open(out, "wb")
            f.write(obj)
            f.close()


    def save_asm_code(self, out):
        if self.tm is None or self.llmod is None:
            return

        asm = self.tm.emit_assembly(self.llmod)

        if out == '-':
            os.write(sys.stdout.fileno(), asm)
        else:
            f = open(out, "wb")
            f.write(asm)
            f.close()

        
    def save_executable(self, out):
        llfilename = out + '.ll'
        self.save_ir(llfilename)
        subprocess.call(['clang', llfilename, '-o', out])