from backend_in_py.asm.literal import *
from backend_in_py.asm.operand import *


class Assembly ():
    def to_source (self, table):
        return

    def dump(self):
        return

    def is_instruction(self):
        return False

    def is_label (self):
        return False

    def is_directive (self):
        return False

    def is_comment (self):
        return False

    def collect_statistics (self, stats):
        return


class Label (Assembly):
    def __init__ (self, sym = None):
        super().__init__()
        self._symbol = None
        if sym:
            self._symbol = sym
        else:
            self._symbol = UnnamedSymbol()

    def symbol(self):
        return self._symbol

    def is_label(self):
        return True

    def dump (self):
        return "(Label " + self._symbol.dump() + ")"

    def to_source(self, table ):
        return self._symbol.to_source (table) + ":"


class Instruction (Assembly):
    def __init__ (self, mnemonic: str, suffix:str = None, a1:Operand = None, a2:Operand = None, reloc:bool = None):
        self._mnemonic = mnemonic
        self._operands = []
        if suffix:
            self._suffix = suffix
        else:
            self._suffix = ""
        if a1:
            self._operands.append(a1)
        if a2:
            self._operands.append(a2)
        if reloc:
            self._need_relocation = reloc
        else:
            self._need_relocation = False
    
    def build (self, mnemonic:str, o1:Operand, o2:Operand = None):
        if not o2:
            return Instruction (mnemonic= mnemonic, suffix = self._suffix, a1 = o1, reloc = self._need_relocation)
        else:
            return Instruction (mnemonic = mnemonic, suffix = self._suffix, a1 = o1, a2 = o2, reloc = self._need_relocation)

    def is_instruction(self):
        return True

    def mnemonic(self):
        return self._mnemonic

    def is_jump_instruction (self):
        list = ("jmp", "jz", "jne", "je", "jne")
        return self._mnemonic in list

    def num_operands (self):
        return len (self._operands)

    def operand1 (self):
        return self._operands[0]

    def operand2 (self):
        return self._operands[1]

    #Extract jump destination _label from operands
    def jmp_destination (self):
        ref = DirectMemoryReference (self._operands[0])
        return ref.value()

    def collect_statistics (self, stats):
        stats.instruction_used (self._mnemonic)
        for i in self._operands:
            i.collect_statistics (stats)

    def to_source (self, table):
        buf = ""
        buf = buf + "\t"
        buf = buf + self._mnemonic + self._suffix
        sep = "\t"
        for i in self._operands:
            buf += sep
            sep = ", "
            buf += i.to_source (table)
        return buf

    def __str__(self):
        return "#<Insn " + self._mnemonic + ">"

    def dump(self):
        buf = ""
        buf = buf + "(Instruction " + self._mnemonic + " " + self._suffix
        for i in self._operands:
            buf = buf + " " + i.dump()
        buf = buf + ")"
        return buf


class Directive (Assembly):
    def __init__(self, content: str):
        super().__init__()
        self._content = content

    def is_directive(self):
        return True

    def to_source(self, table):
        return self._content

    def dump(self):
        return "(Directive " + self._content.strip() + ")"


class Comment (Assembly):
    def __init__(self, string, indent_level = 0):
        super().__init__()
        self._string = string
        self._indent_level = indent_level

    def is_comment(self):
        return True

    def to_source (self, table):
        return "\t" + self.indent() + "# " + self._string

    def indent (self):
        buf = ""
        for i in range (self._indent_level):
            buf = buf + "  "
        return buf

    def dump(self):
        return "(Comment "+ self._string + ")"
