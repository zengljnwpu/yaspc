from __future__ import absolute_import, print_function

from backend.ir.ir import import_ir
from backend.sys_dep.x86.code_generator import *
import json

with open ("data.json", "r") as f:
    str = f.read()
    data = json.loads(str)
    ir = import_ir(data)
    asm = CodeGenerator (None, Type.INT32)
    file = asm.generate(ir)
    str = file.to_source()
    print (str)
