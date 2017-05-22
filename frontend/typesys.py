'''
Type system of frontend
'''
from __future__ import absolute_import, print_function

import math
import sys


class Type(object):

    def __init__(self, identifier=None):
        self.identifier = identifier
        self.handle = None

    @property
    def id(self):
        return self.identifier

    def __eq__(self, obj):
        if isinstance(obj, Type):
            return self.id == obj.id

        return False

    def __ne__(self, obj):
        if isinstance(obj, Type):
            return self.id != obj.id

        return True

    def __str__(self):
        return str(self.id)


# abstract class
class IntType(Type):

    def __init__(self, lo, hi, width, val=None):
        Type.__init__(self, "int[%d]" % width)

        if width <= 0:
            raise SymtabException('Invalid integer width %d', width)

        self.lo = lo
        self.hi = hi
        self.width = width
        self.value = val

    @property
    def signed(self):
        return self.lo < 0

    @property
    def unsigned(self):
        return self.lo >= 0


class UIntType(IntType):

    def __init__(self, width, val=None):
        lo = 0
        hi = (2 ** width) - 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "uint[%d]" % width)


class SIntType(IntType):

    def __init__(self, width, val=None):
        lo = -(2 ** (width - 1))
        hi = (2 ** (width - 1)) - 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "sint[%d]" % width)


class IntRangeType(IntType):

    def __init__(self, lo, hi, width=None):
        lo = int(lo)
        hi = int(hi)

        lo_ = min(lo, hi)
        hi_ = max(lo, hi)

        if not width:
            num = max(abs(lo_), abs(hi_))
            signed = (lo_ < 0)

            if num > (2 ** 16 - signed) - 1:
                width = 32
            elif num > (2 ** 8 - signed) - 1:
                width = 16
            else:
                width = 8

        IntType.__init__(self, lo_, hi_, width)
        Type.__init__(self, "range[%d..%d]" % (lo_, hi_))


class EnumType(IntType):

    def __init__(self, names, width=None):
        assert len(names) > 0

        self.names = names
        lo = 0
        hi = len(names) - 1

        if not width:
            if hi > (2 ** 16) - 1:
                width = 32
            elif hi > (2 ** 8) - 1:
                width = 16
            else:
                width = 8

        IntType.__init__(self, lo, hi, width)
        Type.__init__(self, "enum[%d..%d]" % (lo, hi))


class BoolType(IntType):

    def __init__(self, val=None):
        lo = 0
        hi = 1
        width = 1
        IntType.__init__(self, lo, hi, width, val)
        Type.__init__(self, "bool")


class CharType(Type):

    def __init__(self, val=None):
        self.hi = 255
        self.lo = 0
        self.width = 8
        self.value = None
        self.signed = False
        self.unsigned = True
        self.value = val

        Type.__init__(self, "char")


class CharRangeType(CharType):

    def __init__(self, lo, hi):
        self.lo = ord(lo)
        self.hi = ord(hi)
        self.width = 8
        self.signed = False
        self.unsigned = True

        Type.__init__(self, "range[%c..%c]" % (self.lo, self.hi))


class RealType(Type):

    def __init__(self, width=32):
        self.width = width

        Type.__init__(self, "real[%d]" % width)


class FloatType(RealType):

    def __init__(self):
        RealType.__init__(self, 32)


class DoubleType(RealType):

    def __init__(self):
        RealType.__init__(self, 64)


class NamedType(Type):

    def __init__(self, name):
        self.name = name
        Type.__init__(self, name)


class DeferredType(NamedType):
    # Type required when named types are used
    # before being defined.
    def __init__(self, name):
        NamedType.__init__(self, name)

    @property
    def id(self):
        return "deferred[%s]" % self.name

class ArrayType(Type):

    def __init__(self, element_ty, range_ty):
        assert_is_type(element_ty)
        assert_is_type(range_ty)

        self.element = element_ty
        self.range = range_ty

        Type.__init__(self)

    @property
    def id(self):
        return "array[%d..%d] of %s" % (self.range.lo, self.range.hi,
                                           self.element)

    @property
    def width(self):
        return self.element.width * self.length

    @property
    def length(self):
        return self.range.hi - self.range.lo + 1


class StringType(ArrayType):

    def __init__(self, length):
        element_ty = CharType()
        range_ty = IntRangeType(0, length - 1)

        ArrayType.__init__(self, element_ty, range_ty)


class SetType(Type):

    def __init__(self, element_ty):
        assert_is_type(element_ty)

        self.element = element_ty
        Type.__init__(self)

    @property
    def id(self):
        return "set of %s" % self.element

    @property
    def width(self):
        return 2 ** self.element.width


class EmptySetType(Type):

    def __init__(self):
        self.value = 0
        Type.__init__(self, "emptyset")


class VoidType(Type):

    def __init__(self):
        Type.__init__(self, "void")


class AnyType(Type):

    def __init__(self):
        Type.__init__(self, "any")


class ReferenceType(Type):

    def __init__(self, referee_ty):
        assert_is_type(referee_ty)

        self.referee = referee_ty
        Type.__init__(self)

    @property
    def id(self):
        return "reference of %s" % self.referee


class PointerType(Type):

    def __init__(self, pointee_ty):
        assert_is_type(pointee_ty)

        self.pointee = pointee_ty
        Type.__init__(self)

    @property
    def id(self):
        return "pointer to %s" % self.pointee

    @property
    def width(self):
        return math.log(sys.maxsize, 2) + 1


class FunctionType(NamedType):

    def __init__(self, module, name, ret_ty=VoidType(), scope_level=0):
        assert_is_type(ret_ty)

        self.ret = ret_ty
        self.params = list()
        self.namespace = module + '.' + name
        self.scope_level = scope_level
        self.scope_hook = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        "function[%s]" % self.namespace


class ParameterType(NamedType):

    def __init__(self, name, ty):
        assert_is_type(ty)

        self.type = ty

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "param of %s" % self.type

    @property
    def width(self):
        return self.type.width


class RecordType(NamedType):

    def __init__(self, name):
        self.fields = list()
        self.variant = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "record[%s]" % self.name

    @property
    def width(self):
        return sum([x.width for x in self.fields])


class VariantType(NamedType):

    def __init__(self, name):
        self.cases = list()
        self.selector = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "variant[%s]" % self.name

    @property
    def largest(self):
        ty = None

        for case in self.cases:
            if not ty:
                ty = case
            elif ty.width < case.width:
                ty = case

        return ty

    @property
    def width(self):
        return self.largest.width


class FieldType(NamedType):

    def __init__(self, name, ty):
        assert_is_type(ty)

        self.type = ty
        self.index = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "field[%s]" % self.name

    @property
    def width(self):
        return self.type.width


class ScopeHookType(NamedType):

    def __init__(self, name):
        self.fields = list()

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "scope_hook[%s]" % self.name


class ScopeFieldType(FieldType):

    def __init__(self, name, ty):
        assert_is_type(ty)

        self.type = ty
        self.index = None

        NamedType.__init__(self, name)

    @property
    def id(self):
        return "scope_field[%s]" % self.name

    @property
    def width(self):
        return self.type.width


class FileType(Type):

    def __init__(self, component_ty):
        assert_is_type(component_ty)

        self.component_ty = component_ty
        Type.__init__(self)

    @property
    def id(self):
        return "file of %s" % self.component


def assert_is_type(ty):
    if not isinstance(ty, Type):
        raise SymtabException("Invalid type '%s'", type(ty))