'''
Type checker and caster for frontend syntax trees.
'''
from __future__ import absolute_import, print_function

import copy

from frontend import ast
from frontend import typesys
from frontend import symtab
from frontend import visitor
from frontend import log


def _upcast_ret(lhs=None, rhs=None):
    if not rhs:
        return lhs, lhs
    else:
        return lhs, rhs


def upcast_int(lhs, rhs):
    '''
    make sure lhs and rhs is of the same integer type.
    upcasts to the smallest possible width. when signess differ,
    the largest width * 2 will be used.
    '''
    if not isinstance(lhs, typesys.IntType):
        return _upcast_ret()
    if not isinstance(rhs, typesys.IntType):
        return _upcast_ret()

    if (lhs.value is not None and
        rhs.lo <= lhs.value <= rhs.hi):
        return _upcast_ret(rhs)

    elif (rhs.value is not None and
        lhs.lo <= rhs.value <= lhs.hi):
        return _upcast_ret(lhs)

    elif lhs.signed == rhs.signed:
        if lhs.width >= rhs.width:
            return _upcast_ret(lhs)
        else:
            return _upcast_ret(rhs)

    elif lhs.signed and rhs.unsigned:
        if lhs.width > rhs.width:
            width = lhs.width
        else:
            width = rhs.width * 2

        return _upcast_ret(typesys.SIntType(width))

    elif lhs.unsigned and rhs.signed:
        if lhs.width < rhs.width:
            width = rhs.width
        else:
            width = lhs.width * 2

        return _upcast_ret(typesys.SIntType(width))

    else:
        return _upcast_ret()


def upcast_real(lhs, rhs):
    '''
    upcast lhs and rhs to a real number.
    NOTE: assumes that all integers (signed or unsigned) will fit
    inside a float.
    '''
    if (isinstance(lhs, typesys.RealType) and
        isinstance(rhs, typesys.RealType)):
        if lhs.width >= rhs.width:
            return _upcast_ret(lhs)
        else:
            return _upcast_ret(rhs)

    elif isinstance(lhs, typesys.RealType):
        return _upcast_ret(lhs)

    elif isinstance(rhs, typesys.RealType):
        return _upcast_ret(rhs)

    else:
        return _upcast_ret(typesys.FloatType())


def upcast(lhs, rhs):
    if lhs == rhs:
        return _upcast_ret(lhs, rhs)

    elif isinstance(lhs, typesys.AnyType):
        return _upcast_ret(rhs)

    elif isinstance(rhs, typesys.AnyType):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, typesys.RealType) or
        isinstance(rhs, typesys.RealType)):
        return upcast_real(lhs, rhs)

    elif (isinstance(lhs, typesys.IntType) and
        isinstance(rhs, typesys.IntType)):
        return upcast_int(lhs, rhs)

    elif (isinstance(lhs, typesys.SetType) and
        isinstance(rhs, typesys.EmptySetType)):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, typesys.EmptySetType) and
        isinstance(rhs, typesys.SetType)):
        return _upcast_ret(rhs)

    elif (isinstance(lhs, typesys.PointerType) and
        isinstance(rhs, typesys.PointerType) and
        isinstance(lhs.pointee, typesys.AnyType)):
        return _upcast_ret(rhs)

    elif (isinstance(lhs, typesys.PointerType) and
        isinstance(rhs, typesys.PointerType) and
        isinstance(rhs.pointee, typesys.AnyType)):
        return _upcast_ret(lhs)

    elif (isinstance(lhs, typesys.SetType) and
        isinstance(rhs, typesys.SetType)):
        lo = min(lhs.element.lo, rhs.element.lo)
        hi = max(lhs.element.hi, rhs.element.hi)

        if (isinstance(lhs.element, typesys.IntType) and
            isinstance(rhs.element, typesys.IntType)):
            el_ty = typesys.IntRangeType(lo, hi)
        elif (isinstance(lhs.element, typesys.CharType) and
              isinstance(rhs.element, typesys.CharType)):
            el_ty = typesys.CharRangeType(lo, hi)
        else:
            return _upcast_ret()

        return _upcast_ret(typesys.SetType(el_ty))

    else:
        return _upcast_ret()


def upcast_arithmetic(lhs, rhs, sign=None):

    if sign == '/':
        return _upcast_ret(typesys.DoubleType())

    elif (isinstance(lhs, typesys.RealType) or
        isinstance(rhs, typesys.RealType)):
        if sign in ['div', 'mod']:
            return _upcast_ret()
        else:
            return _upcast_ret(typesys.DoubleType())

    def _int_prepare(x):
        if isinstance(x, typesys.IntType):
            x.value = None

            if x.width < 16:
                if x.signed:
                    x = typesys.SIntType(16)
                else:
                    x = typesys.UIntType(16)

        return x

    lhs = _int_prepare(lhs)
    rhs = _int_prepare(rhs)

    return upcast(lhs, rhs)


