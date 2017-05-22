from backend_in_py.asm.Literal import *


class SymbolTable ():
    def __init__(self, base):
        self.base = base
        self.map = dict ({})
        self.seq= 0

    def _new_string(self):
        new_str = self.base + str(self.seq)
        self.seq += 1
        return new_str

    def new_symbol (self):
        return NamedSymbol (self._new_string())

    def symbol_string (self, sym):
        str = self.map.get (sym)
        if str:
            return str
        else:
            new_str = self._new_string()
            self.map[sym] = new_str
            return new_str


__DUMMY_SYMBOL_BASE = "L"
dummy = SymbolTable(__DUMMY_SYMBOL_BASE)
