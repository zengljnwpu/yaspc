
from enum import Enum

from backend.asm.operand import Register
from backend.asm.inttype import IntType


class RegisterClass (Enum):
    AX = 1
    BX = 2
    CX = 3
    DX = 4
    SI = 5
    DI = 6
    SP = 7
    BP = 8


# Describe propertys of x86 Registers
class x86Register (Register):
    def __init__(self, _class, reg_type):
        super(x86Register, self).__init__()
        self._class = _class
        self.type = reg_type

    def for_type(self, t):
        return x86Register(self._class, t)

    def is_register(self):
        return True

    def __eq__(self, other):
        return isinstance(other, x86Register) and (other._class == self._class)

    @property
    def __hash__(self):
        return self._class.__hash__()

    def base_name(self):
        return self._class.name.lower()

    def to_source(self, table):
        return "%" + self.__typed_name()

    def __typed_name(self):
        if self.type.size() == IntType.INT8:
            return self.__lower_byte_register()
        elif self.type.size() == IntType.INT16:
            return self.base_name()
        elif self.type.size() == IntType.INT32:
            return "e" + self.base_name()
        elif self.type.size() == IntType.INT64:
            return "r" + self.base_name()
        else:
            raise Exception("unknown register type: " + str(self.type))

    def __lower_byte_register(self):
        if self._class == (RegisterClass.AX or RegisterClass.BX or RegisterClass.CX or RegisterClass.DX):
            return self.base_name()[0, 1] + "l"
        else:
            raise Exception(
                "does not have lower-byte register:" + str(self._class))

    def dump(self):
        return "(Register " + str(self._class) + " " + str(self.type) + ")"
