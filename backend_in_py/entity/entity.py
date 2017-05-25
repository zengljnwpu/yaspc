from backend_in_py.asm.assembly import *
from backend_in_py.asm.operand import *
from backend_in_py.asm.literal import *

class Entity (object):
    def __init__ (self, priv:bool, type, name:str):
        self.name = name
        self.is_private = priv
        self.type_node = type
        self.n_refered = 0
        self._mem_ref = None
        self._address = None

    def symbol_string(self):
        return self.name

    def is_defined(self):
        return

    def is_initialized(self):
        return

    def is_constant(self):
        return False

    def value(self):
        raise Exception ("Entity#value")

    def is_parameter(self):
        return False

    def is_private(self):
        return self.is_private

    def type(self):
        return self.type_node.type()

    def alloc_size(self):
        return self.type().alloc_size()

    def alignment(self):
        return self.type().alignment()

    def refered(self):
        self.n_refered += 1

    def  is_refered(self):
        return self.n_refered > 0

    @property
    def mem_ref (self):
        self._check_address()
        return self._mem_ref

    def set_mem_ref(self, mem: MemoryReference):
        self._mem_ref = mem

    @property
    def address(self):
        self._check_address()
        return self._address

    def set_address (self, mem):
        if isinstance(mem, MemoryReference):
            self._address = mem
        elif isinstance(mem, ImmediateValue):
            self._address = mem

    def _check_address(self):
        if (not self.mem_ref and not self.address):
            raise Exception ("_address did not resolved: " + self.name)

    def location (self):
        return self.type_node.location()

    def accept (self, visitor):
        return

    def dump(self, d):
        d.print_class (self.location())
        self._dump (d)

    def _dump(self, d):
        return


class Constant (Entity):
    def __init__(self, type, name, value):
        super(Constant, self).__init__(True, type, name)
        self.__value = value

    def is_assignable (self):
        return False

    def is_defined(self):
        return True

    def is_initialized(self):
        return True

    def is_constant(self):
        return True

    @property
    def value(self):
        return self.__value

    def _dump(self, d):
        d.print_member ("name", self.name)
        d.print_member ("type_node", self.type_node)
        d.print_member ("value", self.value)

    def accept(self, visitor):
        return visitor.visit()


class Function (Entity):
    def __init__(self, priv: bool, t, name: str):
        super().__init__(priv, t, name)
        self._calling_symbol = None
        self._label = None

    def is_initialized(self):
        return True

    def is_defined(self):
        return

    def parameters(self):
        return

    def return_type(self):
        return self.type().get_function_type().return_type()

    def is_void (self):
        return self.return_type().is_void()

    def set_calling_symbol (self, sym: Symbol):
        if self._calling_symbol:
            raise Exception ("must not happen: Function#callingSymbol was set again")
        self._calling_symbol = sym

    @property
    def calling_symbol (self):
        if not self._calling_symbol:
            raise Exception  ("must not happen: Function#callingSymbol was set again")
        return self._calling_symbol

    @property
    def label (self):
        if self._label:
            return self._label
        else:
            self._label = Label (self._calling_symbol())
            return self._label


class DefinedFuntion (Function):
    def __init__(self, priv: bool, type, name: str, params, body):
        super(DefinedFuntion, self).__init__(priv, type, name)
        self._params = params
        self._body = body
        self._scope = None
        self._ir = None

    def is_defined(self):
        return True

    @property
    def parameters(self):
        return self._params.parameters()

    @property
    def body(self):
        return self._body

    @property
    def ir (self):
        return self._ir

    def set_ir (self, ir):
        self._ir = ir

    def set_scope (self, scope):
        self._scope = scope

    def lvar_scope (self):
        return self.body.scope()

    #
    # Returns function local variables
    # Does NOT include parameters
    # Does NOT include static local variables

    def local_variables (self):
        return self._scope.all_local_variables()

    def _dump(self, d):
        d.print_member ("name", self.name)
        d.print_member ("is_private", self.is_private())
        d.print_member ("params", self._params)
        d.print_member ("body", self.body)

    def accept(self, visitor):
        return visitor.visit ()


class UndefinedFunction (Function):
    def __init__(self, t, name, params):
        super(UndefinedFunction, self).__init__(False, t, name)
        self._params = params

    def parameters(self):
        return self._params.parameters()

    def is_defined(self):
        return False

    def _dump(self, d):
        d.print_member("name", self.name)
        d.print_member("is_private", self.is_private())
        d.print_member("type_node", self.type_node)
        d.print_member("params", self._params)

    def accept(self, visitor):
        return visitor.visit()

class Variable (Entity):
    def __init__(self, priv:bool, type, name):
        super(Variable, self).__init__(priv, type, name)


class UndefinedVariable (Variable):
    def __init__(self, t, name):
        super(UndefinedVariable, self).__init__(False, t, name)

    def is_defined(self):
        return False

    def is_private(self):
        return False

    def is_initialized(self):
        return False

    def _dump(self, d):
        d.print_member("name", self.name)
        d.print_member("is_private", self.is_private())
        d.print_member("type_node", self.type_node)

    def accept(self, visitor):
        return visitor.visit()
class DefinedVariable (Variable):
    def __init__(self, priv, type, name, init):
        super(DefinedVariable, self).__init__(priv, type, name)
        self._initializer = init
        self._sequence = -1
        self._symbol = None
        self._ir = None

    tmp_seq = 0

    @classmethod
    def tmp (cls, t):
        return DefinedVariable (False, TypeNode(t), "@tmp" + str(cls.tmp_seq), None)

    def is_defined(self):
        return True

    def set_sequence (self, seq):
        self._sequence = seq

    def symbol_string(self):
        if self._sequence < 0:
            return self.name
        else:
            return self.name + "." + str(self._sequence)

    def has_initializer(self):
        return self._initializer != None

    def is_initialized(self):
        return self.has_initializer()

    @property
    def initializer (self):
        return self._initializer

    def set_initializer (self, expr):
        self._initializer = expr

    def set_ir (self, expr):
        self._ir = expr

    @property
    def ir(self):
        return self._ir

    def _dump(self, d):
        d.print_member("name", self.name)
        d.print_member("is_private", self.is_private())
        d.print_member("type_node", self.type_node)
        d.print_member("initializer", self.initializer)

    def accept(self, visitor):
        return visitor.visit()

class Parameter (DefinedVariable):
    def __init__(self, type, name):
        super(Parameter, self).__init__(False, type, name, None)

    def is_parameter(self):
        return True

    def _dump(self, d):
        d.print_member ("name", self.name)
        d.print_member ("type_node", self.type_node)

