from backend_in_py.asm.SymbolTable import *


class Operand ():
    def to_source (self, table):
        return

    def dump (self):
        return

    def __eq (self):
        return False

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


class ImmediateValue (Operand):
    def __init__ (self, expr):
        if isinstance(expr, int):
            self.expr = IntegerLiteral (expr)
        else:
            self.expr = expr

    def __eq__(self, other):
        if not isinstance (other, ImmediateValue):
            return False
        imm = ImmediateValue (other)
        return self.expr == imm.expr

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
    def __init__(self, offset, base, fixed = True):
        super().__init__()
        if isinstance(offset, int):
            self.offset = IntegerLiteral (offset)
        else:
            self.offset = offset
        self.base = base
        self.fixed = fixed

    @staticmethod
    def reloca_table (cls, offset, base):
        return IndirectMemoryReference (IntegerLiteral (offset), base , False)

    def fix_offset(self, diff):
        if self.fixed:
            raise Exception("must not happen: fixed = True")
        curr = IntegerLiteral (self.offset).value
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
        return -(mem.cmp (self))

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
        self.value = val

    def collect_statistics(self, stats):
        self.value.collect_statistics (stats)

    def fix_offset(self, diff):
        raise Exception ("DirectMemoryReference#fixoffset")

    def __str__ (self):
        return self.to_source (dummy)

    def to_source (self, table):
        return self.value.to_source (table)

    def compare_to (self, mem):
        return -(mem.cmp (self))

    def cmp (self, mem):
        if isinstance (mem, IndirectMemoryReference):
            return 1
        elif isinstance (mem, DirectMemoryReference):
            return self.value.compare_to (mem.value)

    def dump (self):
        return "(DirectMemoryReference " + self.value.dump () + ")"


class Register (Operand):
    def is_register(self):
        return True

    def collect_statistics(self, stats):
        return stats.register_used (self)

    def to_source(self, table):
        return

    def dump(self):
        return

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