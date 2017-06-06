from backend_in_py.ir.ir import *
from backend_in_py.sys_dep.x86.code_generator import *
import json

with open ("data.json", "r") as f:
    str = f.read()
    data = json.loads(str)
    ir = import_ir(data)
    asm = CodeGenerator (None, Type.INT32)
    file = asm.generate(ir)
    file.dump()
    str = file.to_source()
    print (str)

