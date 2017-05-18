class AssemblyCode():
    def __init__(self, natural_type = Type(), stack_wordsize = 0, label_Symbols = SymbolTable(), verbose = False):
        self.__natural_type = natural_type;
        self.__stack_wordsize = stack_wordsize;
        self.__label_symbols = label_Symbols;
        self.__verbose = verbose;
        self.__virtual_stack = VirtualStack();
        self.__assemblies = [];
        self.__comment_indent_level = 0;
        self.__statistics = Statistics ();

    def assemblies(self):
        return self.__assemblies;

    def add_all (self, assemblies):
        return self.__assemblies.add_all (assemblies);

    def to_source (self):
        buf = "";
        for asm in self.__assemblies:
            buf+= asm.to_source (self.__label_symbols);
            buf+= "\n";
        return buf;

    def dump (self):
        for asm in self.__assemblies:
            print (asm.dump());

    def apply (self, opt):
        #optmization;
        return;

    def __statistics (self):
        if self.__statistics == None:
            self.__statistics = Statistics.collect(self.__assemblies);
        return self.__statistics;

    def does_uses (self, reg):
        return self.__statistics ().does_register_used (reg);

    def comment (self, str):
        self.__assemblies.append (Comment (str, self.__comment_indent_level));

    def indent_comment (self):
        self.__comment_indent_level += 1;

    def unindent_comment (self):
        self.__comment_indent_level -= 1;

    def label (self, sym):
        if isinstance(sym, Symbol):
            self.__assemblies.append(Label (sym));
        else:
            self.__assemblies.append(label);

    def reduce_label (self):
        stats = self.__statistics();
        result = [];
        for asm in self.__assemblies:
            if (asm.is_label ()) and (not (stats.does_symbol_used (Label(asm)))):
                continue;
            else:
                result.append(asm);
        self.__assemblies = result;

    def __directive (self, direc):
        self.__assemblies.append(Directive(direc));

    def __insn (self, *op):
       ## self.__assemblies.append(Instruction (op));
        return;

    def __type_suffix (self, *type):
        ##
        return;

    #directives
    def _file (self, name):
        self.__directive(".file\t" + name);

    def _text (self):
        self.__directive("\t.text");

    def _data (self):
        self.__directive("\t.data");

    def _section (self, name, flag = "", type = "", group = "", linkage = ""):
        #self.__directive("\t.section\t", name);
        return;

    def _globl (self, sym):
        self.__directive(".globl " + sym.name());

    def _local (self, sym):
        self.__directive(".local " + sym.name());

    def _hidden (self, sym):
        self.__directive("\t.hidden\t", sym.name());

    def _comm (self, sym, size, alignment):
        self.__directive("\t.comm\t" + sym.name() + "," + str (size) + "," + str (alignment));

    def _align (self, n):
        self.__directive("\t.align\t" + str (n));

    def _type (self, sym, type):
        self.__directive("\t.type\t" + sym.name() + "," + type);

    def _size (self, sym, size):
        self.__directive("\t.size\t" + sym.name() + "," + str (size));

    def _byte (self, val):
        self.__directive(".byte\t" + IntegerLiteral ((val).to_source()));

    def _value(self, val):
        self.__directive(".value\t" + IntegerLiteral((val).to_source()));

    def _long(self, val):
        self.__directive(".long\t" + IntegerLiteral((val).to_source()));

    def _quad(self, val):
        self.__directive(".quad\t" + IntegerLiteral((val).to_source()));

    def _string(self, str):
        self.__directive("\t.string\t" + str);

    def virtual_push(self, reg):
        if self.__verbose:
            self.comment("push" + reg.base_name() + " -> " + self.__virtual_stack.top());
        else:
            self.mov (self.__virtual_stack.top(), reg);
            self.__virtual_stack.rewind(self.__stack_wordsize);

    def jmp (self, label):
        self.__insn("jmp", DirectMemoryReference (label.symbol()));
    def jne (self, label):
        self.__insn("jnz", DirectMemoryReference (label.symbol()));
    def je (self, label):
        self.__insn("je", DirectMemoryReference (label.symbol()));
    def cmp (self, a, b):
        self.__insn(b.type, "cmp", a, b);
    def sete (self, reg):
        self.__insn("sete", reg);
    def setne (self, reg):
        self.__insn("setne", reg);
    def seta (self, reg):
        self.__insn("seta", reg);
    def setae (self, reg):
        self.__insn("setae", reg);
    def setb (self, reg):
        self.__insn("setb", reg);
    def setbe (self, reg):
        self.__insn("setbe", reg);
    def setg (self, reg):
        self.__insn("setg", reg);
    def setge (self, reg):
        self.__insn("setge", reg);
    def setl (self, reg):
        self.__insn("setl", reg);
    def setle (self, reg):
        self.__insn("setle", reg);
    def test (self, a, b):
        self.__insn(b.type, "test", a, b);
    def push (self, reg):
        self.__insn("push", self.__type_suffix(self.__natural_type), reg);
    def pop (self, reg):
        self.__insn("pop", self.__type_suffix(self.__natural_type), reg);
    #call function by relative address
    def call (self, sym):
        self.__insn("call", DirectMemoryReference (sym));
    #call funciton byabsolute address
    def call_absolute (self, reg):
        self.__insn("call", AbsoluteAddress (reg));
    def ret (self):
        self.__insn("ret");
    def mov (self, src, dest):
        if isinstance(src, Register) and isinstance(dest, Register):
            type = self.__natural_type;
        elif isinstance(src, Operand) and isinstance(dest, Register):
            type = dest.type;
        elif isinstance(src, Register) and isinstance( dest, Operand):
            type = src.type;
        self.__insn(type, "mov", src, dest);
    #for stack access
    def reloca_table_mov (self, src, dest):
        self.__assemblies.append(Insruction ("mov", self.__type_suffix(self.__natural_type), src, dest, True));
    def movsx (self, src, dest):
        self.__insn( "movs", self.__type_suffix(src.type, dest.type), src, dest)
    def movzx (self, src, dest):
        self.__insn( "movz", self.__type_suffix(src.type, dest.type), src, dest)
    def movzb (self, src, dest):
        self.__insn( "movz", "b" + str (self.__type_suffix(src.type, dest.type)), src, dest)
    def lea (self, src, dest):
        self.__insn(self.__natural_type, "lea", src, dest);
    def neg (self, reg):
        self.__insn(reg.type, "neg", reg);
    def add (self, diff, base):
        self.__insn(base.type, "add", diff, base);
    def sub (self, diff, base):
        self.__insn(base.type, "sub", diff, base);
    def imul (self, m, base):
        self.__insn(base.type, "imul", m, base);
    def cltd (self):
        self.__insn("cltd");
    def div (self, base):
        self.__insn(base.type, "div", base);
    def idiv (self, base):
        self.__insn(base.type, "idiv", base);
    def _not (self, reg):
        self.__insn(reg.type, "not", reg);
    def _and (self, bits, base):
        self.__insn(base.type, "and", bits,base);
    def _or (self, bits, base):
        self.__insn(base.type, "or", bits,base);
    def _xor (self, bits, base):
        self.__insn(base.type, "xor", bits,base);
    def _sar (self, bits, base):
        self.__insn(base.type, "sar", bits,base);
    def _sal (self, bits, base):
        self.__insn(base.type, "sal", bits,base);
    def _shr (self, bits, base):
        self.__insn(base.type, "shr", bits,base);

#Virtual Stack
class VirtualStack ():
        def __init__ (self):
            self.__offset = 0;
            self.__max = 0;
            self.__mem_refs = [];
            self.reset();

        def reset (self):
            self.__offset = 0;
            self.__max = 0;
            self.__mem_refs.clear();

        def max_size(self):
            return self.__max;

        def extent (self, len):
            self.__offset += len;
            self.__max = max (self.__offset, self.__max);

        def rewind (self, len):
            self.__offset -= len;

        def top (self):
            mem = self.__reloca_table_mem (-self.__offset, self.__bp());
            self.__mem_refs.append(mem);
            return mem;

        def __reloca_table_mem (self, offset, base):
            return IndirectMemoryReference.reloca_table(offset, base);

        def __bp(self):
            return Register (RegisterClass.BP, natural_type);

        def fix_offset (self, diff):
            for mem in self.__mem_refs:
                mem.fix_offset (diff);

