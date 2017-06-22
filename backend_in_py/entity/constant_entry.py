from backend_in_py.asm.literal import *
from backend_in_py.asm.operand import *


class ConstantEntry (object):
    def __init__(self, val: str):
        self._value = val
        self._symbol = 0
        self._mem_ref = 0
        self._address = 0

    def value(self):
        return self._value

    def symbol (self):
        if not self._symbol:
            raise Exception ("must not happen: symbol == null")
        return self._symbol

    def set_symbol(self, sym: Symbol):
        self.sym = sym

    def mem_ref (self):
        if not self._mem_ref:
            raise Exception ("must not happen: memref == null")
        return self._mem_ref


    def set_mem_ref (self, mem: MemoryReference):
        self._mem_ref = mem

    def address (self):
        return self._address

    def set_address(self, imm: ImmediateValue):
        self._address = imm


class ConstantTable (ConstantEntry):
    def __init__(self):
        self._table = dict({})

    def is_empty (self):
        return self._table

    def intern (self, s:str):
        ent = self._table.get(s)
        if not ent:
            ent = ConstantEntry (s)
            self._table[s] = ent
        return ent

    def entries(self):
        return self._table.values()

    def iterators(self):
        return self._table.values().__iter__()
