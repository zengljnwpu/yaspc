from backend_in_py.asm.Literal import *
from backend_in_py.asm.Operand import *

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
        if sym:
            self.symbol = sym
        else:
            self.symbol = UnnamedSymbol()

    def is_label(self):
        return True

    def dump (self):
        return "(Label " + self.symbol.dump() + ")"

    def to_source(self, table):
        return self.symbol.to_source (table) + ":"

class Instruction (Assembly):
    def __init__ (self, mnemonic, suffix = None, a1 = None, a2 = None, reloc = None):
        self.mnemonic = mnemonic
        self.operands = []
        if suffix:
            self.suffix = suffix
        else:
            self.suffix = ""
        if a1:
            self.operands.append(a1)
        if a2:
            self.operands.append(a2)
        if reloc:
            self.need_relocation = reloc
        else:
            self.need_relocation = False
    
    def build (self, mnemonic, o1, o2 = None):
        if not o2:
            return Instruction (mnemonic= mnemonic, suffix = self.suffix, a1 = o1, reloc = self.need_relocation)
        else:
            return Instruction (mnemonic = mnemonic, suffix = self.suffix,a1 = o1, a2 = o2, reloc = self.need_relocation)

    def is_instruction(self):
        return True

    def is_jump_instruction (self):
        list = ("jump", "jz", "jne", "je", "jne")
        return self.mnemonic in list

    def num_operands (self):
        return len (self.operands)

    def operand1 (self):
        return self.operands[0]

    def operand2 (self):
        return self.operands[1]

    #Extract jump destination label from operands
    def jmp_destination (self):
        ref = DirectMemoryReference (self.operands[0])
        return Symbol (ref.value)

    def collect_statistics (self, stats):
        stats.instruction_ussed (self.mnemonic)
        for i in self.operands:
            i.collect_statistics (stats)

    def to_source (self, table):
        buf = ""
        buf = buf + "\t"
        buf = buf + self.mnemonic + self.suffix
        sep = "\t"
        for i in self.operands:
            buf = buf + sep
            sep = ", "
            buf = buf + i.to_source (table)
        return buf

    def _str__(self):
        return "#<Insn" + self.mnemonic + ">"

    def dump(self):
        buf = ""
        buf = buf + "(Instruction " + self.mnemonic + " " + self.suffix
        for i in self.operands:
            buf = buf + " " + i.dump()
        buf = buf + ")"
        return buf

class Directive (Assembly):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def is_directive(self):
        return True

    def to_source(self, table):
        return self.content

    def dump(self):
        return "(Directive " + self.content.strip() + ")"

class Comment (Assembly):
    def __init__(self, string, indent_level = 0):
        super().__init__()
        self.string = string
        self.indent_level = indent_level

    def is_comment(self):
        return True

    def to_source (self, table):
        return "\t" + self.indent() + "# " + self.string

    def indent (self):
        buf = ""
        for i in range (self.indent_level):
            buf = buf + "  "
        return buf

    def dump(self):
        return "Comment "+ self.string + ")"
