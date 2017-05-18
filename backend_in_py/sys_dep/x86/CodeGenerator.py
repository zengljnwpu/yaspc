class CodeGenerator ():
    __LABEL_SYMBOL_BASE = ".L"
    __CONST_SYMBOL_BASE = ".LC"

    def __init__ (self, options, natural_type, error_handler):
        self.__options = options
        self.__natural_type = natural_type
        self.__error_handler = error_handler

    #Compiles IR and generates assembly code.
    def generate (self, ir):
        self.__locate_symbols (ir)
        return self.generate_assembly_code (ir)

    #locate Symbols
    def __locate_symbols (self, ir):
        const_symbols = SymbolTable (CONST_SYMBOL_BASE)
        for ent in ir.const_table().entries():
            self.__locate_string_literal (ent, const_symbols);
        for var in ir.all_global_variables ():
            self.__locate_global_variable (var)
        for func in ir.all_functions():
            self.__locate_function (func)

    def __locate_string_literal (self, ent, syms):
        ent.set_symbols (syms.new_symbol())
        if self.options.is_position_indepedent ():
            offset = self.local_GOT_symbol (ent.symbol())
            ent.set_mem_ref (self.__mem (offset, self.__GOT_base_reg()));
        else:
            ent.set_mem_ref (self.__mem (ent.symbol()))
            ent.set_address (self.__imm (ent.symbol()))

    def __locate_global_variable (self, ent):
        sym = self.__symbol (ent.symbol_string(), ent.is_private())
        if (self.__options.is_positions_independent()):
            if ent.is_private() or self.__optimize_gvar_access (ent):
                ent.set_mem_ref (self.__mem (self.__local_GOT_symbol (sym), self.__GOT_base_reg()))
            else:
                ent.set_address (self.__mem (self.__global_GOT_symbol(sym), self.__GOT_base_reg()))
        else:
            ent.set_mem_ref (self.__mem (sym))
            ent.set_address (self.__imm (sym))

    def __locate_function (self, func):
        func.set_calling_symbol (self.__calling_symbol (func))
        self.__locate_global_variable(func)

    def __symbol (self, sym, is_private):
        if is_private:
            return self.__private_symbol (sym)
        else:
            return self.__global_symbol (sym)

    def __global_symbol (self, sym):
        return NamedSymbol (sym)

    def __private_symbol (self, sym):
        return NamedSymbol (sym)

    def __calling_symbol (self, func):
        if func.is_private:
            return self.__private_symbol(fun.symbol_string())
        else:
            sym = self.__global_symbol(func.symbol_string())
            if self.__should_use_plt (func):
                return PLT_symbol (sym)
            else:
                return sym

    def __should_use_plt (self, ent):
        return self.__options.is_positions_independent () and not self.__optimize_gvar_access (ent)

    def __optimize_gvar_access (self, ent):
        return self.__options.is_PIE_required () and ent.is_defined()

    #generate Assembly code
    def __generate_assembly_code (self, ir):
        file = self.__new_assembly_code ()
        file._file (ir.file_name())
        if ir.is_global_variable_defined():
            self.__generate_data_section (file, ir.defined_global_variables())
        if ir.is_string_literal_defined():
            self.__generate_read_only_data_section (file, ir.const_table())
        if ir.is_function_defined():
            self.__generate_text_section (file, ir.defined_funcitons())
        if ir.is_common_symbol_defined():
            self.__generate_common_symbols (file, ir.defined_common_symbols())
        if self.__options.is_positions_independent():
            self.__PIC_thunk (file, self.__GOT_base_reg())
        return file

    def __new_assembly_code (self):
        return AssemblyCode (self.__natural_type, self.__STACK_WORD_SIZE, \
                             SymbolTable (self.__LABEL_SYMBOL_BASE),\
                             self.__options.is_verbose_asm())

    def __generate_data_section (self, file, gvars):
        file._data()
        for var in gvars:
            sym = self.__global_symbol(var.symbol_string())
            if not var.is_private():
                file._globl (sym)
            file._align (var.alignment())
            file._type (sym, "@object")
            file._size (sym, var.alloc_size())
            file.label (sym)
            self.__generate_immediate (file, var.type().alloc_size(), var.ir())

    #generate immediate values for .data section
    def __generate_immediate (self, file, size, node):
        if isinstance(node, Int):
            expr = Int (node)
            if size == 1:
                file._byte (expr.value())
            elif size == 2:
                file._value (expr.value())
            elif size == 4:
                file._long (expr.value())
            elif size == 8:
                file._quad (expr.value())
            else:
                raise ArithmeticError
        elif isinstance(node, Str):
            expr = Str (node)
            if size == 4:
                file._long (expr.symbol())
            elif size == 8:
                file._quad (expr.symbol())
            else:
                raise ArithmeticError
        else:
            raise ArithmeticError

    #generate .rodata entries (const strings)
    def __generate_read_only_data_section (self, file, constants):
        file._section (".rodata")
        for ent in constants:
            file.label (ent.symbol())
            file._string (ent.value())

    def __generate_text_section (self, file, functions):
        file._text()
        for func in functions:
            sym = self.__global_symbol(func.name())
            if not func.is_private():
                file._globl (sym)
            file._type (sym, "@function")
            file.label (sym)
            self.__compile_function_body (file, func)
            file._size (sym, ".-" + sym.to_source())

    def __generate_common__symbols (self, file, variables):
        for var in variables:
            sym = self.__global_symbol(var.symbol_string())
            if var.is_private():
                file._local (sym)
            file._comm (sym, var.alloc_size(), var.alignment())

    #PIC/PIE related constants and codes
    __GOT = NamedSymbol ("_GLOBAL_OFFSET_TABLE_")

    def __load_GOT_base_address (self, file, reg):
        file.call (PIC_thunk_symbol (reg))
        file.add (self.__imm (self.__GOT), reg)

    def __GOT_base_reg (self):
        return self.__bx ()

    def __global_GOT_symbol (self, base):
        return SuffixedSymbol (base, "@GOT")

    def __local_GOT_symbol (self, base):
        return SuffixedSymbol (base, "@GOTOFF")

    def __PLT_symbol (self, base):
        return SuffixedSymbol (base, "@PLT")

    def __PIC_thunk_symbol (self, reg):
        return NamedSymbol ("__i686.get_pc_thunk." + reg.base_name())

    __PIC_thunk_section_flags = SectionFlag_allocatable + SectionFlag_executable + SectionFlag_sectiongroup

    #Output PIC thunk
    #ELF section declaration format is:
    #
    #   .section NAME, FLAGS, TYPE, flag_arguments
    #
    #FLAGS, TYPE, flag_arguments are optimal
    #For "M" flag (a member of a section group),
    #following format is used:
    #
    # .section NAME, "...M", TYPE, section_group_name, linkage
    #

    def __PIC_thunk (self, file, reg):
        sym = self.__PIC_thunk_symbol(reg)
        file._section (".text" + "." + sym.to_source(),\
                       "\"" + PICThunkSectionFlags + "\"",
                       SectionType_bits, \
                       sym.toSource(), \
                       Linkage_linkonce)
        file._globl (sym)
        file._hidden (sym)
        file._type (sym, SymbolType_function)
        file.label (sym)
        file.mov (self.__mem (self.__sp()), reg)
        file.ret()

    # Compile Function
    #
    #
    # Standard IA-32 stack frame layout



    # Expressions

    # Assignable expressions




