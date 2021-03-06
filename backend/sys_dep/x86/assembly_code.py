
from backend.asm.inttype import IntType
from backend.asm.statistics import Statistics
from backend.asm.assembly import Comment
from backend.asm.assembly import Label
from backend.asm.assembly import Directive
from backend.asm.assembly import Instruction
from backend.asm.operand import DirectMemoryReference
from backend.asm.operand import AbsoluteAddress
from backend.asm.operand import Operand
from backend.asm.operand import IndirectMemoryReference
from backend.asm.literal import Symbol
from backend.asm.literal import Literal
from backend.asm.literal import IntegerLiteral
from backend.sys_dep.x86.register import RegisterClass
from backend.sys_dep.x86.register import x86Register

# Describe a kind of ASM DSL (Domain Specific Languages) so that it can convert from ASM objects to ASM codes easily
class AssemblyCode():
    def __init__(self, natural_type, stack_wordsize, label_Symbols, verbose):
        self.natural_type = natural_type
        self.stack_wordsize = stack_wordsize
        self.label_symbols = label_Symbols
        self.verbose = verbose
        self.virtual_stack = VirtualStack(self.natural_type)
        self._assemblies = []
        self._comment_indent_level = 0
        self._statistics = Statistics ()

    def assemblies(self):
        return self._assemblies

    def add_all (self, assemblies):
        return self._assemblies.extend(assemblies)

    def to_source (self):
        buf = ""
        for asm in self._assemblies:
            buf += asm.to_source (self.label_symbols)
            buf+= "\n"
        return buf

    def dump (self):
        for asm in self._assemblies:
            print (asm.dump())

    def apply (self, opt):
        #optmization
        return

    def __statistics (self):
        if not self._statistics:
            self._statistics = Statistics.collect(self._assemblies)
        return self._statistics

    def does_uses (self, reg):
        return self._statistics.does_register_used (reg.base_name())

    def comment (self, code_str):
        self._assemblies.append (Comment (code_str, self._comment_indent_level))

    def indent_comment (self):
        self._comment_indent_level += 1

    def unindent_comment (self):
        self._comment_indent_level -= 1

    def label (self, sym):
        if isinstance(sym, Symbol):
            self._assemblies.append(Label (sym))
        elif isinstance(sym, Symbol):
            self._assemblies.append(sym)

    def reduce_label (self):
        stats = self._statistics
        result = []
        for asm in self._assemblies:
            if (asm.is_label ()) and (not (stats.does_symbol_used (Label(asm)))):
                continue
            else:
                result.append(asm)
        self._assemblies = result

    def _directive (self, direc):
        self._assemblies.append(Directive(direc))

    def _insn (self, t = None, op = None, suffix = None, a = None,b = None):
        if op and not t and not suffix and not a and not b:
            self._assemblies.append(Instruction (mnemonic = op))
        elif op and not t and not suffix and a and not b:
            self._assemblies.append(Instruction(mnemonic = op, suffix = "", a1 = a))
        elif op and not t and suffix and a and not b:
            self._assemblies.append(Instruction(mnemonic = op, suffix=  suffix, a1 = a))
        elif op and t and not suffix and a and not b:
            self._assemblies.append(Instruction (mnemonic = op, suffix = self._type_suffix(t), a1 = a))
        elif op and not t and suffix and a and b:
            self._assemblies.append(Instruction(mnemonic = op, suffix = suffix, a1 = a, a2 = b))
        elif op and t and not suffix and a and b:
            self._assemblies.append(Instruction(mnemonic = op, suffix = self._type_suffix(t), a1= a, a2=b))
        else:
            raise Exception ("wrong operand")

    def _type_suffix (self, t1, t2 = None):
        type_str = ""
        if t1:
            if t1.size() == IntType.INT8:
                type_str += "b"
            elif t1.size() == IntType.INT16:
                type_str += "w"
            elif t1.size() == IntType.INT32:
                type_str += "l"
            elif t1.size() == IntType.INT64:
                type_str += "q"
            else:
                raise Exception ("unknown register type: " + t1.size())
        if t2:
            if t2 == IntType.INT8:
                type_str += "b"
            elif t2 == IntType.INT16:
                type_str += "w"
            elif t2 == IntType.INT32:
                type_str += "l"
            elif t2 == IntType.INT64:
                type_str += "q"
            else:
                raise Exception("unknown register type: " + t2.size())
        return type_str

    #directives
    def _file (self, name):
        self._directive(".file\t" + name)

    def _text (self):
        self._directive("\t.text")

    def _data (self):
        self._directive("\t.data")

    def _section (self, name, flags = None, code_type = None, group = None, linkage = None):
        if flags and code_type and group and linkage:
            self._directive("\t.section\t" + name + "," + flags + "," + code_type + "," + group + "," + linkage)
        elif (not flags) and (not type) and (not group) and (not linkage):
            self._directive("\t.section\t" + name)

    def _globl (self, sym):
        self._directive(".globl " + sym.name())

    def _local (self, sym):
        self._directive(".local " + sym.name())

    def _hidden (self, sym):
        self._directive("\t.hidden\t", sym.name())

    def _comm (self, sym, size, alignment):
        self._directive("\t.comm\t" + sym.name() + "," + str (size) + "," + str (alignment))

    def _align (self, n):
        self._directive("\t.align\t" + str (n))

    def _type (self, sym, code_type):
        self._directive("\t.type\t" + sym._name + "," + code_type)

    def _size (self, sym, size):
        self._directive("\t.size\t" + sym._name + "," + str (size))

    def _byte (self, val):
        if isinstance(val, int):
            self._directive(".byte\t" + IntegerLiteral((val)).to_source())
        elif isinstance(val, Literal):
            self._directive(".byte\t" + val.to_source())

    def _value(self, val):
        if isinstance(val, int):
            self._directive("._value\t" + IntegerLiteral((val)).to_source())
        elif isinstance(val, Literal):
            self._directive("._value\t" + val.to_source())

    def _long(self, val):
        if isinstance(val, int):
            self._directive(".long\t" + IntegerLiteral((val)).to_source())
        elif isinstance(val, Literal):
            self._directive(".long\t" + val.to_source())

    def _quad(self, val):
        if isinstance(val, int):
            self._directive(".quad\t" + IntegerLiteral((val)).to_source())
        elif isinstance(val, Literal):
            self._directive(".quad\t" + val.to_source())

    def _string(self, code_str):
        self._directive("\t.string\t" + code_str)

    def virtual_push(self, reg):
        if self.verbose:
            self.comment("push " + reg.base_name() + " -> " + self.virtual_stack.top())
        else:
            self.virtual_stack.extent(self.stack_wordsize)
            self.mov (reg, self.virtual_stack.top())

    def virtual_pop(self, reg):
        if self.verbose:
            self.comment("pop " + reg.base_name() + " <- " + self.virtual_stack.top())
        else:
            self.mov(self.virtual_stack.top(), reg)
            self.virtual_stack.rewind(self.stack_wordsize)

    def jmp (self, label):
        self._insn(op = "jmp", a = DirectMemoryReference (label.symbol()))

    def jne (self, label):
        self._insn(op = "jnz", a = DirectMemoryReference (label.symbol()))

    def je (self, label):
        self._insn(op = "je", a = DirectMemoryReference (label.symbol()))

    def cmp (self, a, b):
        self._insn(t = b.type, op = "cmp", a = a, b = b)

    def sete (self, reg):
        self._insn(op = "sete", a = reg)

    def setne (self, reg):
        self._insn(op = "setne", a = reg)

    def seta (self, reg):
        self._insn(op = "seta", a = reg)

    def setae (self, reg):
        self._insn(op = "setae", a = reg)

    def setb (self, reg):
        self._insn(op = "setb", a = reg)

    def setbe (self, reg):
        self._insn(op = "setbe", a = reg)

    def setg (self, reg):
        self._insn(op = "setg", a = reg)

    def setge (self, reg):
        self._insn(op = "setge", a = reg)

    def setl (self, reg):
        self._insn(op = "setl", a = reg)

    def setle (self, reg):
        self._insn(op = "setle", a = reg)

    def test (self, a, b):
        self._insn(t = b.type, op = "test", a = a, b = b)

    def push (self, reg):
        self._insn(op = "push", suffix = self._type_suffix(self.natural_type), a = reg)

    def pop (self, reg):
        self._insn(op = "pop", suffix = self._type_suffix(self.natural_type), a = reg)

    #call function by relative _address
    def call (self, sym):
        self._insn(op = "call", a = DirectMemoryReference (sym))

    #call funciton byabsolute _address
    def call_absolute (self, reg):
        self._insn(op = "call", a = AbsoluteAddress (reg))

    def ret (self):
        self._insn(op = "ret")

    def mov (self, src, dest):
        if isinstance(src, x86Register) and isinstance(dest, x86Register):
            code_type = self.natural_type
        elif isinstance(src, Operand) and isinstance(dest, x86Register):
            code_type = dest.type
        elif isinstance(src, x86Register) and isinstance( dest, Operand):
            code_type = src.type
        else:
            raise Exception ("Wrong src or dest type")
        self._insn(t = code_type, op = "mov", a = src, b = dest)

    #for stack access
    def reloca_table_mov (self, src, dest):
        self._assemblies.append(Instruction ("mov", self._type_suffix(self.natural_type), src, dest, True))
    def movsx (self, src, dest):
        self._insn(op = "movs", suffix = self._type_suffix(src.type, dest.type), a = src, b = dest)
    def movzx (self, src, dest):
        self._insn(op = "movz", suffix = self._type_suffix(src.type, dest.type), a = src, b = dest)
    def movzb (self, src, dest):
        self._insn(op = "movz", suffix = "b" + str (self._type_suffix(src.type, dest.type)), a = src, b = dest)
    def lea (self, src, dest):
        self._insn(t = self.natural_type, op = "lea", a = src, b = dest)
    def neg (self, reg):
        self._insn(t = reg.type, op = "neg", a = reg)
    def add (self, diff, base):
        self._insn(t = base.type, op = "add", a = diff, b = base)
    def sub (self, diff, base):
        self._insn(t = base.type, op = "sub", a = diff, b = base)
    def imul (self, m, base):
        self._insn(t = base.type, op = "imul",a = m, b = base)
    def cltd (self):
        self._insn(op = "cltd")
    def div (self, base):
        self._insn(t = base.type, op = "div", a = base)
    def idiv (self, base):
        self._insn(t = base.type, op = "idiv", a = base)
    def _not (self, reg):
        self._insn(t = reg.type, op = "not", a = reg)
    def _and (self, bits, base):
        self._insn(t = base.type, op = "and", a = bits, b = base)
    def _or (self, bits, base):
        self._insn(t = base.type, op = "or", a = bits, b = base)
    def xor (self, bits, base):
        self._insn(t = base.type, op = "xor", a = bits, b = base)
    def sar (self, bits, base):
        self._insn(t = base.type, op = "sar", a = bits, b = base)
    def sal (self, bits, base):
        self._insn(t = base.type, op = "sal", a = bits, b = base)
    def shr (self, bits, base):
        self._insn(t = base.type, op = "shr", a = bits, b = base)

#Virtual Stack
class VirtualStack ():
        def __init__ (self, natural_type):
            self.__offset = 0
            self.__max = 0
            self.__mem_refs = []
            self.__natural_type = natural_type
            self.reset()

        def reset (self):
            self.__offset = 0
            self.__max = 0
            self.__mem_refs = []

        def max_size(self):
            return self.__max

        def extent (self, stack_len):
            self.__offset += stack_len
            self.__max = max (self.__offset, self.__max)

        def rewind (self, stack_len):
            self.__offset -= stack_len

        def top (self):
            mem = self.__reloca_table_mem (-self.__offset, self.__bp())
            self.__mem_refs.append(mem)
            return mem

        def __reloca_table_mem (self, offset, base):
            return IndirectMemoryReference.reloca_table(offset, base)

        def __bp(self):
            return x86Register (RegisterClass.BP, self.__natural_type)

        def fix_offset (self, diff):
            for mem in self.__mem_refs:
                mem.fix_offset (diff)

