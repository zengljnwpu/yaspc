'''
Symbol table for frontend.
'''
from __future__ import absolute_import, print_function

from frontend.typesys import Type

class SymtabException(Exception):
    pass


def assert_is_value(value):
    if not isinstance(value, Value):
        raise SymtabException("Invalid value '%s'", value)


class Value(object):
    def __init__(self, handle, ty):
        Type.assert_is_type(ty)

        self.handle = handle
        self.type = ty

    def __str__(self):
        return str(self.type)


class VariableValue(Value):
    pass


class ConstantValue(Value):
    pass


class FunctionValue(Value):
    pass


class GotoBlock(object):
    def __init__(self):
        self.handle = None
        self.entries = list()


class Symbol(object):

    def __init__(self, name, ty, handle=None):
        Type.assert_is_type(ty)

        self.name = name
        self.type = ty
        self.handle = handle

    def __str__(self):
        return "%s (%s)" % (self.name, self.type)


class Scope(object):

    def __init__(self):
        self.symbols = dict()
        self.typedefs = dict()
        self.gotos = dict()
        self.functions = dict()

    def dump_symbols(self, prefix=""):
        for name in list(self.symbols.keys()):
            print(("%s: %s" % (prefix, name)))

            sym = self.symbols[name]
            if isinstance(sym, Scope):
                sym.dump_symbols(prefix + "  ")

    def dump_functions(self, prefix=""):
        for name in list(self.functions.keys()):
            print(("%s: %s" % (prefix, name)))

    def dump_typedefs(self, prefix=""):
        for name in list(self.typedefs.keys()):
            print(("%s: %s" % (prefix, name)))

            sym = self.typedefs[name]
            if isinstance(sym, Scope):
                sym.dump_typedefs(prefix + "  ")


class SymbolTable(object):

    def __init__(self):
        self._scopes = list()
        self._lvl = -1  # scope level counter
        self._lbl = 0  # Next label number

    def label(self, s='label'):
        self._lbl += 1
        return "%s_%d" % (s, self._lbl)

    def dump_symbols(self):
        print('---------- SYMBOLS --------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_symbols(" " * i)

    def dump_functions(self):
        print('--------- FUNCTIONS -------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_functions(" " * i)

    def dump_typedefs(self):
        print('--------- TYPEDEFS --------------')
        for i, scope in enumerate(self._scopes):
            scope.dump_typedefs(" " * i)

    def enter_scope(self):
        scope = Scope()
        self._lvl += 1
        self._scopes.append(scope)

    def exit_scope(self):
        self._scopes.pop(self._lvl)
        self._lvl -= 1

    @property
    def symbols(self):
        d = dict()

        for i in range(self._lvl + 1):
            l = list(d.items())
            l += list(self._scopes[i].symbols.items())
            d = dict(l)

        return d.values()

    def install_symbol(self, name, ty, handle=None):
        scope = self._scopes[self._lvl]
        sym = Symbol(name, ty, handle)
        scope.symbols[name] = sym

        return sym

    def find_symbol(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.symbols:
                return scope.symbols[name]

        raise SymtabException("Unknown symbol '%s'" % name)

    def install_const(self, name, ty, handle):
        scope = self._scopes[self._lvl]
        const = ConstantValue(handle, ty)
        scope.symbols[name] = const

        return const

    def install_typedef(self, name, ty):
        scope = self._scopes[self._lvl]
        scope.typedefs[name] = ty

        return ty

    def find_typedef(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.typedefs:
                return scope.typedefs[name]

        raise SymtabException("Unknown typedef '%s'" % name)

    def install_function(self, name, ty, handle=None):
        scope = self._scopes[self._lvl]
        func = FunctionValue(handle, ty)
        scope.functions[name] = func

        return func

    def find_function(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.functions:
                return scope.functions[name]

        raise SymtabException("Unknown function '%s'" % name)

    def install_goto(self, name, goto):
        scope = self._scopes[self._lvl]
        scope.gotos[name] = goto

        return goto

    def find_goto(self, name):
        for i in range(self._lvl, -1, -1):
            scope = self._scopes[i]
            if name in scope.gotos:
                return scope.gotos[name]

        raise SymtabException("Unknown goto label '%s'" % name)
