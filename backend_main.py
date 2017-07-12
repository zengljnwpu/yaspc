from __future__ import absolute_import, print_function

import json

from backend.ir.ir import import_ir
from backend.sys_dep.x86.code_generator import CodeGenerator
from backend.asm.type import Type

with open ("data.json", "r") as f:
    json_file_str = f.read()
    json_file_data = json.loads(json_file_str)
    json_ir = import_ir(json_file_data)
    asm = CodeGenerator (None, Type.INT32)
    json_new_file = asm.generate(json_ir)
    json_file_str = json_new_file.to_source()
    print (str)

