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
        self.register = reg

    def collect_statistics(self, stats):
        self.register.collect_statistics (stats)

    def to_source (self, table):
        return "*" + self.register.to_source (table)

    def dump (self):
        return "AbsoluteAddress " + self.register.dump() + ")"


class ImmediateValue (Operand):
    def __init__ (self, expr):
        if isinstance(expr, int):
            self.expr = IntegerLiteral (expr)
        elif isinstance (expr, Literal):
            self.expr = expr

    def __eq__(self, other):
        if not isinstance (other, ImmediateValue):
            return False
        else:
            return self.expr == other.expr

    def collect_statistics (self, stats):
        return

    def to_source(self, table):
        return "$" + self.expr.to_source (table)

    def dump (self):
        return "(ImmediateValue " + self.expr.dump() + ")"


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
        if isinstance(offset, IntegerLiteral):
            self.offset = offset
        else:
            self.offset = IntegerLiteral(offset)
        self.base = base
        self.fixed = fixed

    @staticmethod
    def reloca_table (offset, base):
        return IndirectMemoryReference (offset, base , False)

    def fix_offset(self, diff):
        if self.fixed:
            raise Exception("must not happen: fixed = True")
        curr = self.offset.value
        self.offset = IntegerLiteral (curr + diff)
        self.fixed = True

    def collect_statistics(self, stats):
        return self.base.collect_statistics (stats)

    def __str__ (self):
        return self.to_source (dummy)

    def to_source (self, table):
        if not self.fixed:
            raise Exception ("must not happen: writing unfixed variable")
        if self.offset.is_zero ():
            return ""
        else:
            return self.offset.to_source (table) + "(" + self.base.to_source (table) + ")"
            
    def compare_to (self, mem):
        return self.cmp (mem)

    def cmp (self, mem):
        if isinstance (mem, DirectMemoryReference):
            return -1
        elif isinstance(mem, IndirectMemoryReference):
            return self.offset.compare_to (mem.offset)

    def dump (self):
        str = "(IndirectMemoryReference "
        if self.fixed:
            str += ""
        else:
            str += "*"
        str = str +self.offset.dump() + " " + self.base.dump() + ")"
        return str

class DirectMemoryReference (MemoryReference):
    def __init__ (self, val):
        super().__init__()
        if isinstance(val, IntegerLiteral):
            self.value = val
        else:
            self.value = IntegerLiteral(val)

    def collect_statistics(self, stats):
        self.value.collect_statistics (stats)

    def fix_offset(self, diff):
        raise Exception ("DirectMemoryReference#fixoffset")

    def __str__ (self):
        return self.to_source (dummy)

    def to_source (self, table):
        return self.value.to_source (table)

    def compare_to (self, mem):
        return self.cmp (mem)

    def cmp (self, mem):
        if isinstance (mem, IndirectMemoryReference):
            return 1
        elif isinstance (mem, DirectMemoryReference):
            return self.value.compare_to (mem.value)

    def dump (self):
        return "(DirectMemoryReference " + self.value.dump () + ")"


