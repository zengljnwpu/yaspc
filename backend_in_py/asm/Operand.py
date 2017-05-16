from asm import *

class Operand ():
    def __init__ (self):
        return;
    def to_source (self, table):
        return;
    def dump (self):
        return;
    def is_register (self):
        return False;
    def is_memory_reference (self):
        return False;
    def integer_literal (self):
        return None;
    def collect_statistics (self, stats):
        return;
    def __eq__ (self, operand):
        return False;
    def match (self, operand):
        return operand == self;

class ImmediateValue (Operand):
    def __init__ (self, n: int):
        self.__expr = IntegerLiteral (n);

    def __eq__(self, other):
        result = isinstance (other, ImmediateValue);
        if result == False:
                return False;
        imm = ImmediateValue (other);
        return self.__expr == other.__expr;
    def expr (self):
        return self.__expr;
    def collect_statistics (self, stats):
        return;
    def to_source(self, table):
        return "$" + self.__expr.to_source (table);
    def dump (self):
        return "(ImmediateValue " + self.__expr.dump() + ")";

class MemoryReference (Operand):
    def __init__ (self):
        super().__init__();
    def is_memory_reference(self):
        return True;
    def fix_offset (self, diff):
        return;
    def cmp (self, mem):
        return;

class IndirectMemoryReference (MemoryReference):
    def __init__(self, offset, base, fixed = True):
        self.__offset = IntegerLiteral (offset);
        self.__base = Register (base);
        self.__fixed = fixed;

    @staticmethod
    def reloca_table (offset, base):
        return IndirectMemoryReference (IntegerLiteral (offset), base ,False);
    
    def offset(self):
        return self.__offset;

    def fix_offset(self, diff):
        if self.__fixed:
            raise AttributeError;
        curr = IntegerLiteral (offset).value;
        self.__offset = IntegerLiteral (curr + diff);
        self.__fixed = True;

    def base(self):
        return self.__base;

    def collect_statistics(self, stats):
        return self.__base.collect_statistics (stats);

    def to_string (self):
        return to_source (SymbolTable.dummy ());

    def to_source (self, table):
        if self.__fixed == False:
            raise Exception;
        if self.__offset.is_zero ():
            return "";
        else:
            return self.__offset.to_source (table) + "(" + self.__base.to_source (table) + ")";
            
    def compare_to (self, mem):
        return - (mem.__cmp (self));

    def __cmp (self, mem):
        if isinstance (mem, DirectMemoryReference):
            return -1;
        elif isinstance(mem, IndirectMemoryReference):
            return self.__offset.compare_to (mem.__offset);
        else:
            raise ArithmeticError;

    def dump (self):
        str = "(IndirectMemoryReference ";
        if self.__fixed:
            str += "";
        else:
            str += "*";
        str = str +self.__offset.dump() + " " + self.__base.dump() + ")";

class DirectMemoryReference (MemoryReference):
    def __init__ (self, val):
        self.__value = val;
    def value (self):
        return self.__value;
    def collect_statistics(self, stats):
        self.__value.collect_statistics (stats);
    def fix_offset(self, diff):
        raise Exception;
    def to_string (self):
        return to_source (SymbolTable.dummp());
    def to_source (self, table):
        return self.__value.to_source (table);
    def compare_to (self, mem):
        return -(mem.cmp (self));
    def cmp (self, mem):
        if isinstance (mem, IndirectMemoryReference):
            return 1;
        elif isinstance (mem, DirectMemoryReference):
            return self.__value.compare_to (mem.__value);
        else:
            raise BaseException;
    def dump (self):
        return "(DirectMemoryReference " + self.__value.dump () + ")";


class Register (Operand):
    def is_register(self):
        return True;
    def collect_statistics(self, stats):
        return stats.register_used (self);
    def to_source(self, table):
        return super().to_source(table);
    def dump(self):
        return super().dump();

class AbsoluteAddress (Operand):
    def __init__(self, reg):
        super().__init__();
        self.__register = reg;

    def register(self):
        return self.__register;

    def collect_statistics(self, stats):
        self.__register.collect_statistics (stats);

    def to_source (self, table):
        return "*" + self.__register.to_source (table);

    def dump (self):
        return "AbsoluteAddress " + self.__register.dump() + ")";