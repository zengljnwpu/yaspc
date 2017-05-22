'''
frontend front end for LLVM.
'''
from __future__ import absolute_import, print_function

import sys
import os

from frontend import lexer
from frontend import parser
from frontend import typecheck
from frontend import visitor
from frontend import log


class Compiler(object):

    def __init__(self, filename):
        self.ctx = None
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

    def print_tree(self):
        if self.ast is not None:
            log.d("compiler", "Printing syntax tree for %s" % self.filename)
            self.ast.accept(visitor.PrintVisitor())
