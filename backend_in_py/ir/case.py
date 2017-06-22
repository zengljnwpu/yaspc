from backend_in_py.asm.assembly import *


class Case():
    def __init__(self, value: int, label: Label):
        self._value = value
        self._label = label

    def dump (self, d):
        d.print_class (self)
        d.print_member ("_value", self._value)
        d.print_member ("_label", self._label)


