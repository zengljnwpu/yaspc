
from backend.asm.literal import IntegerLiteral
from backend.entity.entity import entity_map
from backend.entity.entity import Function
from backend.entity.entity import ImmediateValue
from backend.ir.op import Op
import backend.type.type


class Expr(object):
    @staticmethod
    def expr_factory(value):
        if value["name"] == "value":
            return Int(type=value["type"], value=value["value"])
        elif value["name"] == "variable":
            return Var(type=value["type"], entity=entity_map[value["variable"]])
        elif value["name"] == "variable*":
            return Addr(type=value["type"], entity=entity_map[value["variable"]])

    def __init__(self, expr_type):
        self._type = backend.type.type.Type.type_factory(type=expr_type, obj=None)

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

    def address_node(self, expr_type):
        raise Exception("unexpected node for LHS: " + str(expr_type))

    def det_entity_force(self):
        return None

    def accept(self, visitor):
        return

    def dump(self, d):
        d.print_class(self)
        d.print_member("type", self._type)
        self._dump(self, d=d)

    def _dump(self, d):
        return


class Addr(Expr):
    def __init__(self, addr_type, entity):
        super(Addr, self).__init__(addr_type)
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
    def __init__(self, bin_type, op, left, right, value):
        super(Bin, self).__init__(bin_type)
        self._op = Op.op_factory(op)
        self._left = Expr.expr_factory(left)
        self._right = Expr.expr_factory(right)
        self._value = Expr.expr_factory(value)

    def left(self):
        return self._left

    def right(self):
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
    def __init__(self, call_type, expr, args):
        super(Call, self).__init__(call_type)
        self.__expr = Expr.expr_factory(expr)
        self.__args = list()
        for i in args:
            self.__args.append(Expr.expr_factory(i))

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
    def __init__(self, int_type, value):
        super(Int, self).__init__(int_type)
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
    def __init__(self, mem_type, expr):
        super(Mem, self).__init__(mem_type)
        self._expr = expr

    def expr(self):
        return self._expr

    def address_node(self, mem_type):
        return self._expr

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("__expr", self._expr)


class Str(Expr):
    def __init__(self, str_type, entry):
        super(Str, self).__init__(str_type)
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
    def __init__(self, uni_type, op, expr):
        super(Uni, self).__init__(uni_type)
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
    def __init__(self, var_type, entity):
        super(Var, self).__init__(var_type)
        self._entity = entity

    def is_var(self):
        return True

    def type(self):
        if (super(Var, self).type() == False):
            raise Exception("Var is too big to load by 1 insn\n")
        else:
            return super(Var, self).type()

    def name(self):
        return self._entity.name()

    def entity(self):
        return self._entity

    def address(self):
        return self._entity.address()

    def mem_ref(self):
        return self._entity.mem_ref()

    def address_node(self, var_type):
        return Addr(var_type, self._entity)

    def get_entity_force(self):
        return self._entity

    def accept(self, visitor):
        return visitor.visit(self)

    def _dump(self, d):
        d.print_member("entity", self._entity.name())
