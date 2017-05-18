class Assembly ():
    def __init__ (self):
        return

    def to_source (self, table):
        return

    def dump(self):
        return

    def is_instruction(self):
        return False;

    def is_label (self):
        return False;

    def is_directive (self):
        return ;

    def is_comment (self):
        return False;

    def collect_statistics (self):
        return;

class Label (Assembly):
    def __init__ (self):
        super().__init__();
        self.symbol;

    def __init__ (self, sym):
        super().__init__();
        self.symbol = sym;

    def symbol(self):
        return self.symbol;

    def is_label(self):
        return True;

    def to_source(self, table):
        return self.symbol.to_source (table) + ":";

class Instruction (Assembly):
    def __init__(self, mnemonic):
        super().__init__();
        self.mnemonic = mnemonic;
        self.suffix = "";
        self.operands = [];
        self.need_relocation = False;

    def __init__ (self, mnemonic, suffix, a1, reloc):
        super().__init__();
        self.mnemonic = mnemonic;
        self.suffix = suffix;
        self.operands = [];
        self.operands.append (a1);
        self.need_relocation = reloc;

    def __init__ (self, mnemonic, suffix, a1):
        super().__init__();
        self.mnemonic = mnemonic;
        self.suffix = suffix;
        self.operands = [];
        self.operands.append (a1);
        self.need_relocation = False;

    def __init__ (self, mnemonic, suffix, a1, a2, reloc = False):
        super().__init__();
        self.mnemonic = mnemonic;
        self.suffix = suffix;
        self.operands = [];
        self.operands.append (a1);
        self.operands.append (a2);
        self.need_relocation = False;

    def __init__ (self, mnemonic, suffix, operands, reloc):
        super().__init__();
        self.mnemonic = mnemonic;
        self.suffix = suffix;
        self.operands = operands;
        self.need_relocation = reloc;

    def build (self, mnemonic, o1):
        return Instruction (mnemonic = mnemonic,suffix = self.suffix, a1 = o1, reloc = self.need_relocation);
    
    def build (self, mnemonic, o1, o2):
        return Instruction (mnemonic = mnemonic, suffix = self.suffix, a1 = o1,  a2 = o2, reloc = self.need_relocation);

    def is_instruction(self):
        return True;

    def mnemonic(self):
        return self.mnemonic;

    def is_jump_instruction (self):
        list = ("jump", "jz", "jne", "je", "jne");
        return self.mnemonic in list;

    def num_operands (self):
        return len (self.operands);

    def operand1 (self):
        return self.operands[0];

    def operrand2 (self):
        return self.operands[1];
    
    def jmp_destination (self):
        ref = DirectMemoryReference (self.operands[0]);
        return Symbol (ref.value());

    def collect_statistics (self, stats):
        stats.instruction_ussed (self.mnemonic);
        for i in len (self.operands):
            self.operands[i].collect_statistics (stats);

    def to_source (self, table):
        buf = "";
        buf = buf + "\t";
        buf = buf + self.mnemonic + self.suffix;
        sep = "\t";
        for i in len (self.operands):
            buf = buf + sep;
            sep = ", ";
            buf = buf + self.operands[i].to_source (table);
        return buf;

    def to_string (self):
        return "#<Insn" + self.mnemonic + ">";

    def dump(self):
        buf = "";
        buf = buf + "(Instruction " + self.mnemonic + " " + self.suffix;
        for i in self.operands:
            buf = buf + " " + i.dump();
        buf = buf + ")";
        return buf;

class Directive (Assembly):
    def __init__(self, content):
        super().__init__();
        self.content = "";
        self.content = content;

    def is_directive(self):
        return True;

    def to_source(self, table):
        return self.content;

    def dump(self):
        return "(Directive " + self.content.strip() + ")";

class Comment (Assembly):
    def __init__(self, string):
        super().__init__();
        self.string = "";
        self.indent_level = 0;
        self.string = string;

    def __init__(self, string, indent_level):
        super().__init__();
        self.string = "";
        self.indent_level = 0;
        self.string = string;
        self.indent_level = indent_level;

    def is_comment(self):
        return True;

    def to_source (self, table):
        return "\t" + self.indent() + "# " + self.string;

    def indent (self):
        buf = "";
        for i in self.indent_level:
            buf = buf + "  ";
        return buf;

    def dump(self):
        return "Comment "+ self.string + ")";