def upcast_relational(lhs, rhs, sign=None):

    # upcast left hand operator to set member
    if ((isinstance(lhs, typesys.IntType) or
         isinstance(lhs, typesys.CharType)) and
        isinstance(rhs, typesys.SetType) and
        sign == 'in'):
        return _upcast_ret(rhs.element, rhs)

    elif ((isinstance(lhs, typesys.IntType) or
         isinstance(lhs, typesys.CharType)) and
        isinstance(rhs, typesys.EmptySetType) and
        sign == 'in'):
        return _upcast_ret(lhs, typesys.SetType(lhs))

    elif sign == 'in':
        return _upcast_ret()

    return upcast(lhs, rhs)


class NodeException(Exception):

    def __init__(self, node, msg):
        Exception.__init__(self)
        self.msg = msg
        self.node = node

    def __str__(self):
        pos = self.node.position
        if not pos:
            pos = '?'

        return str(pos) + ':' + str(self.msg)


def downcast_assignment(source, target, pos):

    if source == target:
        return target

    # Int --> Int
    if (isinstance(source, typesys.IntType) and
        isinstance(target, typesys.IntType)):

        # Avoid warning message
        if (source.hi <= target.hi and
            source.lo >= target.lo):
            return target

        if(source.value is not None and
           target.lo <= source.value and
           target.hi >= source.value):
            return target

        if source.value:
            source = source.value

        log.w('typecheck', "%s:casting from '%s' to '%s'" % (pos, source,
                                                           target))
        return target

    # Int --> Real
    elif (isinstance(source, typesys.IntType) and
        isinstance(target, typesys.RealType)):
        return target

    # Real --> Real
    elif (isinstance(source, typesys.RealType) and
          isinstance(target, typesys.RealType)):
            return target

    # Set --> Set
    elif (isinstance(source, typesys.SetType) and
          isinstance(target, typesys.SetType)):
        return target

    # EmptySet --> Set
    elif (isinstance(source, typesys.EmptySetType) and
          isinstance(target, typesys.SetType)):
        return target

    # Any
    elif (isinstance(target, typesys.AnyType)):
        return source

    # Any
    elif (isinstance(source, typesys.AnyType)):
        return target

    # Reference --> Reference of Any
    elif (isinstance(source, typesys.ReferenceType) and
          isinstance(target, typesys.ReferenceType) and
          isinstance(target.referee, typesys.AnyType)):
        return target

    # Array --> Reference of Any
    elif (isinstance(source, typesys.ArrayType) and
          isinstance(target, typesys.ReferenceType) and
          isinstance(target.referee, typesys.AnyType)):
        return target

    # Pointer --> Pointer of Any
    elif (isinstance(source, typesys.PointerType) and
          isinstance(target, typesys.PointerType) and
          isinstance(target.pointee, typesys.AnyType)):
        return target

    # Pointer of Any (Null) --> Pointer
    elif (isinstance(source, typesys.PointerType) and
          isinstance(target, typesys.PointerType) and
          isinstance(source.pointee, typesys.AnyType)):
        return target

    # Reference --> Reference
    elif (isinstance(source, typesys.ReferenceType) and
          isinstance(target, typesys.ReferenceType) and
          source.referee.width == target.referee.width and
          downcast_assignment(source.referee, target.referee, pos)):
        return target

    # Array --> Array (within range, same type width)
    elif (isinstance(source, typesys.ArrayType) and
          isinstance(target, typesys.ArrayType) and
          source.element.width == target.element.width and
          source.length <= target.length):
        return target

    return None


