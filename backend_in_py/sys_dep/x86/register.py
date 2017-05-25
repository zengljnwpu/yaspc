from backend_in_py.asm.operand import Register
from backend_in_py.asm.type import *
from backend_in_py.sys_dep.x86.register_class import RegisterClass

class x86Register (Register):
    def __init__ (self, _class: RegisterClass, type: Type):
        super().__init__()
        self._class = _class
        self.type = type

    def for_type (self, t):
        return x86Register (self._class, t)

    def is_register(self):
        return True

    def __eq__ (self, other):
        return isinstance(other, Register) and (other._class == self._class)

    @property
    def __hash__ (self):
        return self._class.__hash__()

    def base_name (self):
        return self._class.name.lower()

    def to_source (self, table):
        return "%" + self.__typed_name()

    def __typed_name(self):
        if self.type == Type.INT8:
            return self.__lower_byte_register()
        elif self.type == Type.INT16:
            return self.base_name()
        elif self.type == Type.INT32:
            return "e" + self.base_name()
        elif self.type == Type.INT64:
            return "r" + self.base_name()
        else:
            raise Exception ("unknown register type: " + str(self.type))

    def __lower_byte_register(self):
        if self._class == (RegisterClass.AX or RegisterClass.BX or RegisterClass.CX or RegisterClass.DX):
            return self.base_name()[0, 1] + "l"
        else:
            raise Exception ("does not have lower-byte register:" + str(self._class))

    def dump (self):
        return "(Register " + str(self._class) + " " + str(self.type) + ")"


