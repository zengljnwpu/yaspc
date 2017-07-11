from backend.asm.assembly import *
from backend.asm.operand import *
from backend.asm.literal import *
import backend.type.type
import backend.ir.ir

entity_map = dict()

class Entity (object):
    def __init__ (self, priv, type, name):
        self._name = name
        self._is_private = priv
        self._type = backend.type.type.Type.type_factory(type, name)
        self.n_refered = 0
        self._mem_ref = None
        self._address = None
        entity_map[self._name] = self

    def name (self):
        return self._name

    def symbol_string(self):
        return self._name

    def is_defined(self):
        return

    def is_initialized(self):
        return

    def is_constant(self):
        return False

    def value(self):
        raise Exception ("Entity#_value")

    def is_parameter(self):
        return False

    def is_private(self):
        return self._is_private

    def type(self):
        return self._type

    def alloc_size(self):
        return self.type().alloc_size()

    def alignment(self):
        return self.type().alignment()

    def refered(self):
        self.n_refered += 1

    def is_refered(self):
        return self.n_refered > 0

    def mem_ref (self):
        self._check_address()
        return self._mem_ref

    def set_mem_ref(self, mem):
        self._mem_ref = mem

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
            raise Exception ("_address did not resolved: " + self._name)

    def location (self):
        return self._type.location()

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
        self.__value = int(value)

    def is_assignable (self):
        return False

    def is_defined(self):
        return True

    def is_initialized(self):
        return True

    def is_constant(self):
        return True

    def value(self):
        return self.__value

    def _dump(self, d):
        d.print_member ("_name", self._name)
        d.print_member ("_type", self._type)
        d.print_member ("_value", self.value)

    def accept(self, visitor):
        return visitor.visit()


class Function (Entity):
    def __init__(self, priv, t, name):
        super(Function, self).__init__(priv, t, name)
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

    def set_calling_symbol (self, sym):
        if self._calling_symbol:
            raise Exception ("must not happen: Function#callingSymbol was set again")
        self._calling_symbol = sym

    def calling_symbol (self):
        if not self._calling_symbol:
            raise Exception  ("must not happen: Function#callingSymbol was set again")
        return self._calling_symbol

    def label (self):
        if self._label:
            return self._label
        else:
            self._label = Label (self._calling_symbol())
            return self._label


class DefinedFuntion (Function):
    def __init__(self, priv, type, name, params, body, scope):
        super(DefinedFuntion, self).__init__(priv, type, name)
        self._params = Params (loc = 0, param_descs = params)
        self._body = body
        self._scope = scope
        self._ir = list()
        for i in self._body:
            self._ir.append(backend.ir.ir.inst_factory(i))


    def is_defined(self):
        return True

    def parameters(self):
        return self._params

    def body(self):
        return self._body

    def ir (self):
        return self._ir

    def lvar_scope (self):
        return self._scope

    #
    # Returns function local variables
    # Does NOT include parameters
    # Does NOT include static local variables

    def local_variables (self):
        return self._scope.all_local_variables()

    def _dump(self, d):
        d.print_member ("name", self._name)
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
        d.print_member("_name", self._name)
        d.print_member("_is_private", self.is_private())
        d.print_member("_type", self._type)
        d.print_member("params", self._params)

    def accept(self, visitor):
        return visitor.visit()

class Variable (Entity):
    def __init__(self, priv, type, name):
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
        d.print_member("_name", self._name)
        d.print_member("_is_private", self.is_private())
        d.print_member("_type", self._type)

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
        return DefinedVariable (False, backend.type.type.Type.type_factory(t, obj = None), "@tmp" + str(cls.tmp_seq), None)

    def is_defined(self):
        return True

    def set_sequence (self, seq):
        self._sequence = seq

    def symbol_string(self):
        if self._sequence < 0:
            return self._name
        else:
            return self._name + "." + str(self._sequence)

    def has_initializer(self):
        return self._initializer != None

    def is_initialized(self):
        return self.has_initializer()

    def initializer (self):
        return self._initializer

    def set_initializer (self, expr):
        self._initializer = expr

    def set_ir (self, expr):
        self._ir = expr

    def ir(self):
        return self._ir

    def _dump(self, d):
        d.print_member("_name", self._name)
        d.print_member("_is_private", self.is_private())
        d.print_member("_type", self._type)
        d.print_member("initializer", self.initializer)

    def accept(self, visitor):
        return visitor.visit()


class Parameter (DefinedVariable):
    def __init__(self, type, name):
        super(Parameter, self).__init__(False, type, name, None)

    def is_parameter(self):
        return True

    def _dump(self, d):
        d.print_member ("_name", self._name)
        d.print_member ("_type", self._type)


class ParamSlot (object):
    def __init__(self, loc, param_descs, var_arg):
        self._location = loc
        self._param_descriptors = list()
        for i in param_descs:
            self._param_descriptors.append(Parameter(name = i["name"], type = i["type"]))
        self._var_arg = var_arg

    def argc (self):
        if self._var_arg:
            raise Exception ("must not happen: Param#argc for var_arg")
        return len (self._param_descriptors)

    def min_argc(self):
        return len (self._param_descriptors)

    def accept_varargs(self):
        self._var_arg = True

    def is_vararg(self):
        return self._var_arg

    def location(self):
        return self._location


class Params (ParamSlot):
    def __init__(self, loc, param_descs):
        super(Params, self).__init__(loc, param_descs, False)

    def parameters(self):
        return self._param_descriptors

    def parameters_type_ref (self):
        type_refs = []
        for param in self._param_descriptors:
            type_refs.append(param.type_node().type_ref())
        return ParamTypeRefs (self.location, type_refs, self._var_arg)

    def __eq__ (self, other):
        if not isinstance(other, Params):
            return False
        else:
            return other._var_arg == self._var_arg  and other._param_descriptors == self._param_descriptors

    def dump(self, d):
        d.print_node_list ("parameters", self.parameters)