class ConstantEvalVisitor(visitor.DefaultVisitor):

    def __init__(self, ctx):
        self.ctx = ctx

    def default_visit(self, node, arg=None):
        value = visitor.DefaultVisitor.default_visit(self, node, arg)
        if value is None:
            return node
        else:
            return value

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        expr = node.expr.accept(self)

        if isinstance(expr, ast.Node):
            raise NodeException(expr, "illegal constant expression")

        if node.name == '-':
            op = lambda val: (-val)
        elif node.name == '+':
            op = lambda val: (+val)
        elif node.name == 'not':
            op = lambda val: (~val)
        else:
            raise NodeException(node, "unknown unary operator '%s'" %
                                      node.name)

        return op(expr)

    def visit_OpNode(self, node, arg=None):
        
        assert isinstance(node, ast.OpNode)

        if node.name == '+':
            return lambda lhs, rhs: (lhs + rhs)
        if node.name == '-':
            return lambda lhs, rhs: (lhs - rhs)
        if node.name == '*':
            return lambda lhs, rhs: (lhs * rhs)
        if node.name == 'or':
            return lambda lhs, rhs: (lhs | rhs)
        if node.name == '/':
            return lambda lhs, rhs: (lhs / rhs)
        if node.name == 'div':
            return lambda lhs, rhs: (int(lhs) / int(rhs))
        if node.name == 'mod':
            return lambda lhs, rhs: (lhs % rhs)
        if node.name == 'and':
            return lambda lhs, rhs: (lhs & rhs)
        if node.name == '=':
            return lambda lhs, rhs: (lhs == rhs)
        if node.name == '<>':
            return lambda lhs, rhs: (lhs != rhs)
        if node.name == '<':
            return lambda lhs, rhs: (lhs < rhs)
        if node.name == '<=':
            return lambda lhs, rhs: (lhs <= rhs)
        if node.name == '>':
            return lambda lhs, rhs: (lhs > rhs)
        if node.name == '>=':
            return lambda lhs, rhs: (lhs >= rhs)

        raise NodeException(node, "unknown binary operator '%s'" % node.name)

    def visit_BinaryOpNode(self, node, arg=None):
        
        assert isinstance(node, ast.BinaryOpNode)

        left = node.left.accept(self)
        right = node.right.accept(self)

        if isinstance(left, ast.Node):
            raise NodeException(left, "illegal constant expression")

        if isinstance(right, ast.Node):
            raise NodeException(right, "illegal constant expression")

        op = node.op.accept(self)

        return op(left, right)

    def visit_RangeNode(self, node, arg=None):
        
        assert isinstance(node, ast.RangeNode)

        node.start = node.start.accept(self, arg)
        node.stop = node.stop.accept(self, arg)

        return node

    def visit_CaseConstNode(self, node, arg=None):
        assert isinstance(node, ast.CaseConstNode)

        return node.constant.accept(self, arg)

    def visit_IntegerNode(self, node, arg=None):
        assert isinstance(node, ast.IntegerNode)

        return node.value

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        return node.value

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        return node.value

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        return node.value

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        return node.var_access.accept(self)

    def visit_VarAccessNode(self, node, field):
        assert isinstance(node, ast.VarAccessNode)

        if not isinstance(node.identifier, ast.IdentifierNode):
            raise NodeException(node, "illegal constant expression")

        sym = self.ctx.find_symbol(node.identifier.name)

        return sym.handle

    def visit_TypeConvertNode(self, node, field):
        assert isinstance(node, ast.TypeConvertNode)

        return node.child.accept(self)



class DeferredTypeVisitor(visitor.DefaultVisitor):

    def __init__(self, ctx):
        self.ctx = ctx

    def default_visit(self, node, arg=None):
        # Ugly monkey patching required when named types are used
        # before being defined.
        if isinstance(node.type, typesys.DeferredType):
            ty = self.ctx.find_typedef(node.type.name)
            node.type.__class__ = ty.__class__
            node.type.__dict__ = ty.__dict__

        for c in node.children:
            if c is not None:
                c.accept(self)


