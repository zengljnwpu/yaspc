from backend_in_py.asm.assembly import *


class Case():
    def __init__(self, value: int, label: Label):
        self.value = value
        self.label = label

    def dump (self, d):
        d.print_class (self)
        d.print_member ("_value", self.value)
        d.print_member ("_label", self.label)


