'''
LLVM-IR code generation.
'''
from __future__ import absolute_import, print_function

import llvmlite.ir as ir
import llvmlite.llvmpy.core as lc

from frontend import ast
from frontend import symtab
from frontend import log
from frontend import typesys
from frontend import builtin
from frontend import visitor

# Constant type

def c_int(val, width=32):
    return ir.Constant(ir.IntType(width), val)


def c_char(val):
    return c_int(ord(val), 8)


def c_bool(val):
    return c_int(val, 1)


def c_double(val):
    return ir.Constant(ir.DoubleType(), val)


def c_float(val):
    return ir.Constant(ir.FloatType(), val)


def libc_format_string(args):
    fmt = ''

    for arg in args:
        if isinstance(arg.type, typesys.IntType):
            if arg.type.width == 64:
                fmt += '%li'

            if arg.type.width == 32:
                fmt += '%i'

            elif arg.type.width == 16:
                fmt += '%hi'

            elif arg.type.width == 8:
                fmt += '%hhi'

        elif isinstance(arg.type, typesys.CharType):
            fmt += '%c'

        elif isinstance(arg.type, typesys.RealType):
            fmt += '%lf'

        elif isinstance(arg.type, typesys.StringType):
            fmt += '%s'

        elif isinstance(arg.type, typesys.PointerType):
            fmt += '%p'

        elif (isinstance(arg.type, typesys.ArrayType) and
              isinstance(arg.type.element, typesys.CharType)):
            fmt += '%s'

    return fmt


class CodegenException(Exception):
    pass


class CodegenNodeException(CodegenException):

    def __init__(self, node, msg):
        CodegenException.__init__(self)
        self.msg = msg
        self.node = node

    def __str__(self):
        pos = self.node.position
        if not pos:
            pos = '?'

        return str(pos) + ':' + str(self.msg)