class TypeSetVisitor(visitor.DefaultVisitor):

    def __init__(self):
        self.ctx = symtab.SymbolTable()
        self.module = None
        self.ctx.enter_scope()
        self.func_scope_level = 0

        self.ctx.install_typedef('Boolean' , typesys.BoolType())
        self.ctx.install_typedef('char'    , typesys.CharType())
        self.ctx.install_typedef('integer' , typesys.SIntType(16))
        self.ctx.install_typedef('word'    , typesys.UIntType(16))
        self.ctx.install_typedef('longint' , typesys.SIntType(32))
        self.ctx.install_typedef('double'  , typesys.DoubleType())
        self.ctx.install_typedef('real'    , typesys.FloatType())
        # TODO: add text

        self.ctx.install_const('cr'        , typesys.CharType('\r')  , '\r')
        self.ctx.install_const('false'     , typesys.BoolType(False)  , False)
        self.ctx.install_const('lf'        , typesys.CharType('\n')  , '\n')
        self.ctx.install_const('maxint'    , typesys.SIntType(16, (2 ** 15) - 1), (2 ** 15) - 1)
        self.ctx.install_const('maxlongint', typesys.SIntType(32, (2 ** 31) - 1), (2 ** 31) - 1)
        self.ctx.install_const('maxword'   , typesys.UIntType(16, (2 ** 16) - 1), (2 ** 16) - 1)
        self.ctx.install_const('true'      , typesys.BoolType(True)  , True)
        # TODO: add eol

        # pointer --> VOID
        ty = typesys.FunctionType('frontend', 'new')
        param = typesys.AnyType()
        param = typesys.ReferenceType(param)
        param = typesys.ParameterType('ptr', param)
        ty.params.append(param)
        self.ctx.install_function(ty.name, ty)

        # ordinal --> INTEGER
        ty = typesys.FunctionType('frontend', 'ord', typesys.SIntType(16))
        ty.params.append(typesys.ParameterType(ty.name, typesys.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # int-type --> CHAR
        ty = typesys.FunctionType('frontend', 'chr', typesys.CharType())
        ty.params.append(typesys.ParameterType('int', typesys.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        # TODO: ordinal --> same as input
        ty = typesys.FunctionType('frontend', 'pred', typesys.AnyType())
        ty.params.append(typesys.ParameterType('ordinal', typesys.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # TODO: ordinal --> same as input
        ty = typesys.FunctionType('frontend', 'succ', typesys.AnyType())
        ty.params.append(typesys.ParameterType('ordinal', typesys.AnyType()))
        self.ctx.install_function(ty.name, ty)

        # int-type --> BOOLEAN
        ty = typesys.FunctionType('frontend', 'odd', typesys.BoolType())
        ty.params.append(typesys.ParameterType('int', typesys.SIntType(32)))
        self.ctx.install_function(ty.name, ty)

        # TODO: int,real --> same as input
        ty = typesys.FunctionType('frontend', 'abs', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('number', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # TODO: int,real --> same as input
        ty = typesys.FunctionType('frontend', 'sqr', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('number', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'sqrt', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'exp', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'ln', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'sin', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'cos', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # double --> double
        ty = typesys.FunctionType('frontend', 'arctan', typesys.DoubleType())
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # real --> INTEGER
        ty = typesys.FunctionType('frontend', 'trunc', typesys.SIntType(16))
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # real --> INTEGER
        ty = typesys.FunctionType('frontend', 'round', typesys.SIntType(16))
        ty.params.append(typesys.ParameterType('real', typesys.DoubleType()))
        self.ctx.install_function(ty.name, ty)

        # variadic functions
        ty = typesys.FunctionType('frontend', 'write')
        self.ctx.install_function(ty.name, ty)

        ty = typesys.FunctionType('frontend', 'writeln')
        self.ctx.install_function(ty.name, ty)

        ty = typesys.FunctionType('frontend', 'read', typesys.SIntType(32))
        self.ctx.install_function(ty.name, ty)

        ty = typesys.FunctionType('frontend', 'readln', typesys.SIntType(32))
        self.ctx.install_function(ty.name, ty)

        # TODO: add get/put/reset/rewrite/pack/unpack

    def visit(self, node, arg=None):
        try:
            return visitor.DefaultVisitor.visit(self, node, arg)
        except NodeException as e:
            log.e('typecheck', str(e))
        except symtab.SymtabException as e:
            log.e('typecheck', str(e))

    def visit_ProgramNode(self, node, arg=None):
        assert isinstance(node, ast.ProgramNode)

        self.module = node.identifier.accept(self)

        self.ctx.enter_scope()

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()

    def visit_FunctionNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionNode)

        func = node.header.accept(self, self.module)
        node.type = func.ret

        self.ctx.install_function(func.name, func)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        for param in func.params:
            self.ctx.install_symbol(param.name, param.type)

        self.ctx.install_symbol(func.name, func.ret)

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()
        self.func_scope_level -= 1

        return node.type

    def visit_ProcedureNode(self, node, arg=None):
        assert isinstance(node, ast.ProcedureNode)

        func = node.header.accept(self, self.module)
        node.type = typesys.VoidType()

        self.ctx.install_function(func.name, func)

        self.func_scope_level += 1
        self.ctx.enter_scope()

        for param in func.params:
            self.ctx.install_symbol(param.name, param.type)

        if node.block:
            node.block.accept(self)

        self.ctx.exit_scope()
        self.func_scope_level -= 1

        return node.type

    def visit_WithNode(self, node, arg=None):
        assert isinstance(node, ast.WithNode)

        self.ctx.enter_scope()

        for rec in node.rec_var_list.accept(self):
            for field in rec.fields:
                self.ctx.install_symbol(field.name, field.type)

            if rec.variant is None:
                continue

            if rec.variant.selector:
                selector = rec.variant.selector
                self.ctx.install_symbol(selector.name, selector.type)

            for case in rec.variant.cases:
                for field in case.fields:
                    self.ctx.install_symbol(field.name, field.type)

        if node.statement_list:
            node.statement_list.accept(self)

        self.ctx.exit_scope()

    def visit_IndexedVarNode(self, node, field=None):
        assert isinstance(node, ast.IndexedVarNode)

        ty = node.var_access.accept(self)
        indices = node.index_expr_list.accept(self)

        for _ in indices:
            if not isinstance(ty, typesys.ArrayType):
                raise NodeException(node, "variable type '%s' is not indexed" %
                                          ty)

            ty = ty.element

        node.type = ty

        return node.type

    def visit_PointerAccessNode(self, node, field):
        assert isinstance(node, ast.PointerAccessNode)

        ty = node.var_access.accept(self)

        if not isinstance(ty, typesys.PointerType):
            raise NodeException(node, "variable type '%s' is not a pointer" %
                                      ty)

        node.type = ty.pointee

        return node.type

    def visit_VarAccessNode(self, node, field):
        assert isinstance(node, ast.VarAccessNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_symbol(name)
        except symtab.SymtabException:
            try:
                sym = self.ctx.find_function(name)
                return sym.type.ret
            except symtab.SymtabException:
                raise NodeException(node, "call to unknown function '%s'" %
                                          name)

        if isinstance(sym.type, typesys.ReferenceType):
            node.type = sym.type.referee
        else:
            node.type = sym.type

        return node.type

    def visit_FieldAccessNode(self, node, arg=None):
        assert isinstance(node, ast.FieldAccessNode)

        name = node.identifier.accept(self)
        var = node.var_access.accept(self)

        for field in var.fields:
            if field.name == name:
                node.type = field.type
                return node.type

        if var.variant:
            s = var.variant.selector
            if s and s.name == name:
                node.type = s.type
                return node.type

            for case in var.variant.cases:
                for field in case.fields:
                    if field.name == name:
                        node.type = field.type
                        return node.type

        raise NodeException(node, "unknown field '%s'" % name)

    def visit_VarLoadNode(self, node, arg=None):
        assert isinstance(node, ast.VarLoadNode)

        ty = node.var_access.accept(self)

        if isinstance(ty, typesys.ReferenceType):
            node.type = ty.referee
        else:
            node.type = ty

        return node.type

    def visit_UnaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.UnaryOpNode)

        signed = node.name in ['+', '-']

        ty = node.expr.accept(self, signed)

        if (isinstance(ty, typesys.IntType) and
            not ty.signed and signed):
            ty = typesys.SIntType(32)

            node.expr = ast.TypeConvertNode(node.expr)
            node.expr.type = ty

        node.type = ty

        return node.type

    def visit_BinaryOpNode(self, node, arg=None):
        assert isinstance(node, ast.BinaryOpNode)

        sign = node.op.name

        left = node.left.accept(self)
        right = node.right.accept(self)

        if sign in ['+', '-', '*', '/', 'div', 'mod']:
            lhs, rhs = upcast_arithmetic(left, right, sign)
            if not lhs or not rhs:
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            if lhs != left:
                node.left = ast.TypeConvertNode(node.left)
                node.left.type = lhs

            if rhs != right:
                node.right = ast.TypeConvertNode(node.right)
                node.right.type = rhs

            assert lhs == rhs
            ty = lhs

        elif sign in ['=', '<>', '>', '>=', '<', '<=', 'in']:
            lhs, rhs = upcast_relational(left, right, sign)
            if not lhs or not rhs:
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            if lhs != left:
                node.left = ast.TypeConvertNode(node.left)
                node.left.type = lhs

            if rhs != right:
                node.right = ast.TypeConvertNode(node.right)
                node.right.type = rhs

            ty = typesys.BoolType()

        elif sign in ['and', 'or']:
            if (not isinstance(left, typesys.BoolType) or
                not isinstance(right, typesys.BoolType)):
                raise NodeException(node, "invalid binary expression '%s' '%s' '%s'" % (left, sign, right))

            ty = typesys.BoolType()

        node.type = ty

        return node.type

    def visit_AssignmentNode(self, node, arg=None):
        assert isinstance(node, ast.AssignmentNode)

        left = node.var_access.accept(self)
        right = node.expr.accept(self)

        ty = downcast_assignment(right, left, node.position)
        if ty is None:
            raise NodeException(node, "casting from '%s' to '%s'" %
                                      (right, left))

        elif ty != right:
            node.expr = ast.TypeConvertNode(node.expr)
            node.expr.type = ty

        node.type = ty

        return node.type

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)

        try:
            sym = self.ctx.find_function(name)
            params = list(sym.type.params)

            if node.arg_list:
                args = node.arg_list.accept(self, params)
            else:
                args = []

            if len(params):
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

            node.type = sym.type.ret
            return node.type

        except symtab.SymtabException:
            pass

        try:
            ty = self.ctx.find_typedef(name)

            if not node.arg_list:
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

            args = node.arg_list.accept(self)
            if len(args) != 1:
                raise NodeException(node, "wrong number of arguments to '%s'" %
                                          name)

        except symtab.SymtabException:
            raise NodeException(node, "call to unknown function '%s'" % name)

        node.type = ty

        return node.type

    def visit_ArgumentNode(self, node, params=None):
        assert isinstance(node, ast.ArgumentNode)

        expr = node.expr.accept(self)

        if params and len(params):
            p = params.pop(0)

            if isinstance(p.type, typesys.ReferenceType):
                if isinstance(node.expr, ast.VarLoadNode):
                    node.expr = ast.VarReferenceNode(node.expr.var_access)
                    node.expr.type = typesys.ReferenceType(expr)
                    expr = node.expr.type
                elif isinstance(expr, typesys.ArrayType):
                    pass
                else:
                    raise NodeException(node, "argument is not referenceable")

            ty = downcast_assignment(expr, p.type, node.position)
            if ty is None:
                raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                          (expr, p.type))
            elif ty != expr:
                node.expr = ast.TypeConvertNode(node.expr)
                node.expr.type = ty

            node.type = ty

        else:
            node.type = expr

        if hasattr(expr, 'value'):
            node.type.value = expr.value

        return node.type

    def visit_ForNode(self, node, arg=None):
        assert isinstance(node, ast.ForNode)

        name = node.var.accept(self)
        sym = self.ctx.find_symbol(name)

        start = node.value_start.accept(self)
        end = node.value_end.accept(self)

        node.body.accept(self)  # populate with type info

        ty = downcast_assignment(start, sym.type, node.value_start.position)
        if ty is None:
            raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                      (start, sym.type))

        elif ty != start:
            node.value_start = ast.TypeConvertNode(node.value_start)
            node.value_start.type = ty

        ty = downcast_assignment(end, sym.type, node.value_end.position)
        if ty is None:
            raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                      (end, sym.type))

        elif ty != end:
            node.value_end = ast.TypeConvertNode(node.value_end)
            node.value_end.type = ty

    # Single values          

    def visit_IntegerNode(self, node, signed=False):
        assert isinstance(node, ast.IntegerNode)

        if node.value > (2 ** 63) - 1:
            ty = typesys.UIntType(64, node.value)
        elif node.value > (2 ** 32) - 1:
            ty = typesys.SIntType(64, node.value)
        elif node.value > (2 ** 31) - 1:
            ty = typesys.UIntType(32, node.value)
        elif node.value > (2 ** 16) - 1:
            ty = typesys.SIntType(32, node.value)
        elif node.value > (2 ** 15) - 1:
            ty = typesys.UIntType(16, node.value)
        else:
            ty = typesys.SIntType(16, node.value)

        node.type = ty

        return node.type

    def visit_RealNode(self, node, arg=None):
        assert isinstance(node, ast.RealNode)

        if node.value > (2 ** 31) - 1:
            node.type = typesys.DoubleType()
        else:
            node.type = typesys.FloatType()

        return node.type

    def visit_StringNode(self, node, arg=None):
        assert isinstance(node, ast.StringNode)

        length = len(node.value)
        node.type = typesys.StringType(length)

        return node.type

    def visit_CharNode(self, node, arg=None):
        assert isinstance(node, ast.CharNode)

        node.type = typesys.CharType()
        node.type.value = node.value

        return node.type

    def visit_SetMemberRangeNode(self, node, arg=None):
        assert isinstance(node, ast.SetMemberRangeNode)

        member = node.member.accept(self)
        stop = node.expr.accept(self)

        if member != stop:
            ty, _ = upcast_int(member, stop)
            if ty is None:
                raise NodeException(node, "illegal cast from '%s' to '%s'" %
                                          (member, stop))
        else:
            ty = member

        node.type = ty

        return node.type

    def visit_SetNode(self, node, arg=None):
        assert isinstance(node, ast.SetNode)

        members = node.member_list.accept(self)
        if len(members) == 0:
            raise NodeException(node, "invalid set range")

        values = []
        for m in members:
            if m.value is not None:
                values.append(m.value)
            else:
                values.append(m.lo)
                values.append(m.hi)

        lo = min(values)
        hi = max(values)

        if all(isinstance(x, int) for x in values):
            el_ty = typesys.IntRangeType(lo, hi)
        elif all(isinstance(x, int) for x in values):
            el_ty = typesys.CharRangeType(lo, hi)
        else:
            raise NodeException(node, "invalid set range")

        node.type = typesys.SetType(el_ty)

        return node.type

    def visit_SetEmptyNode(self, node, arg=None):
        assert isinstance(node, ast.SetEmptyNode)

        node.type = typesys.EmptySetType()

        return node.type

    # Definitions and declarations 

    def visit_RangeNode(self, node, arg=None):
        assert isinstance(node, ast.RangeNode)

        lo = node.start.accept(self)
        hi = node.stop.accept(self)

        if lo != hi:
            ty_lo, ty_hi = upcast_int(lo, hi)
        else:
            ty_lo, ty_hi = lo, hi

        if (not ty_lo) or (not ty_hi):
            raise NodeException(node, "invalid range combo '%s' and '%s'" %
                                      (lo, hi))

        if ty_lo != lo:
            node.start = ast.TypeConvertNode(node.start)
            node.start.type = ty_lo

        if ty_hi != hi:
            node.stop = ast.TypeConvertNode(node.stop)
            node.stop.type = ty_hi

        cev = ConstantEvalVisitor(self.ctx)
        lo = node.start.accept(cev)
        hi = node.stop.accept(cev)

        if isinstance(lo, str) and len(lo) != 1:
            raise NodeException(node.start, "invalid range type '%s'" % lo)

        if isinstance(hi, str) and len(hi) != 1:
            raise NodeException(node.stop, "invalid range type '%s'" % hi)

        if isinstance(hi, str):
            node.type = typesys.CharRangeType(lo, hi)
        else:
            node.type = typesys.IntRangeType(lo, hi)

        return node.type

    def visit_ConstDeclNode(self, node, arg=None):
        assert isinstance(node, ast.ConstDeclNode)

        name = node.identifier.accept(self)
        ty = node.expr.accept(self)

        cev = ConstantEvalVisitor(self.ctx)
        value = node.expr.accept(cev)

        # convert 'a' + 'b' to 'ab'
        if isinstance(value, str) and len(value) > 1:
            ty = typesys.StringType(len(value))

        ty.value = value
        self.ctx.install_const(name, ty, value)

        node.type = ty

        return node.type

    def visit_EnumTypeNode(self, node, arg=None):
        assert isinstance(node, ast.EnumTypeNode)

        names = node.identifier_list.accept(self)

        for value, name in enumerate(names):
            ty = typesys.EnumType(names)
            ty.value = value
            self.ctx.install_const(name, ty, value)

        node.type = typesys.EnumType(names)

        return node.type

    def visit_SetTypeNode(self, node, arg=None):
        assert isinstance(node, ast.SetTypeNode)

        base = node.base_type.accept(self)
        ty = typesys.SetType(base)

        node.type = ty

        return node.type

    def visit_TypeNode(self, node, arg=None):
        assert isinstance(node, ast.TypeNode)

        name = node.identifier.accept(self)

        try:
            node.type = self.ctx.find_typedef(name)
        except symtab.SymtabException:
            node.type = typesys.DeferredType(name)

        return node.type


    def visit_TypeDeclListNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclListNode)

        for c in node.children:
            c.accept(self)

        for c in node.children:
            c.accept(DeferredTypeVisitor(self.ctx))


    def visit_ArrayTypeNode(self, node, arg=None):
        assert isinstance(node, ast.ArrayTypeNode)

        ty = node.component_type.accept(self)
        dims = node.index_list.accept(self)

        for dim in dims:
            ty = typesys.ArrayType(ty, dim)

        node.type = ty

        return node.type

    def visit_PointerTypeNode(self, node, arg=None):
        assert isinstance(node, ast.PointerTypeNode)

        pointee_ty = node.domain_type.accept(self)
        node.type = typesys.PointerType(pointee_ty)

        return node.type

    def visit_NullNode(self, node, ty):
        assert isinstance(node, ast.NullNode)

        pointee_ty = typesys.AnyType()
        node.type = typesys.PointerType(pointee_ty)

        return node.type

    def visit_FileTypeNode(self, node, arg=None):
        assert isinstance(node, ast.FileTypeNode)

        ty = node.component_type.accept(self)
        node.type = typesys.FileType(ty)

        return node.type

    def visit_TypeDeclNode(self, node, arg=None):
        assert isinstance(node, ast.TypeDeclNode)

        name = node.identifier.accept(self)
        ty = node.type_denoter.accept(self)
        ty.name = name
        self.ctx.install_typedef(name, ty)

        node.type = ty

        return node.type

    def visit_VarDeclNode(self, node, arg=None):
        assert isinstance(node, ast.VarDeclNode)

        ty = node.type_denoter.accept(self)
        names = node.identifier_list.accept(self)

        for name in names:
            self.ctx.install_symbol(name, ty)

        node.type = ty

        return node.type

    def visit_FunctionHeadNode(self, node, module=None):
        assert isinstance(node, ast.FunctionHeadNode)

        name = node.identifier.accept(self)
        ret_ty = node.return_type.accept(self)

        ty = typesys.FunctionType(module, name, ret_ty, self.func_scope_level)

        if node.param_list:
            ty.params = node.param_list.accept(self)

        node.type = ty

        return node.type

    def visit_ProcedureHeadNode(self, node, module=None):
        assert isinstance(node, ast.ProcedureHeadNode)

        name = node.identifier.accept(self)
        ret_ty = typesys.VoidType()

        ty = typesys.FunctionType(module, name, ret_ty, self.func_scope_level)

        if node.param_list:
            ty.params = node.param_list.accept(self)

        node.type = ty

        return node.type

    def visit_ValueParameterNode(self, node, arg=None):
        assert isinstance(node, ast.ValueParameterNode)

        type_name = node.type_denoter.accept(self)
        ty = self.ctx.find_typedef(type_name)
        names = node.identifier_list.accept(self)

        l = []
        for name in names:
            param = typesys.ParameterType(name, ty)
            l.append(param)

        return l

    def visit_RefParameterNode(self, node, arg=None):
        assert isinstance(node, ast.RefParameterNode)

        type_name = node.type_denoter.accept(self)
        ty = self.ctx.find_typedef(type_name)
        ty = typesys.ReferenceType(ty)
        names = node.identifier_list.accept(self)

        l = []
        for name in names:
            param = typesys.ParameterType(name, ty)
            l.append(param)

        return l

    def visit_RecordTypeNode(self, node, arg=None):
        assert isinstance(node, ast.RecordTypeNode)

        name = self.ctx.label()
        ty = typesys.RecordType(name)

        if node.section_list:
            ty.fields = node.section_list.accept(self)

        if node.variant:
            ty.variant = node.variant.accept(self)

        node.type = ty

        return node.type

    def visit_RecordSectionNode(self, node, arg=None):
        assert isinstance(node, ast.RecordSectionNode)

        names = node.identifier_list.accept(self)
        ty = node.type_denoter.accept(self)

        fields = []
        for name in names:
            field = typesys.FieldType(name, ty)
            fields.append(field)

        node.type = ty

        return fields

    def visit_VariantPartNode(self, node, arg=None):
        assert isinstance(node, ast.VariantPartNode)

        name = self.ctx.label()
        ty = typesys.VariantType(name)

        ty.selector = node.variant_selector.accept(self)
        ty.cases = node.variant_list.accept(self, ty.selector)

        node.type = ty

        return node.type

    def visit_VariantSelectorNode(self, node, arg=None):
        assert isinstance(node, ast.VariantSelectorNode)

        if node.tag_field:
            field_name = node.tag_field.accept(self)
        else:
            field_name = self.ctx.label("selector")

        type_name = node.tag_type.accept(self)
        field_type = self.ctx.find_typedef(type_name)

        node.type = typesys.FieldType(field_name, field_type)

        return node.type

    def visit_VariantNode(self, node, selector):
        assert isinstance(node, ast.VariantNode)

        node.case_list.accept(self, selector.type)   # populate with type info

        cev = ConstantEvalVisitor(self.ctx)
        node.case_list.accept(cev)

        if node.variant_part:
            node.variant_part.accept(self)

        if node.record_list:
            record_name = self.ctx.label("variant")
            ty = typesys.RecordType(record_name)
            ty.fields = node.record_list.accept(self)

            return ty

    def visit_CaseStatementNode(self, node, arg=None):
        assert isinstance(node, ast.CaseStatementNode)

        index = node.case_index.accept(self)
        node.case_list_element_list.accept(self, index)

        if node.otherwise:
            node.otherwise.accept(self)

        node.type = index

        return node.type

    def visit_CaseListElementNode(self, node, index):
        assert isinstance(node, ast.CaseListElementNode)

        consts = node.case_constant_list.accept(self, index)

        if node.statement:
            node.statement.accept(self)

        return consts

    def visit_CaseConstNode(self, node, index):
        assert isinstance(node, ast.CaseConstNode)

        const = node.constant.accept(self)

        lhs, rhs = upcast_relational(const, index)
        if index != rhs:
            raise NodeException(node, "casting from '%s' to '%s'" %
                                      (const, index))

        elif lhs != const:
            node.constant = ast.TypeConvertNode(node.constant)
            node.constant.type = lhs

        node.type = copy.deepcopy(lhs)
        node.type.value = const.value

        return node.type

    def visit_CaseRangeNode(self, node, index=None):
        assert isinstance(node, ast.CaseRangeNode)

        lo = node.first_constant.accept(self)
        hi = node.last_constant.accept(self)

        if lo != hi:
            ty_lo, ty_hi = upcast_int(lo, hi)
        else:
            ty_lo, ty_hi = lo, hi

        if (not ty_lo) or (not ty_hi):
            raise NodeException(node, "invalid range combination '%s' and '%s'" % (lo, hi))

        if ty_lo != lo:
            node.first_constant = ast.TypeConvertNode(node.first_constant)
            node.first_constant.type = ty_lo

        if ty_hi != hi:
            node.last_constant = ast.TypeConvertNode(node.last_constant)
            node.last_constant.type = ty_hi

        cev = ConstantEvalVisitor(self.ctx)
        lo = node.first_constant.accept(cev)
        hi = node.last_constant.accept(cev)

        if isinstance(lo, str) and len(lo) != 1:
            raise NodeException(node.start, "illegal range type '%s'" % lo)

        if isinstance(hi, str) and len(hi) != 1:
            raise NodeException(node.stop, "illegal range type '%s'" % hi)

        if isinstance(hi, str):
            node.type = typesys.CharRangeType(lo, hi)
        else:
            node.type = typesys.IntRangeType(lo, hi, index.width)

        return node.type

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name



class FixBuiltinCallbyRefVisitor(visitor.NodeVisitor):

    def __init__(self):
        self.named_functions = set()
        self.named_functions.add('read')
        self.named_functions.add('readln')

    def default_visit(self, node, arg=None):
        visitor.NodeVisitor.default_visit(self, node, arg)

        return node

    def visit_IdentifierNode(self, node, arg=None):
        assert isinstance(node, ast.IdentifierNode)

        return node.name

    def visit_FunctionCallNode(self, node, arg=None):
        assert isinstance(node, ast.FunctionCallNode)

        name = node.identifier.accept(self)

        if name not in self.named_functions:
            return

        byref = True

        if node.arg_list:
            node.arg_list.accept(self, byref)

    def visit_VarLoadNode(self, node, byref):
        assert isinstance(node, ast.VarLoadNode)

        if byref:
            return node.var_access
        else:
            return node

    def visit_ArgumentNode(self, node, byref=False):
        assert isinstance(node, ast.ArgumentNode)

        if not byref:
            return
            
        expr = node.expr.accept(self, byref)
        if expr:
            node.expr = expr
