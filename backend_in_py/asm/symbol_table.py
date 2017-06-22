from backend_in_py.asm.literal import *


class SymbolTable ():
    def __init__(self, base: str):
        self._base = base
        self._map = dict ({})
        self._seq= 0

    def _new_string(self):
        new_str = self._base + str(self._seq)
        self._seq += 1
        return new_str

    def new_symbol (self):
        return NamedSymbol (self._new_string())

    def symbol_string (self, sym):
        str = self._map.get (sym)
        if str:
            return str
        else:
            new_str = self._new_string()
            self._map[sym] = new_str
            return new_str

    @staticmethod
    def dummp ():
        return dummy

__DUMMY_SYMBOL_BASE = "L"
dummy = SymbolTable(__DUMMY_SYMBOL_BASE)

