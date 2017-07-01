from backend_in_py.asm.type import *
from backend_in_py.asm.operand import *
from backend_in_py.entity.entity import *
from backend_in_py.asm.type import *
from backend_in_py.ir.dumper import *
from backend_in_py.ir.stmt import *
from backend_in_py.ir.op import *
from backend_in_py.ir.expr import *
from backend_in_py.entity.scope import *


def import_ir (data: dict()):
    def_vars = list()
    def_funs = list()

    for i in data["variablelist"]:
        t = DefinedVariable (name = i["name"], type = i["type"], priv = i["is_private"], init = i["value"])
        def_vars.append(t)

    for i in data["functionlist"]:
        t = DefinedFuntion (priv = False, body = i["body"], name = i["name"], params = i["parameterlist"], type = i["type"], scope= LocalScope (i["variablelist"]))
        def_funs.append(t)

    ir = IR (source = "test.asm", defuns = def_funs, defvars = def_vars, constant_table = None, funcdecls = None, scope = None)
    return ir

def inst_factory (insn):
    if insn["name"] == "store":
        return Assign (loc= insn["line_number"], lhs= insn["address"], rhs= insn["value"])
    elif insn["name"] == "return":
        return Return (loc = insn ["line_number"], expr= insn["expr"])
    elif insn["name"] == "bin":
        return Bin (left= insn["left"], right= insn["right"], op= insn["op"], type= insn["type"], value= insn["value"])
    else:
        raise Exception ("Feature not implemented")


# This class were used to import IR from json text
class IR ():
    def __init__ (self,
                  source,
                  defvars,
                  defuns,
                  funcdecls,
                  constant_table,
                  scope):
        self.source = source
        self.defvars = defvars
        self.defuns = defuns
        self.funcdecls = funcdecls
        self.scope = scope
        self.constant_table = constant_table
        self.gvars = []
        self.comms = []

    def file_name (self):
        return self.source

    def location (self):
        return self.source

    def defined_variables (self):
        return self.defvars

    def is_function_defined (self):
        if self.defuns:
            return True
        else:
            return False

    def defined_funcitons(self):
        return self.defuns

    def scope (self):
        return self.scope

    def all_functions (self):
        result = []
        if self.defuns:
            result.extend(self.defuns)
        if self.funcdecls:
            result.extend(self.funcdecls)
        return result

    def init_variables (self):
        self.comms = []
        self.comms = []
        for var in self.scope.defined_glabal_scope_variables():
            if var.has_initializer == True:
                self.gvars.append(var)
            else:
                self.comms.append(var)


    #a list of all defined/declared global-scope variables
    def all_global_variables (self):
        #return self.scope.all_global_variables()
        return self.defvars

    def is_global_variable_defined (self):
        if self.defined_global_variables:
            return True
        else:
            return False

    #Returns the list of global variables.
    def defined_global_variables (self):
       #if not self.gvars:
       #     self.init_variables()
       # else:
       #     return self.gvars
        return self.defvars


    def is_common_symbol_defined(self):
        if self.defined_common_symbols():
            return True
        else:
            return False

    def defined_common_symbols (self):
        if not self.comms:
            self.init_variables()
        else:
            return self.comms

    def is_string_literal_defined(self):
        if self.constant_table:
            return True
        else:
            return False

    def const_table (self):
        return self.constant_table

    def dump (self):
        d = Dumper()
        d.print_class (self, self.source)
        d.print_vars ("variables", self.defvars)
        d.print_funs ("function", self.defuns)