class Context(symtab.SymbolTable):

    def __init__(self):
        symtab.SymbolTable.__init__(self)
        self.module = None
        self.const_str_counter = 0

    @property
    def builder(self):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if hasattr(scope, 'builder'):
                return scope.builder

    @builder.setter
    def builder(self, val):
        scope = self._scopes[self._lvl]
        scope.builder = val

    @property
    def function(self):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if hasattr(scope, 'function'):
                return scope.function

    @function.setter
    def function(self, val):
        scope = self._scopes[self._lvl]
        scope.function = val

    def cast(self, operand, ty):
        if operand.type == ty:
            return operand

        # print operand, '==>', ty

        # Real --> Int (signed)
        if (isinstance(operand.type, typesys.RealType) and
            isinstance(ty, typesys.IntType) and
            ty.signed):

            return self.fptosi(operand, ty)

        # Real --> Int (unsigned)
        elif (isinstance(operand.type, typesys.RealType) and
            isinstance(ty, typesys.IntType) and
            ty.unsigned):

            return self.fptoui(operand, ty)

        # Real --> Real
        elif (isinstance(operand.type, typesys.RealType) and
            isinstance(ty, typesys.RealType) and
            operand.type.width > ty.width):

            return self.fptrunc(operand, ty)

        # Int --> Int
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.IntType) and
            operand.type.width > ty.width):

            return self.trunc(operand, ty)

        # Int --> Char
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.CharType)):

            if operand.type.width > ty.width:
                return self.trunc(operand, ty)
            else:
                return self.zext(operand, ty)

        # Char --> Int
        elif (isinstance(operand.type, typesys.CharType) and
            isinstance(ty, typesys.IntType)):

            return self.zext(operand, ty)

        # Char --> Real
        elif (isinstance(operand.type, typesys.CharType) and
            isinstance(ty, typesys.RealType)):

            return self.uitofp(operand, ty)

        # Reference --> Reference of Any
        elif (isinstance(operand.type, typesys.ReferenceType) and
              isinstance(ty, typesys.ReferenceType) and
              isinstance(ty.referee, typesys.AnyType)):

            return self.bitcast(operand, ty)

        # Pointer --> Pointer to Any
        elif (isinstance(operand.type, typesys.PointerType) and
              isinstance(ty, typesys.PointerType) and
              isinstance(ty.pointee, typesys.AnyType)):

            return self.bitcast(operand, ty)

        # Array --> Reference of Any
        elif (isinstance(operand.type, typesys.ArrayType) and
              isinstance(ty, typesys.ReferenceType) and
              isinstance(ty.referee, typesys.AnyType)):

            return self.bitcast(operand, ty)

        rc = self.coerce(operand, ty)
        if rc:
            return rc

        raise CodegenException("cast from '%s' to '%s'" % (operand.type, ty))

    def coerce(self, operand, ty):
        if operand.type == ty:
            return operand

        # print operand, '-->', ty

        # Int (signed) --> Real
        if (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.RealType) and
            operand.type.signed):

            return self.sitofp(operand, ty)

        # Int (unsigned) --> Real
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.RealType) and
            operand.type.unsigned):

            return self.uitofp(operand, ty)

        # Real --> Real
        elif (isinstance(operand.type, typesys.RealType) and
            isinstance(ty, typesys.RealType) and
            operand.type.width <= ty.width):

            return self.sitofp(operand, ty)

        # Int (signed) --> Int (signed)
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.IntType) and
            operand.type.width <= ty.width and
            operand.type.signed and ty.signed):

            return self.sext(operand, ty)

        # Int (unsigned) --> Int (signed)
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.IntType) and
            operand.type.width <= ty.width and
            operand.type.unsigned and ty.signed):

            return self.zext(operand, ty)

        # Int (signed) --> Int (unsigned)
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.IntType) and
            operand.type.width <= ty.width and
            operand.type.signed and ty.unsigned):

            return self.sext(operand, ty)

        # Int (unsigned) --> Int (unsigned)
        elif (isinstance(operand.type, typesys.IntType) and
            isinstance(ty, typesys.IntType) and
            operand.type.width <= ty.width and
            operand.type.unsigned and ty.unsigned):

            return self.zext(operand, ty)

        # EmptySet --> Set
        elif (isinstance(operand.type, typesys.EmptySetType) and
              isinstance(ty, typesys.SetType)):

            return self.zext(operand, ty)

        # Int --> Set (e.g. 3 in [1, 2, 3])
        elif (isinstance(operand.type, typesys.IntType) and
              isinstance(ty, typesys.SetType) and
              operand.type.width <= ty.width):

            return self.zext(operand, ty)

        # Set --> Set
        elif (isinstance(operand.type, typesys.SetType) and
              isinstance(ty, typesys.SetType) and
              ty.element.lo <= operand.type.element.lo and
              ty.element.hi >= operand.type.element.hi):

            return self.zext(operand, ty)

        # Pointer of Any (Null) --> Pointer
        elif (isinstance(operand.type, typesys.PointerType) and
              isinstance(ty, typesys.PointerType) and
              isinstance(operand.type.pointee, typesys.AnyType)):

            type_ = self.typegen(ty)
            handle = ir.Constant(type_, None)
            return symtab.ConstantValue(handle, ty)

        # Array --> String (within range, same type width)
        elif (isinstance(operand.type, typesys.StringType) and
              isinstance(ty, typesys.ArrayType) and
              operand.type.element.width == ty.element.width and
              operand.type.length <= ty.length):

            # preserve the String type
            ty = typesys.StringType(ty.length)
            return symtab.ConstantValue(operand.handle, ty)

        # Array --> Array (within range, same type width)
        elif (isinstance(operand.type, typesys.ArrayType) and
              isinstance(ty, typesys.ArrayType) and
              operand.type.element.width == ty.element.width and
              operand.type.length <= ty.length):

            return symtab.ConstantValue(operand.handle, ty)

        # log.w('codegen', "Unknown coerce from '%s' to '%s'", operand.type, ty)

    def typegen(self, ty):
        if ty.handle:
            return ty.handle

        ty.handle = self._typegen(ty)
        return ty.handle

    def _typegen(self, ty):

        if isinstance(ty, typesys.IntType):
            return ir.IntType(ty.width)

        elif isinstance(ty, typesys.CharType):
            return ir.IntType(8)

        elif isinstance(ty, typesys.FloatType):
            return ir.FloatType()

        elif isinstance(ty, typesys.DoubleType):
            return ir.DoubleType()

        elif isinstance(ty, typesys.ArrayType):
            ele_type = self.typegen(ty.element)
            length = ty.range.hi - ty.range.lo + 1
            return ir.ArrayType(ele_type, length)

        elif isinstance(ty, typesys.RecordType):
            ty.handle = ir.global_context.get_identified_type(ty.name)
            field_types = [self.typegen(x.type) for x in ty.fields]

            if ty.variant:
                selector = ty.variant.selector
                selector = self.typegen(selector.type)
                field_types.append(selector)

                largest = ty.variant.largest
                if largest:
                    largest = self.typegen(largest)
                    field_types.append(largest)

            ty.handle.set_body(field_types)
            return ty.handle

        elif isinstance(ty, typesys.FieldType):
            return self.typegen(ty.type)

        elif isinstance(ty, typesys.SetType):
            return ir.IntType(ty.width)

        elif isinstance(ty, typesys.EmptySetType):
            return ir.IntType(1)

        elif isinstance(ty, typesys.FunctionType):
            param_types = [self.typegen(x.type) for x in ty.params]
            ret_type = self.typegen(ty.ret)
            return ir.FunctionType(ret_type, param_types)

        elif isinstance(ty, typesys.VoidType):
            return ir.VoidType()

        elif isinstance(ty, typesys.ReferenceType):
            ref_type = self.typegen(ty.referee)
            return ir.PointerType(ref_type)

        elif isinstance(ty, typesys.PointerType):
            pointer_type = self.typegen(ty.pointee)
            return ir.PointerType(pointer_type)

        elif isinstance(ty, typesys.ScopeHookType):
            field_types = [self.typegen(x.type) for x in ty.fields]
            field_types = [ir.PointerType(x) for x in field_types]
            return ir.LiteralStructType(field_types)

        elif isinstance(ty, typesys.AnyType):
            # llvm doesn't support void*. Instead, i8* should be used
            return ir.IntType(8)

        raise CodegenException("unknown type '%s'" % type(ty))

    def c_string(self, val, pointer=False):
        if pointer:
            ty = typesys.CharType()
        else:
            length = len(val)
            ty = typesys.StringType(length + 1)

        type_ = self.typegen(ty)

        value = ir.GlobalVariable(self.module, type_, "conststr" + str(self.const_str_counter))
        self.const_str_counter += 1
        value.initializer = lc.Constant.stringz(val)
        value.linkage = lc.LINKAGE_INTERNAL
        value.global_constant = True

        return symtab.ConstantValue(value, ty)

    def translate_call(self, name, args):
        if name == 'writeln' or name == 'write':
            func_value = builtin.f_printf(self.module)
            func_type = builtin.translate_function(func_value)
            func = symtab.FunctionValue(func_value, func_type)

            # printf doesn't support boolean or floats
            # instead, we upcast them before printing to stdout
            for i in range(len(args)):
                if isinstance(args[i].type, typesys.BoolType):
                    ty = typesys.UIntType(16)
                    args[i] = self.cast(args[i], ty)
                elif isinstance(args[i].type, typesys.RealType):
                    ty = typesys.DoubleType()
                    args[i] = self.cast(args[i], ty)

            fmt = libc_format_string(args)
            if name == 'writeln':
                fmt += '\n'

            arg = self.c_string(fmt)
            args.insert(0, arg)

            # cast char array to char pointer
            for i in range(len(args)):
                if isinstance(args[i].type, typesys.StringType):
                    type_ = func_value.args[0].type  # char*
                    value = args[i].handle
                    value = self.builder.bitcast(value, type_)
                    args[i] = symtab.ConstantValue(value, args[i].type)

            return func, args

        elif name == 'read' or name == 'readln':
            func_value = builtin.f_scanf(self.module)
            func_type = builtin.translate_function(func_value)
            func = symtab.FunctionValue(func_value, func_type)

            fmt = libc_format_string(args)

            # TODO(Cholerae): scanf doesn't support booleans etc
            arg = self.c_string(fmt)
            args.insert(0, arg)

            # cast char array to char pointer
            for i in range(len(args)):
                if isinstance(args[i].type, typesys.StringType):
                    type_ = func_value.args[0].type  # char*
                    value = args[i].handle
                    value = self.builder.bitcast(value, type_)
                    args[i] = symtab.ConstantValue(value, args[i].type)

                elif (isinstance(args[i].type, typesys.IntType) or
                      isinstance(args[i].type, typesys.RealType)):
                    value = args[i].handle
                    ty = typesys.ReferenceType(args[i].type)
                    args[i] = symtab.ConstantValue(value, ty)

            return func, args

        # pascal1973.pdf P37 Standard functions

        # pascal1973.pdf P37 11.1.1 Arithmetic functions

        elif name == 'abs':
            handle = builtin.f_fabs(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'sqr':
            handle = c_double(2)
            ty = typesys.DoubleType()
            arg = symtab.ConstantValue(handle, ty)

            handle = builtin.f_pow(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            args.append(arg)

            return func, args

        elif name == 'sin':
            handle = builtin.f_sin(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'cos':
            handle = builtin.f_cos(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'tan':
            handle = builtin.f_tan(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'exp':
            handle = builtin.f_exp(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'ln':
            handle = builtin.f_ln(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'sqrt':
            handle = builtin.f_sqrt(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'arctan':
            handle = builtin.f_arctan(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        # pascal1973.pdf P38 11.1.2 Predicates
        # TODO(Cholerae): missing eof

        # elif name == 'odd':
        #     handle = builtin.f_odd(self.module)
        #     ty = builtin.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     return func, args
        
        # pascal1973.pdf P38 11.1.3 Transfer functions

        elif name == 'trunc':
            handle = builtin.f_trunc(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        elif name == 'round':
            handle = builtin.f_round(self.module)
            ty = builtin.translate_function(handle)
            func = symtab.FunctionValue(handle, ty)

            return func, args

        # elif name == 'ord':
        #     if isinstance(args[0].type, typesys.StringType):
        #         handle = builtin.f_atoi(self.module)
        #     else:
        #         handle = builtin.f_ord(self.module)

        #     ty = builtin.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     # typesys allow any type, cast the argument
        #     args[0] = self.cast(args[0], ty.params[0].type)

        #     return func, args

        # elif name == 'chr':
        #     handle = builtin.f_chr(self.module)
        #     ty = builtin.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     return func, args

        # pascal1973.pdf P38 11.1.4 Further standard functions
        # TODO(Cholerae): missing all

        # elif name == 'succ':
        #     handle = builtin.f_succ(self.module)
        #     ty = builtin.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     # typesys allow any type, cast the argument
        #     args[0] = self.cast(args[0], ty.params[0].type)

        #     return func, args

        # elif name == 'pred':
        #     handle = builtin.f_pred(self.module)
        #     ty = builtin.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     # typesys allow any type, cast the argument
        #     args[0] = self.cast(args[0], ty.params[0].type)

        #     return func, args

        # pascal1973.pdf P34 10.1 Standard procedures
        
        # pascal1973.pdf P34 10.1.1 File handling procedures
        # TODO(Cholerae): missing put/get/reset/rewrite

        # pascal1973.pdf P34 10.1.2 Dynamic allocation procedure
        # TODO(Cholerae): missing varargs new

        # elif name == 'new':
        #     handle = fn.f_new(self.module)
        #     ty = fn.translate_function(handle)
        #     func = symtab.FunctionValue(handle, ty)

        #     length = c_int(int(args[0].type.referee.pointee.width / 8))
        #     length = symtab.ConstantValue(length, typesys.UIntType(32))
        #     args.append(length)

        #     type_ = handle.args[0].type
        #     ptr = self.builder.bitcast(args[0].handle, type_)
        #     args[0] = symtab.ConstantValue(ptr, args[0].type)

        #     return func, args

        # psacal1973.pdf P35 10.1.3 Date transfer procedures
        # TODO(Cholerae): missing pack/unpack

        raise CodegenException("call to unknown function '%s'" % name)

    def scope_hook(self, ty):
        assert isinstance(ty, typesys.ScopeHookType)

        type_ = self.typegen(ty)
        scope = self.builder.alloca(type_, name='call_hook')

        for field in ty.fields:
            indices = [c_int(0), c_int(field.index)]
            var = self.builder.gep(scope, indices)
            sym = self.find_symbol(field.name)
            self.builder.store(sym.handle, var)

        return scope

    def call(self, func, args=[]):
        assert isinstance(func, symtab.FunctionValue)

        args = [x.handle for x in args]

        if func.type.scope_hook:
            param_ty = func.type.params[-1]
            ref_ty = param_ty.type
            hook_ty = ref_ty.referee
            hook_val = self.scope_hook(hook_ty)

            ref_val = self.builder.gep(hook_val, [c_int(0)])
            args.append(ref_val)

        value = self.builder.call(func.handle, args)

        return symtab.ConstantValue(value, func.type.ret)

    def add(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            if not self.builder:
                value = left.handle.fadd(right.handle)
            else:
                value = self.builder.fadd(left.handle, right.handle)

        elif isinstance(left.type, typesys.SetType):
            if not self.builder:
                value = left.handle.or_(right.handle)
            else:
                value = self.builder.or_(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.add(right.handle)
            else:
                value = self.builder.add(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def sub(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            if not self.builder:
                value = left.handle.fsub(left.handle, right.handle)
            else:
                value = self.builder.fsub(left.handle, right.handle)

        elif isinstance(left.type, typesys.SetType):
            if not self.builder:
                value = right.handle.not_()
                value = left.handle.and_(value)
            else:
                value = self.builder.not_(right.handle)
                value = self.builder.and_(left.handle, value)

        else:
            if not self.builder:
                value = left.handle.sub(right.handle)
            else:
                value = self.builder.sub(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def mul(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            if not self.builder:
                value = left.handle.fmul(right.handle)
            else:
                value = self.builder.fmul(left.handle, right.handle)

        elif isinstance(left.type, typesys.SetType):
            if not self.builder:
                value = left.handle.and_(right.handle)
            else:
                value = self.builder.and_(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.mul(right.handle)
            else:
                value = self.builder.mul(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def mod(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            if not self.builder:
                value = left.handle.frem(right.handle)
            else:
                value = self.builder.frem(left.handle, right.handle)

        elif isinstance(left.type, typesys.UIntType):
            if not self.builder:
                value = left.handle.urem(right.handle)
            else:
                value = self.builder.urem(left.handle, right.handle)

        else:
            if not self.builder:
                value = left.handle.srem(right.handle)
            else:
                value = self.builder.srem(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def div(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            if not self.builder:
                value = left.handle.fdiv(right.handle)
            else:
                value = self.builder.fdiv(left.handle, right.handle)

        elif isinstance(left.type, typesys.UIntType):
            if not self.builder:
                value = left.handle.udiv(right.handle)
            else:
                value = self.builder.udiv(left.handle, right.handle)
        
        else:
            if not self.builder:
                value = left.handle.sdiv(right.handle)
            else:
                value = self.builder.sdiv(left.handle, right.handle)

        return symtab.ConstantValue(value, left.type)

    def cmp_eq(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('==', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('==', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def cmp_neq(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('!=', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('!=', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def cmp_gt(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('>', left.handle, right.handle)

        elif (isinstance(left.type, typesys.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp_signed('>', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('>', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def cmp_ge(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('>=', left.handle, right.handle)

        elif (isinstance(left.type, typesys.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp_signed('>=', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('>=', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def cmp_lt(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('<', left.handle, right.handle)

        elif (isinstance(left.type, typesys.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp_signed('<', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('<', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def cmp_le(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        if isinstance(left.type, typesys.RealType):
            value = self.builder.fcmp_ordered('<=', left.handle, right.handle)

        elif (isinstance(left.type, typesys.IntType)
              and (left.type.signed or right.type.signed)):
            value = self.builder.icmp_signed('<=', left.handle, right.handle)

        else:
            value = self.builder.icmp_unsigned('<=', left.handle, right.handle)

        return symtab.ConstantValue(value, typesys.BoolType())

    def and_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        value = self.builder.and_(left.handle, right.handle)
        return symtab.ConstantValue(value, typesys.BoolType())

    def or_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        value = self.builder.or_(left.handle, right.handle)
        return symtab.ConstantValue(value, typesys.BoolType())

    def in_(self, left, right):
        assert isinstance(left, symtab.Value)
        assert isinstance(right, symtab.Value)

        type_ = self.typegen(right.type)
        value = self.builder.zext(left.handle, type_)
        value = self.builder.shl(c_int(1, type_.width), value)

        value = self.builder.and_(value, right.handle)
        value = self.builder.icmp_unsigned('!=', c_int(0, type_.width), value)

        return symtab.ConstantValue(value, typesys.BoolType())

    def not_(self, operand):
        assert isinstance(operand, symtab.Value)

        value = self.builder.not_(operand.handle)
        return symtab.ConstantValue(value, operand.type)

    def neg(self, operand):
        assert isinstance(operand, symtab.Value)

        if isinstance(operand.type, typesys.IntType):
            zero = c_int(0, operand.type.width)

            if not self.builder:
                value = zero.sub(operand.handle)
            else:
                value = self.builder.sub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

        elif isinstance(operand.type, typesys.DoubleType):
            zero = c_double(0)

            if not self.builder:
                value = zero.fsub(operand.handle)
            else:
                value = self.builder.fsub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

        elif isinstance(operand.type, typesys.FloatType):
            zero = c_float(0)

            if not self.builder:
                value = zero.fsub(operand.handle)
            else:
                value = self.builder.fsub(zero, operand.handle)

            return symtab.ConstantValue(value, operand.type)

    def fptosi(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptosi(type_)
        else:
            handle = self.builder.fptosi(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fptoui(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptoui(type_)
        else:
            handle = self.builder.fptoui(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fptrunc(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.fptrunc(type_)
        else:
            handle = self.builder.fptrunc(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def trunc(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.trunc(type_)
        else:
            handle = self.builder.trunc(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def sitofp(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)

        if not self.builder:
            handle = operand.handle.sitofp(type_)
        else:
            handle = self.builder.sitofp(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def uitofp(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)

        if not self.builder:
            handle = operand.handle.uitofp(type_)
        else:
            handle = self.builder.uitofp(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def fpext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if operand.handle.type == type_:
            return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.fpext(type_)
        else:
            handle = self.builder.fpext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def sext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if operand.handle.type.width == type_.width:
            return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.sext(type_)
        else:
            handle = self.builder.sext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def zext(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if operand.handle.type.width == type_.width:
                return symtab.ConstantValue(operand.handle, ty)

        if not self.builder:
            handle = operand.handle.zext(type_)
        else:
            handle = self.builder.zext(operand.handle, type_)

        return symtab.ConstantValue(handle, ty)

    def bitcast(self, operand, ty):
        assert isinstance(operand, symtab.Value)
        assert isinstance(ty, typesys.Type)

        type_ = self.typegen(ty)
        if not self.builder:
            handle = operand.handle.bitcast(type_)
        else:
            handle = self.builder.bitcast(operand.handle, type_)

        return symtab.ConstantValue(handle, operand.type)


class CodegenVisitor(visitor.DefaultVisitor):

    def __init__(self):
        self.ctx = Context()
        self.ctx.enter_scope()
        self.func_scope_level = 0

        self.ctx.module = ir.Module('main')

        self.ctx.install_typedef('Boolean' , typesys.BoolType())
        self.ctx.install_typedef('char'    , typesys.CharType())
        self.ctx.install_typedef('integer' , typesys.SIntType(16))
        self.ctx.install_typedef('word'    , typesys.UIntType(16))
        self.ctx.install_typedef('longint' , typesys.SIntType(32))
        self.ctx.install_typedef('double'  , typesys.DoubleType())
        self.ctx.install_typedef('real'    , typesys.FloatType())

        self.ctx.install_const('cr'        , typesys.CharType()  , c_char('\r'))
        self.ctx.install_const('false'     , typesys.BoolType()  , c_bool(False))
        self.ctx.install_const('lf'        , typesys.CharType()  , c_char('\n'))
        self.ctx.install_const('maxint'    , typesys.SIntType(16), c_int((2 ** 15) - 1, 16))
        self.ctx.install_const('maxlongint', typesys.SIntType(32), c_int((2 ** 31) - 1, 32))
        self.ctx.install_const('maxword'   , typesys.UIntType(16), c_int((2 ** 16) - 1, 16))
        self.ctx.install_const('true'      , typesys.BoolType()  , c_bool(True))

    def visit(self, node, arg=None):
        try:
            # print node, node.position
            return visitor.DefaultVisitor.visit(self, node, arg)
        except CodegenException as e:
            log.e('codegen', str(e))
        except symtab.SymtabException as e:
            log.e('codegen', str(e))

    # scope stuff

    def visit_ProgramNode(self, node, arg=None):
        assert isinstance(node, ast.ProgramNode)

        name = node.identifier.accept(self)
        if name:
            self.ctx.module.name = name

        # TODO(Cholerae): define standard library
        builtin.define_builtinlib(self.ctx)

        self.ctx.enter_scope()

        func = builtin.f_main(self.ctx.module)
        block = func.append_basic_block("entry")
        self.ctx.builder = ir.IRBuilder(block)
        self.ctx.function = func

        # argv = self.ctx.module.get_global("frontend.argv")
        # argv_value = self.ctx.builder.load(argv)
        # argc = self.ctx.module.get_global("frontend.argc")
        # argc_value = self.ctx.builder.load(argc)
        # self.ctx.builder.store(func.args[0], argc_value)
        # self.ctx.builder.store(func.args[1], argv_value)

        if node.block:
            node.block.accept(self)

        self.ctx.builder.ret_void()

        self.ctx.exit_scope()

    def visit_FunctionHeadNode(self, node, arg=None):
        
        assert (isinstance(node, ast.FunctionHeadNode) or
                isinstance(node, ast.ProcedureHeadNode))

        ty = node.type
        if ty.scope_level > 0:
            # Nested function require a hook to its parent scope
            # we append them at the end of the parameter list
            scope_ty = typesys.ScopeHookType(ty.name)
            index = 0
            for sym in self.ctx.symbols:
                # Ignore constants
                if isinstance(sym.handle, ir.Constant):
                    continue

                # when several scopes are nested, we just point
                # at the same place
                if isinstance(sym.type, typesys.ScopeFieldType):
                    sym_ty = sym.type.type
                else:
                    sym_ty = sym.type

                field = typesys.ScopeFieldType(sym.name, sym_ty)
                field.index = index
                scope_ty.fields.append(field)

                index += 1

            if index > 0:
                scope_ty = typesys.ReferenceType(scope_ty)
                param_ty = typesys.ParameterType('hook', scope_ty)
                ty.params.append(param_ty)
                ty.scope_hook = True

        try:
            # handle_ = self.ctx.module.get_global(ty.namespace)
            # TODO(Cholerae): replace globals[ty.namespace] by get_global(ty.namespace)
            # Just for fuck llvmlite. See pull#273.
            handle_ = self.ctx.module.globals[ty.namespace]
        except:
            type_ = self.ctx.typegen(ty)
            handle_ = ir.Function(self.ctx.module, type_, ty.namespace)
            handle_.linkage = 'internal'

        return self.ctx.install_function(ty.name, ty, handle_)

    def visit_ProcedureHeadNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        return self.visit_FunctionHeadNode(node, arg)

    def visit_FunctionNode(self, node, arg=None):
        assert (isinstance(node, ast.FunctionNode) or
                isinstance(node, ast.ProcedureNode))

        func = node.header.accept(self)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        self.ctx.function = func.handle
        self.ctx.builder = ir.IRBuilder(
                              func.handle.append_basic_block("func.entry"))

        # allocate arguments
        for arg, param in zip(self.ctx.function.args, func.type.params):
            handle = self.ctx.builder.alloca(arg.type, name=param.name)
            self.ctx.builder.store(arg, handle)

            param_ty = param.type
            if isinstance(param_ty, typesys.ReferenceType):
                handle = self.ctx.builder.load(handle)
                param_ty = param_ty.referee

            # install (and load) variables declared on a parent stack
            if isinstance(param_ty, typesys.ScopeHookType):
                for field in param_ty.fields:
                    indices = [c_int(0), c_int(field.index)]
                    field_handle = self.ctx.builder.gep(handle, indices)
                    field_handle = self.ctx.builder.load(
                                        field_handle, field.name)
                    self.ctx.install_symbol(field.name, field, field_handle)

            else:
                self.ctx.install_symbol(param.name, param_ty, handle)

        # generate return value
        if not isinstance(func.type.ret, typesys.VoidType):
            type_ = self.ctx.typegen(func.type.ret)
            value = self.ctx.builder.alloca(type_, name=func.type.name)
            self.ctx.install_symbol(func.type.name, func.type.ret, value)

        if node.block:
            node.block.accept(self)

        if not isinstance(func.type.ret, typesys.VoidType):
            ret = self.ctx.builder.load(value)
            self.ctx.builder.ret(ret)
        else:
            self.ctx.builder.ret_void()

        self.ctx.exit_scope()
        self.func_scope_level -= 1

    def visit_ProcedureNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureNode)

        return self.visit_FunctionNode(node, arg)

    def visit_WithNode(self, node, arg=None):
        assert isinstance(node, ast.WithNode)

        self.ctx.enter_scope()

        for rec in node.rec_var_list.accept(self):
            ty = rec.type

            if isinstance(ty, typesys.ReferenceType):
                ty = ty.referee

            if isinstance(ty, typesys.ScopeFieldType):
                ty = ty.type

            # install regular fields in the symbol table
            offset = 0
            for field in ty.fields:
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(rec.handle, indices)
                self.ctx.install_symbol(field.name, field.type, handle)

                offset += 1

            if ty.variant is None:
                continue

            # install the selector in the symbol table
            # I'm not really sure what it is used for,
            # but it can hold values
            if ty.variant.selector:
                selector = ty.variant.selector
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(rec.handle, indices)
                self.ctx.install_symbol(selector.name, selector.type)

                offset += 1

            # install the variants in the symbol table
            # each variant case is a record on its own
            for case in ty.variant.cases:
                case_offset = 0
                for field in case.fields:
                    indices = [c_int(0), c_int(offset)]
                    handle = self.ctx.builder.gep(rec.handle, indices)

                    type_ = self.ctx.typegen(case)
                    handle = self.ctx.builder.bitcast(handle,
                                                      lc.Type.pointer(type_))

                    indices = [c_int(0), c_int(case_offset)]
                    handle = self.ctx.builder.gep(handle, indices)

                    self.ctx.install_symbol(field.name, field.type, handle)

                    case_offset += 1

        if node.statement_list:
            node.statement_list.accept(self)

        self.ctx.exit_scope()

    # declarations

    def visit_LabelDeclNode(self, node, arg=None):
        assert isinstance(node, ast.LabelDeclNode)

        for lbl in node.label_list.accept(self, arg):
            block = symtab.GotoBlock()
            self.ctx.install_goto(lbl, block)

    def visit_ConstDeclNode(self, node, arg=None):
        assert isinstance(node, ast.ConstDeclNode)

        name = node.identifier.accept(self)
        expr = node.expr.accept(self)

        self.ctx.install_const(name, node.type, expr.handle)

    def visit_TypeDeclNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclNode)

        name = node.identifier.accept(self)
        node.type_denoter.accept(self)  # will install enums

        self.ctx.install_typedef(name, node.type)

    def visit_EnumTypeNode(self, node, arg=None):
        assert isinstance(node, ast.EnumTypeNode)

        names = node.identifier_list.accept(self)
        type_ = self.ctx.typegen(node.type)

        for i, name in enumerate(names):
            value = ir.Constant(type_, i)
            self.ctx.install_const(name, node.type, value)

    def visit_VarDeclNode(self, node, arg=None):
        assert isinstance(node, ast.VarDeclNode)

        names = node.identifier_list.accept(self)
        node.type_denoter.accept(self)  # installs constants from sets etc
        type_ = self.ctx.typegen(node.type)

        for name in names:
            if self.func_scope_level <= 0:
                value = ir.GlobalVariable(self.ctx.module, type_, name)
                value.linkage = 'internal'
                value.initializer = ir.Constant(type_, ir.Undefined)
            else:
                value = self.ctx.builder.alloca(type_, name=name)

            self.ctx.install_symbol(name, node.type, value)

    # branching

    def visit_IfNode(self, node, arg=None):
        assert isinstance(node, ast.IfNode)

        bb_true = self.ctx.function.append_basic_block('if.true')
        bb_endif = self.ctx.function.append_basic_block('if.end')

        if node.iffalse:
            bb_false = self.ctx.function.append_basic_block('if.false')
        else:
            bb_false = bb_endif

        cond = node.expr.accept(self)

        self.ctx.builder.cbranch(cond.handle, bb_true, bb_false)

        self.ctx.builder.position_at_end(bb_true)
        if node.iftrue:
            node.iftrue.accept(self)

        self.ctx.builder.branch(bb_endif)

        if node.iffalse:
            self.ctx.builder.position_at_end(bb_false)
            node.iffalse.accept(self)
            self.ctx.builder.branch(bb_endif)

        self.ctx.builder.position_at_end(bb_endif)

    def visit_WhileNode(self, node, arg=None):
        assert isinstance(node, ast.WhileNode)

        bb_cond = self.ctx.function.append_basic_block('while.cond')
        bb_body = self.ctx.function.append_basic_block('while.body')
        bb_exit = self.ctx.function.append_basic_block('while.exit')

        # cond block
        self.ctx.builder.branch(bb_cond)
        self.ctx.builder.position_at_end(bb_cond)
        cond = node.cond.accept(self)
        self.ctx.builder.cbranch(cond.handle, bb_body, bb_exit)

        # body block
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_cond)

        # exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_RepeatNode(self, node, arg=None):
        assert isinstance(node, ast.RepeatNode)

        bb_body = self.ctx.function.append_basic_block('repeat.body')
        bb_cond = self.ctx.function.append_basic_block('repeat.cond')
        bb_exit = self.ctx.function.append_basic_block('repeat.exit')

        # body block
        self.ctx.builder.branch(bb_body)
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_cond)

        # cond block
        self.ctx.builder.position_at_end(bb_cond)
        cond = node.cond.accept(self)
        self.ctx.builder.cbranch(cond.handle, bb_exit, bb_body)

        # exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_ForNode(self, node, arg=None):
        assert isinstance(node, ast.ForNode)

        bb_cond = self.ctx.function.append_basic_block('for.cond')
        bb_incr = self.ctx.function.append_basic_block('for.incr')
        bb_body = self.ctx.function.append_basic_block('for.body')
        bb_exit = self.ctx.function.append_basic_block('for.exit')

        # generate initializer
        name = node.var.accept(self)
        var = self.ctx.find_symbol(name)
        value = node.value_start.accept(self)

        self.ctx.builder.store(value.handle, var.handle)
        self.ctx.builder.branch(bb_cond)

        # generate condition
        self.ctx.builder.position_at_end(bb_cond)
        handle = self.ctx.builder.load(var.handle)
        var_value = symtab.ConstantValue(handle, var.type)
        value = node.value_end.accept(self)

        if node.direction == 'to':
            cond = self.ctx.cmp_le(var_value, value)
        elif node.direction == 'downto':
            cond = self.ctx.cmp_ge(var_value, value)
        else:
            raise CodegenNodeException(node, "unknown loop direction '%s'" %
                                             node.direction)

        self.ctx.builder.cbranch(cond.handle, bb_body, bb_exit)

        # generate increment
        self.ctx.builder.position_at_end(bb_incr)

        handle = self.ctx.builder.load(var.handle)
        var_value = symtab.ConstantValue(handle, var.type)
        one = symtab.ConstantValue(c_bool(1), typesys.BoolType())
        one = self.ctx.cast(one, var.type)

        if node.direction == 'to':
            var_value = self.ctx.add(var_value, one)
        elif node.direction == 'downto':
            var_value = self.ctx.sub(var_value, one)
        else:
            raise CodegenNodeException(node, "unknown loop direction '%s'" %
                                             node.direction)

        self.ctx.builder.store(var_value.handle, var.handle)
        self.ctx.builder.branch(bb_cond)

        # generate body
        self.ctx.builder.position_at_end(bb_body)
        node.body.accept(self)
        self.ctx.builder.branch(bb_incr)

        # move to exit block
        self.ctx.builder.position_at_end(bb_exit)

    def visit_CaseStatementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseStatementNode)

        bb_switch = self.ctx.function.append_basic_block('switch.entry')

        value = node.case_index.accept(self)

        self.ctx.builder.branch(bb_switch)
        self.ctx.builder.position_at_end(bb_switch)

        if node.case_list_element_list:
            bb_cases = node.case_list_element_list.accept(self)
        else:
            bb_cases = []

        bb_else = self.ctx.function.append_basic_block('switch.case.else')
        bb_exit = self.ctx.function.append_basic_block('switch.exit')

        self.ctx.builder.position_at_end(bb_else)
        if node.otherwise:
            node.otherwise.accept(self)
        self.ctx.builder.branch(bb_exit)

        self.ctx.builder.position_at_end(bb_switch)
        switch = self.ctx.builder.switch(value.handle, bb_else, len(bb_cases))

        for case_val, case_enter, case_exit in bb_cases:
            self.ctx.builder.position_at_end(case_exit)
            self.ctx.builder.branch(bb_exit)
            switch.add_case(case_val.handle, case_enter)

        self.ctx.builder.position_at_end(bb_exit)

    def visit_CaseListElementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseListElementNode)

        values = node.case_constant_list.accept(self)

        l = []
        for val in values:
            bb_enter = self.ctx.function.append_basic_block(
                                        'switch.case.enter')
            bb_exit = self.ctx.function.append_basic_block('switch.case.exit')
            self.ctx.builder.position_at_end(bb_enter)

            if node.statement:
                node.statement.accept(self)

            self.ctx.builder.branch(bb_exit)

            l.append((val, bb_enter, bb_exit))

        return l

    def visit_CaseConstNode(self, node, arg=None):
        assert isinstance(node, ast.CaseConstNode)

        return node.constant.accept(self, arg)

    def visit_CaseRangeNode(self, node, arg=None):
        assert isinstance(node, ast.CaseRangeNode)

        lo = node.type.lo
        hi = node.type.hi

        l = []

        for val in range(lo, hi + 1):
            type_ = self.ctx.typegen(node.type)
            handle = lc.Constant.int(type_, val)
            l.append(symtab.ConstantValue(handle, node.type))

        return l

    def visit_GotoNode(self, node, arg=None):
        assert isinstance(node, ast.GotoNode)

        lbl = node.label.accept(self, arg)
        block = self.ctx.find_goto(lbl)

        jmp_bb = self.ctx.function.append_basic_block('jump.%s' % lbl)
        cont_bb = self.ctx.function.append_basic_block('unreachable.%s' % lbl)

        self.ctx.builder.branch(jmp_bb)
        block.entries.append(jmp_bb)

        if block.handle:
            self.ctx.builder.position_at_end(jmp_bb)
            self.ctx.builder.branch(block.handle)

        # might be unreachable
        self.ctx.builder.position_at_end(cont_bb)

    def visit_LabeledStatementNode(self, node, arg=None):
        assert isinstance(node, ast.LabeledStatementNode)

        lbl = node.label.accept(self)
        block = self.ctx.find_goto(lbl)

        block.handle = self.ctx.function.append_basic_block('stmt.%s' % lbl)
        self.ctx.builder.branch(block.handle)

        for jmp_bb in block.entries:
            self.ctx.builder.position_at_end(jmp_bb)
            self.ctx.builder.branch(block.handle)

        self.ctx.builder.position_at_end(block.handle)
        node.stmt.accept(self)

    # expressions

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        expr = node.expr.accept(self)

        if node.name == '-':
            return self.ctx.neg(expr)
        if node.name == '+':
            return expr
        elif node.name == 'not':
            return self.ctx.not_(expr)
        else:
            raise CodegenNodeException(node, "unknown unary operator '%s'" %
                                             node.name)

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        sign = node.op.name
        left = node.left.accept(self)
        right = node.right.accept(self)

        ops = {'+': self.ctx.add,
               '-': self.ctx.sub,
               '*': self.ctx.mul,
               '/': self.ctx.div,
               'div': self.ctx.div,
               'mod': self.ctx.mod,
               'and': self.ctx.and_,
               'or': self.ctx.or_,
               '=': self.ctx.cmp_eq,
               '<>': self.ctx.cmp_neq,
               '>': self.ctx.cmp_gt,
               '>=': self.ctx.cmp_ge,
               '<': self.ctx.cmp_lt,
               '<=': self.ctx.cmp_le,
               'in': self.ctx.in_}

        if sign in ops.keys():
            op = ops[sign]
            return op(left, right)

        raise CodegenNodeException(node, "unknown binary operator '%s'" % sign)

    # statements

    def visit_TypeConvertNode(self, node, arg=None):
        assert isinstance(node, ast.TypeConvertNode)

        value = node.child.accept(self)
        converted = self.ctx.coerce(value, node.type)

        if not converted:
            converted = self.ctx.cast(value, node.type)

        return converted

    def visit_AssignmentNode(self, node, arg=None):
        assert isinstance(node, ast.AssignmentNode)

        var = node.var_access.accept(self)
        expr = node.expr.accept(self)

        if isinstance(expr.type, typesys.StringType):
            types = []
            types.append(ir.PointerType(self.ctx.typegen(var.type.element)))
            types.append(ir.PointerType(self.ctx.typegen(expr.type.element)))
            types.append(ir.IntType(32))

            func = self.ctx.module.declare_intrinsic('llvm.memcpy', types)
            args = []
            args.append(self.ctx.builder.bitcast(var.handle, types[0]))
            args.append(self.ctx.builder.bitcast(expr.handle, types[1]))
            args.append(c_int(expr.type.range.hi - expr.type.range.lo + 1))
            args.append(c_int(0))
            args.append(c_bool(False))
            self.ctx.builder.call(func, args)
        else:
            self.ctx.builder.store(expr.handle, var.handle)

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        return node.expr.accept(self)

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)
        if node.arg_list:
            args = node.arg_list.accept(self)
        else:
            args = []

        # User-defined functions
        try:
            func = self.ctx.find_function(name)
            return self.ctx.call(func, args)
        except symtab.SymtabException:
            pass

        # Built-in functions
        try:
            func, args = self.ctx.translate_call(name, args)
            return self.ctx.call(func, args)
        except CodegenException:
            pass

        # Transfer function for enums
        try:
            ty = self.ctx.find_typedef(name)
        except symtab.SymtabException:
            raise CodegenNodeException(node, "call to unknown function '%s'" %
                                              name)
        if len(args) != 1:
            raise CodegenNodeException(node,
                                       "the transfer function '%s' require "
                                       "exactly one argument" % name)

        value = self.ctx.cast(args[0], ty)
        if not value:
            raise CodegenNodeException(node, "casting from '%s' to '%s'" %
                                             (args[0].type, ty))

        return value

    # variable access

    def visit_VarAccessNode(self, node, arg=None):
        assert isinstance(node, ast.VarAccessNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_symbol(name)
            if isinstance(sym.type, typesys.ReferenceType):
                handle = self.ctx.builder.load(sym.handle)
                return symtab.VariableValue(handle, sym.type.referee)
            else:
                return sym
        except symtab.SymtabException:
            pass

        # User-defined functions
        try:
            func = self.ctx.find_function(name)
            return self.ctx.call(func)
        except symtab.SymtabException:
            pass

        # Built-in functions
        try:
            func, _ = self.ctx.translate_call(name, [])
            return self.ctx.call(func)
        except CodegenException:
            pass

        raise CodegenNodeException(node, "call to unknown function '%s'" %
                                         name)

    def visit_PointerAccessNode(self, node, arg=None):
        assert isinstance(node, ast.PointerAccessNode)

        var = node.var_access.accept(self)
        load = self.ctx.builder.load(var.handle)

        return symtab.ConstantValue(load, node.type)


    def visit_IndexedVarNode(self, node, field=None):
        assert isinstance(node, ast.IndexedVarNode)

        arr = node.var_access.accept(self)
        arr_ty = arr.type

        indices = [c_int(0)]

        for i in node.index_expr_list.accept(self):
            width = i.type.width

            value = c_int(arr_ty.range.lo, width)
            value = self.ctx.builder.sub(i.handle, value)

            indices.append(value)

            arr_ty = arr_ty.element

        handle = self.ctx.builder.gep(arr.handle, indices)

        return symtab.VariableValue(handle, node.type)

    def visit_FieldAccessNode(self, node, arg=None):
        assert isinstance(node, ast.FieldAccessNode)

        name = node.identifier.accept(self)
        var = node.var_access.accept(self)

        offset = 0
        for field in node.var_access.type.fields:
            if field.name == name:
                indices = [c_int(0), c_int(offset)]
                handle = self.ctx.builder.gep(var.handle, indices)
                return symtab.VariableValue(handle, node.type)
            else:
                offset += 1

        variant = node.var_access.type.variant
        if not variant:
            raise CodegenNodeException(node, "unknown field '%s'" % name)

        elif variant.selector.name == name:
            indices = [c_int(0), c_int(offset)]
            handle = self.ctx.builder.gep(var.handle, indices)
            return symtab.VariableValue(handle, node.type)

        offset += 1

        for case in variant.cases:
            case_offset = 0
            for field in case.fields:
                if field.name == name:
                    indices = [c_int(0), c_int(offset)]
                    handle = self.ctx.builder.gep(var.handle, indices)

                    type_ = self.ctx.typegen(case)
                    handle = self.ctx.builder.bitcast(handle,
                                                      ir.PointerType(type_))

                    indices = [c_int(0), c_int(case_offset)]
                    handle = self.ctx.builder.gep(handle, indices)

                    return symtab.VariableValue(handle, field.type)
                else:
                    case_offset += 1

        raise CodegenNodeException(node, "unknown field '%s'" % name)

    def visit_VarReferenceNode(self, node, arg=None):
        assert isinstance(node, ast.VarReferenceNode)

        sym = node.var_access.accept(self)
        ty = typesys.ReferenceType(sym.type)

        return symtab.VariableValue(sym.handle, ty)

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        var = node.var_access.accept(self)
        if isinstance(var, symtab.ConstantValue):
            return var

        load = self.ctx.builder.load(var.handle)

        if (isinstance(node.type, typesys.IntRangeType) or
            isinstance(node.type, typesys.CharRangeType)):
            type_ = self.ctx.typegen(node.type)
            lo = ir.Constant(type_, node.type.lo)
            hi = ir.Constant(type_, node.type.hi)

            md = lc.MetaData.get(self.ctx.module, [lo, hi])
            load.set_metadata('range', md)

        return symtab.ConstantValue(load, node.type)

    # terminals

    def visit_LabelNode(self, node, arg=None):
        assert isinstance(node, ast.LabelNode)

        return node.name

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        type_ = self.ctx.typegen(node.type)
        value = ir.Constant(type_, ord(node.value))

        return symtab.ConstantValue(value, node.type)

    def visit_IntegerNode(self, node, arg=None):
        assert isinstance(node, ast.IntegerNode)

        type_ = self.ctx.typegen(node.type)
        value = ir.Constant(type_, node.value)

        return symtab.ConstantValue(value, node.type)

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        type_ = self.ctx.typegen(node.type)
        value = ir.Constant(type_, node.value)

        return symtab.ConstantValue(value, node.type)

    def visit_SetNode(self, node, arg=None):
        assert isinstance(node, ast.SetNode)

        members = node.member_list.accept(self)

        ty = typesys.UIntType(node.type.width)
        handle = c_int(0, node.type.width)

        for m in members:
            m = self.ctx.cast(m, ty)
            one = c_int(1, node.type.width)

            if not self.ctx.builder:
                one = one.shl(m.handle)
                handle = handle.or_(one)
            else:
                one = self.ctx.builder.shl(one, m.handle)
                handle = self.ctx.builder.or_(handle, one)

        return symtab.ConstantValue(handle, ty)

    def visit_SetMemberRangeNode(self, node, arg=None):
        assert isinstance(node, ast.SetMemberRangeNode)

        start = node.member.accept(self)
        stop = node.expr.accept(self)

        if not hasattr(start.handle, 'z_ext_value'):
            raise CodegenNodeException(node.member,
                                       "todo: variables in set ranges")

        if not hasattr(stop.handle, 'z_ext_value'):
            raise CodegenNodeException(node.expr,
                                       "todo: variables in set ranges")

        # TODO(Cholerae): allow set range members to be variables
        lo = start.handle.z_ext_value
        hi = stop.handle.z_ext_value

        l = []

        for val in range(lo, hi + 1):
            type_ = self.ctx.typegen(node.type)
            handle = ir.Constant(type_, val)
            l.append(symtab.ConstantValue(handle, start.type))

        return l

    def visit_SetEmptyNode(self, node, arg=None):
        assert isinstance(node, ast.SetEmptyNode)

        type_ = self.ctx.typegen(node.type)
        value = ir.Constant(type_, 0)

        return symtab.ConstantValue(value, node.type)

    def visit_NullNode(self, node, arg=None):
        assert isinstance(node, ast.NullNode)

        type_ = self.ctx.typegen(node.type)
        value = ir.Constant(type_, None)

        return symtab.ConstantValue(value, node.type)

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        return self.ctx.c_string(node.value)
