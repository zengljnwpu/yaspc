from backend_in_py.sys_dep.x86.assembly_code import *
from backend_in_py.ir.expr import *
from backend_in_py.ir.op import *
from backend_in_py.ir.stmt import *
from backend_in_py.sys_dep.x86.register import RegisterClass


class CodeGenerator():
    LABEL_SYMBOL_BASE = ".L"
    CONST_SYMBOL_BASE = ".LC"

    def __init__(self, options, natural_type):
        self._options = options
        self._natural_type = natural_type
        __as = None
        __epilogue_ = None

    # Compiles IR and generates assembly code.
    def generate(self, ir):
        self.__locate_symbols(ir)
        return self.__generate_assembly_code(ir)

    # locate Symbols
    def __locate_symbols(self, ir):
        const_symbols = SymbolTable(self.CONST_SYMBOL_BASE)
        # for ent in ir.const_table().entries():
        #    self.__locate_string_literal (ent, const_symbols)
        for var in ir.all_global_variables():
            self.__locate_global_variable(var)
        for func in ir.all_functions():
            self.__locate_function(func)

    # def __locate_string_literal (self, ent, syms):
    #     ent.set_symbols (syms.new_symbol())
    #     if self._options.is_position_indepedent ():
    #         offset = self.__local_GOT_symbol (ent.symbol())
    #         ent.set_mem_ref (self.__mem (offset, self.__GOT_base_reg()))
    #     else:
    #         ent.set_mem_ref (self.__mem (ent.symbol()))
    #         ent.set_address (self.__imm (ent.symbol()))

    def __locate_global_variable(self, ent):
        sym = self.__symbol(ent.symbol_string(), ent.is_private())
        # if (self._options.is_positions_independent()):
        #     if ent.is_private() or self.__optimize_gvar_access (ent):
        #         ent.set_mem_ref (self.__mem (self.__local_GOT_symbol (sym), self.__GOT_base_reg()))
        #     else:
        #         ent.set_address (self.__mem (self.__global_GOT_symbol(sym), self.__GOT_base_reg()))
        # else:
        ent.set_mem_ref(self.__mem(sym))
        ent.set_address(self.__imm(sym))

    def __locate_function(self, func):
        func.set_calling_symbol(self.__calling_symbol(func))
        self.__locate_global_variable(func)

    def __symbol(self, sym, is_private):
        if is_private:
            return self.__private_symbol(sym)
        else:
            return self.__global_symbol(sym)

    def __global_symbol(self, sym):
        return NamedSymbol(sym)

    def __private_symbol(self, sym):
        return NamedSymbol(sym)

    #
    def __calling_symbol(self, func):
        # if func.is_private:
        #     return self.__private_symbol(fun.symbol_string())
        # else:
        sym = self.__global_symbol(func.symbol_string())
        # if self.__should_use_plt (func):
        #     return PLT_symbol (sym)
        # else:
        return sym

    #
    # def __should_use_plt (self, ent):
    #     return self._options.is_positions_independent () and not self.__optimize_gvar_access (ent)
    #
    # def __optimize_gvar_access (self, ent):
    #     return self._options.is_PIE_required () and ent.is_defined()

    # generate Assembly code
    def __generate_assembly_code(self, ir):
        file = self.__new_assembly_code()
        file._file(ir.file_name())
        if ir.is_global_variable_defined():
            self.__generate_data_section(file, ir.defined_global_variables())
        # if ir.is_string_literal_defined():
        #     self.__generate_read_only_data_section (file, ir.const_table())
        if ir.is_function_defined():
            self.__generate_text_section(file, ir.defined_funcitons())
        # if ir.is_common_symbol_defined():
        #     self.__generate_common_symbols (file, ir.defined_common_symbols())
        # if self._options.is_positions_independent():
        #     self.__PIC_thunk (file, self.__GOT_base_reg())
        return file

    def __new_assembly_code(self):
        return AssemblyCode(self._natural_type, self.__STACK_WORD_SIZE,
                            SymbolTable(self.LABEL_SYMBOL_BASE),
                            verbose=False)

    def __generate_data_section(self, file, gvars):
        file._data()
        for var in gvars:
            sym = self.__global_symbol(var.symbol_string())
            if not var.is_private():
                file._globl(sym)
            file._align(var.alignment())
            file._type(sym, "@object")
            file._size(sym, var.alloc_size())
            file.label(sym)
            self.__generate_immediate(file=file, size=var.type().alloc_size(), node=var.initializer())

    # generate immediate values for .data section
    def __generate_immediate(self, file, size, node):
        if node["type"] == "INT32":
            expr = int(node["value"])
            if size == 1:
                file._byte(expr)
            elif size == 2:
                file._value(expr)
            elif size == 4:
                file._long(expr)
            elif size == 8:
                file._quad(expr)
            else:
                raise ArithmeticError
        elif isinstance(node, str):
            expr = Str(node)
            if size == 4:
                file._long(expr.symbol())
            elif size == 8:
                file._quad(expr.symbol())
            else:
                raise ArithmeticError
        else:
            raise ArithmeticError

    # #generate .rodata entries (const strings)
    # def __generate_read_only_data_section (self, file, constants):
    #     file._section (".rodata")
    #     for ent in constants:
    #         file.label (ent.symbol())
    #         file._string (ent.value())

    def __generate_text_section(self, file, functions):
        file._text()
        for func in functions:
            sym = self.__global_symbol(func.name())
            if not func.is_private():
                file._globl(sym)
            file._type(sym, "@function")
            file.label(sym)
            self.__compile_function_body(file, func)
            file._size(sym, ".-" + sym.to_source())

    # def __generate_common_symbols (self, file, variables):
    #     for var in variables:
    #         sym = self.__global_symbol(var.symbol_string())
    #         if var.is_private():
    #             file._local (sym)
    #         file._comm (sym, var.alloc_size(), var.alignment())
    #
    #
    #          These codes (GOT and PIC) were used to describe functions that used in Dynamic-link library
    #
    #
    # #PIC/PIE related constants and codes
    # __GOT = NamedSymbol ("_GLOBAL_OFFSET_TABLE_")
    #
    # def __load_GOT_base_address (self, file, reg):
    #     file.call (PIC_thunk_symbol (reg))
    #     file.add (self.__imm (self.__GOT), reg)
    #
    # def __GOT_base_reg (self):
    #     return self.__bx ()
    #
    # def __global_GOT_symbol (self, base):
    #     return SuffixedSymbol (base, "@GOT")
    #
    # def __local_GOT_symbol (self, base):
    #     return SuffixedSymbol (base, "@GOTOFF")
    #
    # def __PLT_symbol (self, base):
    #     return SuffixedSymbol (base, "@PLT")
    #
    # def __PIC_thunk_symbol (self, reg):
    #     return NamedSymbol ("__i686.get_pc_thunk." + reg.base_name())
    #
    # __PIC_thunk_section_flags = SectionFlag_allocatable + SectionFlag_executable + SectionFlag_sectiongroup
    #
    # #Output PIC thunk
    # #ELF section declaration format is:
    # #
    # #   .section NAME, FLAGS, TYPE, flag_arguments
    # #
    # #FLAGS, TYPE, flag_arguments are optimal
    # #For "M" flag (a member of a section group),
    # #following format is used:
    # #
    # # .section NAME, "...M", TYPE, section_group_name, linkage
    # #
    #
    # def __PIC_thunk (self, file, reg):
    #     sym = self.__PIC_thunk_symbol(reg)
    #     file._section (".text" + "." + sym.to_source(),\
    #                    "\"" + PICThunkSectionFlags + "\"",
    #                    SectionType_bits, \
    #                    sym.toSource(), \
    #                    Linkage_linkonce)
    #     file._globl (sym)
    #     file._hidden (sym)
    #     file._type (sym, SymbolType_function)
    #     file.label (sym)
    #     file.mov (self.__mem (self.__sp()), reg)
    #     file.ret()
    #
    # # Compile Function
    # #
    # #
    # # Standard IA-32 stack frame layout
    #
    #
    #
    # # Expressions
    #
    # # Assignable expressions
    __STACK_WORD_SIZE = 4

    def __align_stack(self, size):
        return align(size, self.__STACK_WORD_SIZE)

    def __stack_size_from_word_num(self, num_words):
        return num_words * self.__STACK_WORD_SIZE

    class StackFrameInfo():
        __STACK_WORD_SIZE = 4

        def __init__(self):
            self.save_regs = []
            self.lvar_size = 0
            self.temp_size = 0

        def save_regs_size(self):
            return len(self.save_regs) * self.__STACK_WORD_SIZE

        def lvar_offset(self):
            return self.save_regs_size()

        def temp_offset(self):
            return self.save_regs_size() + self.lvar_size

        def frame_size(self):
            return self.save_regs_size() + self.lvar_size + self.temp_size

    def __compile_function_body(self, file, func):
        frame = self.StackFrameInfo()
        self.__locate_parameters(func.parameters())
        frame.lvar_size = self.__locate_local_variables(func.lvar_scope())

        body = self.__optimize(self.__compile_stmts(func))
        frame.save_regs = self.__used_callee_save_registers(body)
        frame.temp_size = body.virtual_stack.max_size()

        self.__fix_local_variable_offsets(func.lvar_scope(), frame.lvar_offset())
        self.__fix_temp_varaible_offsets(body, frame.temp_offset())
        self.__generate_function_body(file, body, frame)

    def __optimize(self, body):
        # if self._options.optimize_level () < 1:
        return body
        # body.apply (PeepholeOptimizer.default_set())
        # body.reduce_labels ()
        # return body

    class MemInfo():
        def __init__(self, mem=MemoryReference(), name=""):
            self.mem = mem
            self.name = name

    def __compile_stmts(self, func):
        self.__as = self.__new_assembly_code()
        self.__epilogue_ = Label()
        for s in func.ir():
            self.__compile_stmt(s)
        self.__as.label(self.__epilogue_)
        return self.__as

    # does Not include BP register
    def __used_callee_save_registers(self, body):
        result = []
        for reg in self.__callee_save_registers():
            if body.does_uses(reg):
                result.append(reg)
        # result.remove(self.__bp())
        return result

    CALLEE_SAVE_REGISTERS = [RegisterClass.BX, RegisterClass.BP, RegisterClass.SI, RegisterClass.DI]
    __callee_save_registers_cache = []

    def __callee_save_registers(self):
        if not self.__callee_save_registers_cache:
            regs = []
            for c in self.CALLEE_SAVE_REGISTERS:
                regs.append(x86Register(c, self._natural_type))
            self.__callee_save_registers_cache = regs
        return self.__callee_save_registers_cache

    def __generate_function_body(self, file, body, frame):
        file.virtual_stack.reset()
        self.__prologue(file, frame.save_regs, frame.frame_size())
        # if self._options.is_positions_independent() and body.does_uses (self.__GOT_base_reg()):
        #   self.__load_GOT_base_address(file, self.__GOT_base_reg())

        file.add_all(body.assemblies())
        self.__epilogue(file, frame.save_regs)
        file.virtual_stack.fix_offset(0)

    def __prologue(self, file, save_regs, frame_size):
        file.push(self.__bp())
        file.mov(self.__sp(), self.__bp())
        for reg in save_regs:
            file.virtual_push(reg)
        self.__extend_stack(file, frame_size)

    def __epilogue(self, file, saved_regs=list()):
        temp_list = saved_regs.copy()
        temp_list.reverse()
        for reg in temp_list:
            file.virtual_pop(reg)
        file.mov(self.__bp(), self.__sp())
        file.pop(self.__bp())
        file.ret()

    __PARAM_START_WORD = 2

    def __locate_parameters(self, params):
        num_words = self.__PARAM_START_WORD
        for var in params._param_descriptors:
            var.set_mem_ref(self.__mem(self.__stack_size_from_word_num(num_words), self.__bp()))
            num_words += 1

    # Allocates _address of local variables, but offset is still not determined, assign unfixed IndirectMemoryReference
    def __locate_local_variables(self, scope, parent_stack_len=0):
        len = parent_stack_len
        for var in scope.local_variables():
            len = self.__align_stack(len + var.alloc_size())
            var.set_mem_ref(self.__reloca_table_mem(-len, self.__bp()))

        max_len = len
        return max_len

    def __reloca_table_mem(self, offset, base):
        return IndirectMemoryReference.reloca_table(offset, base)

    def __fix_local_variable_offsets(self, scope, len):
        for var in scope.all_local_variables():
            var.mem_ref().fix_offset(-len)

    def __fix_temp_varaible_offsets(self, asm, len):
        asm.virtual_stack.fix_offset(-len)

    def __extend_stack(self, file, len):
        if len > 0:
            file.sub(self.__imm(len), self.__sp())

    def __rewind_stack(self, file, len):
        if len > 0:
            file.add(self.__imm(len), self.__sp())

    # Implements cdecl function call:
    #   All arguments are on stack
    #   Caller rewinds stack pointer.
    #
    def visit(self, node):
        if isinstance(node, Call):
            temp_list = list(node.args().copy())
            temp_list.reverse()
            for arg in temp_list:
                self.__compile(arg)
                self.__as.push(self.__ax())
            if node.is_static_call():
                self.__as.call(node.function().calling_symbol())
            else:
                self.__compile(node.expr())
                self.__as.call_absolute(self.__ax())
            self.__rewind_stack(self.__as, self.__stack_size_from_word_num(node.num_args()))
        elif isinstance(node, Return):
            if node.expr():
                self.__compile(node.expr())
            # self.__as.jmp (self.__epilogue_)
            return None
        elif isinstance(node, ExprStmt):
            self.__compile(node.expr())
            return None
        elif isinstance(node, LabelStmt):
            self.__as.label(node.label())
            return None
        elif isinstance(node, Jump):
            self.__as.jmp(node.label())
            return None
        elif isinstance(node, CJump):
            self.__compile(node.cond())
            t = node.cond().type()
            self.__as.test(self.__ax(t), self.__ax(t))
            self.__as.jne(node.then_label())
            self.__as.jmp(node.else_label())
            return None
        elif isinstance(node, Bin):
            op = node.op()
            t = node.type()
            if node.right().is_constant() and not self.__does_require_register_operand(op):
                self.__compile(node.left())
                self.__compile_binary_op(op, self.__ax(t), node.right().asm_value())

                #TODO: Modify the ADD part
                self.__store(self.__ax(node.value().type()), node.value().mem_ref())
            elif node.right().is_constant():
                self.__compile_binary_op(node.left())
                self.__load_constant(node.right(), self.__cx())
                self.__compile_binary_op(op, self.__ax(t), self.__cx(t))
            elif node.right().is_var():
                self.__compile(node.left())
                self.__load_variable(node.right(), self.__cx(t))
                self.__compile_binary_op(op, self.__ax(t), self.__cx(t))
            elif node.right().is_addr():
                self.__compile(node.left())
                self.__load_address(node.right().get_entity_force(), self.__cx(t))
                self.__compile_binary_op(op, self.__ax(t), self.__cx(t))
            elif node.left().is_constant() or node.left().is_var() or node.left().is_addr():
                self.__compile(node.right())
                self.__as.mov(self.__ax(), self.__cx)
                self.__compile(node.left())
                self.__compile_binary_op(op, self.__ax(t), self.__cx(t))
            else:
                self.__compile(node.right())
                self.__as.virtual_push(self.__ax())
                self.__compile(node.left())
                self.__as.virtual_pop(self.__cx())
                self.__compile_binary_op(op, self.__ax(t), self.__cx(t))
            return None
        elif isinstance(node, Uni):
            src = node.expr().type()
            dest = node.type()
            self.__compile(node.expr())
            if node.op == Op.UMINUS:
                self.__as.neg(self.__ax(src))
            elif node.op == Op.BIT_NOT:
                self.__as._not(self.__ax(src))
            elif node.op == Op.NOT:
                self.__as.test(self.__ax(src), self.__ax(src))
                self.__as.sete(self.__al())
                self.__as.movzx(self.__al(), self.__ax(dest))
            elif node.op == Op.S_CAST:
                self.__as.movsx(self.__ax(src), self.__ax(dest))
            elif node.op == Op.U_CAST:
                self.__as.movzx(self.__ax(src), self.__ax(dest))
            else:
                raise Exception
            return None
        elif isinstance(node, Var):
            self.__load_variable(node, self.__ax())
            return None
        elif isinstance(node, Int):
            self.__as.mov(self.__imm(node.value()), self.__ax())
            return None
        elif isinstance(node, Str):
            self.__load_constant(node, self.__ax())
            return None
        elif isinstance(node, Assign):
            if node.lhs().is_addr() and node.lhs().mem_ref():
                self.__compile(node.rhs())
                self.__store(self.__ax(node.lhs().type()), node.lhs().mem_ref())
            elif node.rhs().is_constant():
                self.__compile(node.lhs())
                self.__as.mov(self.__ax(), self.__cx())
                self.__load_constant(node.rhs(), self.__ax())
                self.__store(self.__ax(node.lhs().type()), self.__mem(self.__cx()))
            else:
                self.__compile(node.rhs())
                self.__as.virtual_push(self.__ax())
                self.__compile(node.lhs())
                self.__as.mov(self.__ax(), self.__cx())
                self.__as.virtual_pop(self.__ax())
                self.__store(self.__ax(node.lhs().type()), self.__mem(self.__cx()))
            return None
        elif isinstance(node, Mem):
            self.__compile(node.expr())
            self.__load(self.__mem(self.__ax()), self.__ax(node._type))
            return None
        elif isinstance(node, Addr):
            self.__load_address(node.entity(), self.__ax())
            return None

    # Statemments
    def __compile_stmt(self, stmt):
        stmt.accept(self)

    # Expression
    def __compile(self, n):
        n.accept(self)

    def __does_require_register_operand(self, op):
        if op == Op.S_DIV:
            return True
        elif op == Op.U_DIV:
            return True
        elif op == Op.S_MOD:
            return True
        elif op == Op.U_MOD:
            return True
        elif op == Op.BIT_LSHIFT:
            return True
        elif op == Op.BIT_RSHIFT:
            return True
        elif op == Op.ARITH_RSHIFT:
            return True
        else:
            return False

    def __compile_binary_op(self, op, left, right):
        if op == Op.ADD:
            self.__as.add(right, left)
        elif op == Op.SUB:
            self.__as.add(right, left)
        elif op == Op.MUL:
            self.__as.imul(right, left)
        elif op == Op.S_DIV or op == Op.S_MOD:
            self.__as.cltd()
            self.__as.idiv(self.__cx(left.type))
            if (op == Op.S_MOD):
                self.__as.mov(self.__dx(), left)
        elif op == Op.U_DIV or op == Op.U_MOD:
            self.__as.mov(self.__imm(0), self.__dx())
            self.__as.div(self.__cx(left.type))
            if op == Op.U_MOD:
                self.__as.mov(self.__dx(), left)
        elif op == Op.BIT_AND:
            self.__as._and(right, left)
        elif op == Op.BIT_OR:
            self.__as._or(right, left)
        elif op == Op.BIT_XOR:
            self.__as.xor(right, left)
        elif op == Op.BIT_LSHIFT:
            self.__as.sal(self.__cl(), left)
        elif op == Op.BIT_RSHIFT:
            self.__as.shr(self.__cl(), left)
        elif op == Op.ARITH_RSHIFT:
            self.__as.sar(self.__cl(), left)
        else:
            self.__as.cmp(right, self.__ax(left.type))
            if op == Op.EQ:
                self.__as.sete(self.__al())
            elif op == Op.NEQ:
                self.__as.setne(self.__al())
            elif op == Op.S_GT:
                self.__as.setg(self.__al())
            elif op == Op.S_GTEQ:
                self.__as.setge(self.__al())
            elif op == Op.S_LT:
                self.__as.setl(self.__al())
            elif op == Op.S_LTEQ:
                self.__as.setle(self.__al())
            elif op == Op.U_GT:
                self.__as.seta(self.__al())
            elif op == Op.U_GTEQ:
                self.__as.ae(self.__al())
            elif op == Op.U_LT:
                self.__as.setb(self.__al())
            elif op == Op.U_LTEQ:
                self.__as.setbe(self.__al())
            else:
                raise ArithmeticError
            self.__as.movzx(self.__al(), left)

    # Utilities

    # Load constant _value, you must check node by #isConstant
    # beforce calling this method

    def __load_constant(self, node, reg):
        if node.asm_value():
            self.__as.mov(node.asm_value(), reg)
        elif node.mem_ref():
            self.__as.lea(node.mem_ref(), reg)
        else:
            raise Exception

    # Load variable content to the register
    def __load_variable(self, var: Var, dest: x86Register):
        if not var.mem_ref():
            a = dest.for_type(self._natural_type)
            self.__as.mov(var.address(), a)
            self.__load(self.__mem(a), dest.for_type(var.type()))
        else:
            t = var.type()
            self.__load(var.mem_ref(), dest.for_type(var.type()))

    # Load the _address of the variable to the register
    def __load_address(self, var, dest):
        if var.address():
            self.__as.mov(var.address(), dest)
        else:
            self.__as.lea(var.mem_ref(), dest)

    def __ax(self, t=0):
        if t == 0:
            t = self._natural_type
        return x86Register(RegisterClass.AX, t)

    def __al(self):
        return self.__ax(Type.INT8.size())

    def __bx(self, t=0):
        if t == 0:
            t = self._natural_type
        return x86Register(RegisterClass.BX, t)

    def __cx(self, t=0):
        if t == 0:
            t = self._natural_type
        return x86Register(RegisterClass.CX, t)

    def __cl(self):
        return self.__cx(Type.INT8.size())

    def __dx(self, t=0):
        if t == 0:
            t = self._natural_type
        return x86Register(RegisterClass.DX, t)

    def __si(self):
        return x86Register(RegisterClass.SI, self._natural_type)

    def __di(self):
        return x86Register(RegisterClass.DI, self._natural_type)

    def __bp(self):
        return x86Register(RegisterClass.BP, self._natural_type)

    def __sp(self):
        return x86Register(RegisterClass.SP, self._natural_type)

    def __mem(self, a=0, b=0):
        if isinstance(a, Symbol) and b == 0:
            return DirectMemoryReference(a)
        elif isinstance(a, x86Register) and b == 0:
            return IndirectMemoryReference(0, a)
        elif isinstance(a, int) and isinstance(b, x86Register):
            return IndirectMemoryReference(a, b)
        elif isinstance(a, Symbol) and isinstance(b, x86Register):
            return IndirectMemoryReference(a, b)

    def __imm(self, n=0):
        if isinstance(n, int) and n != 0:
            return ImmediateValue(n)
        elif isinstance(n, Symbol):
            return ImmediateValue(n)
        elif isinstance(n, Literal):
            return ImmediateValue(n)

    def __load(self, mem, reg):
        self.__as.mov(mem, reg)

    def __store(self, reg, mem):
        self.__as.mov(reg, mem)


def align(n: int, alignment: int):
    return int((n + alignment - 1) / alignment) * alignment
