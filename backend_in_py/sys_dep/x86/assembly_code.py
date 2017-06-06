from backend_in_py.asm.type import *
from backend_in_py.asm.assembly import *
from backend_in_py.asm.literal import *
from backend_in_py.asm.operand import *
from backend_in_py.asm.statistics import *
from backend_in_py.asm.symbol_table import *
from backend_in_py.sys_dep.x86.register_class import RegisterClass
from backend_in_py.sys_dep.x86.register import x86Register

class AssemblyCode():
    def __init__(self, natural_type: Type, stack_wordsize: int, label_Symbols: SymbolTable, verbose: bool):
        self.natural_type = natural_type
        self.stack_wordsize = stack_wordsize
        self.label_symbols = label_Symbols
        self.verbose = verbose
        self.virtual_stack = VirtualStack(self.natural_type)
        self._assemblies = []
        self._comment_indent_level = 0
        self._statistics = Statistics ()


    def add_all (self, assemblies: list):
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

    def does_uses (self, reg: Register):
        return self._statistics.does_register_used (reg)

    def comment (self, str: str):
        self._assemblies.append (Comment (str, self._comment_indent_level))

    def indent_comment (self):
        self._comment_indent_level += 1

    def unindent_comment (self):
        self._comment_indent_level -= 1

    def label (self, sym: Symbol):
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

    def _directive (self, direc: str):
        self._assemblies.append(Directive(direc))

    def _insn (self, t: Type = None, op: str = None, suffix:str = None, a: Operand = None,b: Operand = None):
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

    def _type_suffix (self, t1: Type, t2: Type = None):
        str = ""
        if t1:
            if t1 == Type.INT8:
                str += "b"
            elif t1 == Type.INT16:
                str += "w"
            elif t1 == Type.INT32:
                str += "l"
            elif t1 == Type.INT64:
                str += "q"
            else:
                raise Exception ("unknown register type: " + t1.size())
        if t2:
            if t2 == Type.INT8:
                str += "b"
            elif t2 == Type.INT16:
                str += "w"
            elif t2 == Type.INT32:
                str += "l"
            elif t2 == Type.INT64:
                str += "q"
            else:
                raise Exception("unknown register type: " + t2.size())
        return str

    #directives
    def _file (self, name: str):
        self._directive(".file\t" + name)

    def _text (self):
        self._directive("\t.text")

    def _data (self):
        self._directive("\t.data")

    def _section (self, name: str, flags:str = None, type:str = None, group:str = None, linkage:str = None):
        if flags and type and group and linkage:
            self._directive("\t.section\t" + name + "," + flags + "," + type + "," + group + "," + linkage)
        elif (not flags) and (not type) and (not group) and (not linkage):
            self._directive("\t.section\t" + name)

    def _globl (self, sym: Symbol):
        self._directive(".globl " + sym.name)

    def _local (self, sym: Symbol):
        self._directive(".local " + sym.name)

    def _hidden (self, sym: Symbol):
        self._directive("\t.hidden\t", sym.name)

    def _comm (self, sym: Symbol, size: int, alignment: int):
        self._directive("\t.comm\t" + sym.name + "," + str (size) + "," + str (alignment))

    def _align (self, n):
        self._directive("\t.align\t" + str (n))

    def _type (self, sym, type):
        self._directive("\t.type\t" + sym.name + "," + type)

    def _size (self, sym, size):
        self._directive("\t.size\t" + sym.name + "," + str (size))

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

    def _string(self, str: str):
        self._directive("\t.string\t" + str)

    def virtual_push(self, reg: x86Register):
        if self.verbose:
            self.comment("push " + reg.base_name() + " -> " + self.virtual_stack.top())
        else:
            self.virtual_stack.extent(self.stack_wordsize)
            self.mov (reg, self.virtual_stack.top())

    def virtual_pop(self, reg: x86Register):
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
            type = self.natural_type
        elif isinstance(src, Operand) and isinstance(dest, x86Register):
            type = dest.type
        elif isinstance(src, x86Register) and isinstance( dest, Operand):
            type = src.type
        self._insn(t = type, op = "mov", a = src, b = dest)

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
    def _xor (self, bits, base):
        self._insn(t = base.type, op = "xor", a = bits, b = base)
    def _sar (self, bits, base):
        self._insn(t = base.type, op = "sar", a = bits, b = base)
    def _sal (self, bits, base):
        self._insn(t = base.type, op = "sal", a = bits, b = base)
    def _shr (self, bits, base):
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
            self.__mem_refs.clear()

        def max_size(self):
            return self.__max

        def extent (self, len: int):
            self.__offset += len
            self.__max = max (self.__offset, self.__max)

        def rewind (self, len):
            self.__offset -= len

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

