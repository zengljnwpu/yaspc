from backend_in_py.asm.symbol_table import *


class Operand (object):
    def to_source (self, table):
        return

    def dump (self):
        return

    def is_register (self):
        return False

    def is_memory_reference (self):
        return False

    def integer_literal (self):
        return None

    def collect_statistics (self, stats):
        return

    def match (self, operand):
        return False


class Register (Operand):
    def is_register(self):
        return True

    def collect_statistics(self, stats):
        return stats.register_used (self)

    def to_source(self, table):
        return ""

    def dump(self):
        return ""


class AbsoluteAddress (Operand):
    def __init__(self, reg):
        super().__init__()
        self._register = reg

    def register(self):
        return self._register

    def collect_statistics(self, stats):
        self._register.collect_statistics (stats)

    def to_source (self, table):
        return "*" + self._register.to_source (table)

    def dump (self):
        return "AbsoluteAddress " + self._register.dump() + ")"


class ImmediateValue (Operand):
    def __init__ (self, expr):
        self._expr = None
        if isinstance(expr, int):
            self._expr = IntegerLiteral (expr)
        elif isinstance (expr, Literal):
            self._expr = expr

    def expr (self):
        return self._expr

    def __eq__(self, other):
        if not isinstance (other, ImmediateValue):
            return False
        else:
            return self._expr == other._expr

    def collect_statistics (self, stats):
        return

    def to_source(self, table):
        return "$" + self._expr.to_source (table)

    def dump (self):
        return "(ImmediateValue " + self._expr.dump() + ")"


class MemoryReference (Operand):
    def is_memory_reference(self):
        return True

    def fix_offset (self, diff):
        return

    def cmp (self, mem):
        return


class IndirectMemoryReference (MemoryReference):
    def __init__(self, offset: int, base: Register, fixed = True):
        super().__init__()
        self._offset = None
        if isinstance(offset, IntegerLiteral):
            self._offset = offset
        else:
            self._offset = IntegerLiteral(offset)
        self._base = base
        self._fixed = fixed

    @staticmethod
    def reloca_table (offset, base):
        return IndirectMemoryReference (offset, base , False)

    def fix_offset(self, diff):
        if self._fixed:
            raise Exception("must not happen: fixed = True")
        curr = IntegerLiteral (self._offset).value()

        self._offset = IntegerLiteral (curr + diff)
        self._fixed = True

    def collect_statistics(self, stats):
        return self._base.collect_statistics (stats)

    def __str__ (self):
        return self.to_source (dummy)

    def to_source (self, table):
        if not self._fixed:
            raise Exception ("must not happen: writing unfixed variable")
        if self._offset.is_zero ():
            return ""
        else:
            return self._offset.to_source (table) + "(" + self._base.to_source (table) + ")"
            
    def compare_to (self, mem):
        return self.cmp (mem)

    def cmp (self, mem):
        if isinstance (mem, DirectMemoryReference):
            return -1
        elif isinstance(mem, IndirectMemoryReference):
            return self._offset.compare_to (mem._offset)

    def dump (self):
        str = "(IndirectMemoryReference "
        if self._fixed:
            str += ""
        else:
            str += "*"
        str = str +self._offset.dump() + " " + self._base.dump() + ")"
        return str


class DirectMemoryReference (MemoryReference):
    def __init__ (self, val: Literal):
        super().__init__()
        self._value = val

    def value(self):
        return self._value

    def collect_statistics(self, stats):
        self._value.collect_statistics (stats)

    def fix_offset(self, diff):
        raise Exception ("DirectMemoryReference#fixoffset")

    def __str__ (self):
        return self.to_source (dummy)

    def to_source (self, table):
        return self._value.to_source (table)

    def compare_to (self, mem):
        return self.cmp (mem)

    def cmp (self, mem):
        if isinstance (mem, IndirectMemoryReference):
            return 1
        elif isinstance (mem, DirectMemoryReference):
            return self._value.cmp (mem._value)

    def dump (self):
        return "(DirectMemoryReference " + self._value.dump () + ")"


