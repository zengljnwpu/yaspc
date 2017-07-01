from backend_in_py.asm.operand import *
from backend_in_py.entity.entity import *
from backend_in_py.asm.type import *
from backend_in_py.ir.dumper import *
from backend_in_py.ir.op import *
import backend_in_py.type.type

class Expr():
    @staticmethod
    def expr_factory(value):
        if value["name"] == "value":
            return Int(type=value["type"], value=value["value"])
        elif value["name"] == "variable":
            return Var(type=value["type"], entity = entity_map[value["variable"]])
        elif value["name"] == "variable*":
            return Addr(type=value["type"], entity = entity_map[value["variable"]])

    def __init__(self, type):
        self._type = backend_in_py.type.type.Type.type_factory(type = type, obj = None)

    def type(self):
        return self._type

    def is_var(self):
        return False

    def is_addr(self):
        return False

    def is_constant(self):
        return False

    def asm_value(self):
        raise Exception("__expr#asm_value called")

    def address(self):
        raise Exception("__expr#_address called\n")

    def mem_ref(self):
        raise Exception("__expr#memref called\n")

    def address_node(self, type: Type):
        raise Exception("unexpected node for LHS: " + str(type))

    def det_entity_force(self):
        return None

    def accept(self, visitor):
        return

    def dump(self, d: Dumper):
        d.print_class(self)
        d.print_member("type", self._type)
        self._dump(self, d=d)

    def _dump(self, d):
        return


class Addr(Expr):
    def __init__(self, type: Type, entity: Entity):
        super().__init__(type)
        self.entity = entity

    def is_addr(self):
        return True

    def entity(self):
        return self.entity

    def address(self):
        return self.entity.address()

    def mem_ref(self):
        return self.entity.mem_ref()

    def get_entity_force(self):
        return self.entity

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_entity", self.entity.name())


class Bin(Expr):
    def __init__(self, type: Type, op: str, left, right, value):
        super(Bin, self).__init__(type)
        self._op = Op.op_factory(op)
        self._left = Expr.expr_factory (left)
        self._right = Expr.expr_factory (right)
        self._value = Expr.expr_factory (value)

    def left(self):
        return self._left

    def right (self):
        return self._right

    def value(self):
        return self._value

    def op(self):
        return self._op

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_op", self._op.to_string())
        d.print_member("_left", self._left)
        d.print_member("_right", self._right)


class Call(Expr):
    def __init__(self, type: Type, expr, args:list):
        super(Call, self).__init__(type)
        self.__expr = expr
        self.__args = args

    def expr(self):
        return self.__expr

    def args(self):
        return self.__args

    def num_args(self):
        return len(self.__args)

    # return True is this funcall is NOT a function pointer call
    def is_static_call(self):
        return isinstance(self.__expr.get_entity_force(), Function)

    # Return a funciton object which is refered by expression
    def function(self):
        ent = self.__expr.get_entity_force()
        if not ent:
            raise Exception("not a static funcall")
        else:
            return ent

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_expr", self.__expr)
        d.print_members("args", self.__args)


class Int(Expr):
    def __init__(self, type, value):
        super(Int, self).__init__(type)
        self._value = value

    def value(self):
        return self._value

    def is_constant(self):
        return True

    def asm_value(self):
        return ImmediateValue(IntegerLiteral(self._value))

    def mem_ref(self):
        raise Exception("must not happen: IntValue#memref")

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_value", self._value)


class Mem(Expr):
    def __init__(self, type, expr):
        super(Mem, self).__init__(type)
        self._expr = expr

    def expr(self):
        return self._expr

    def address_node(self, type):
        return self._expr

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("__expr", self._expr)


class Str(Expr):
    def __init__(self, type, entry):
        super(Str, self).__init__(type)
        self._entry = entry

    def entry(self):
        return self._entry

    def symbol(self):
        return self._entry.symbol

    def is_constant(self):
        return True

    def mem_ref(self):
        return self._entry.mem_ref

    def address(self):
        return self._entry.address

    def asm_value(self):
        return self._entry.address

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_entry", self._entry)


class Uni(Expr):
    def __init__(self, type, op, expr):
        super(Uni, self).__init__(type)
        self._op = op
        self._expr = expr

    def expr(self):
        return self.expr

    def op(self):
        return self._op

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("_op", self._op)
        d.print_member("_expr", self._expr)


class Var(Expr):
    def __init__(self, type, entity):
        super(Var, self).__init__(type)
        self._entity = entity

    def is_var(self):
        return True

    def type(self):
        if (super().type() == False):
            raise Exception("Var is too big to load by 1 insn\n")
        else:
            return super().type()

    def name(self):
        return self._entity.name()

    def entity(self):
        return self._entity

    def address(self):
        return self._entity.address()

    def mem_ref(self):
        return self._entity.mem_ref()

    def address_node(self, type):
        return Addr(type, self._entity)

    def get_entity_force(self):
        return self._entity

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member ("entity", self._entity.name())