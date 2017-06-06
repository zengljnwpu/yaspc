
def type_factory (type: str, obj):
    if type == "int":
        return IntegerType (4, False, obj)


class Type (object):
    size_unknown = -1

    def size(self):
        raise Exception ("Method not instantiated")

    def alloc_size (self):
        return self.size()

    def alignment (self):
        return self.alloc_size()

    def is_same_type (self, other):
        return False

    def is_void (self):
        return False

    def is_int (self):
        return False

    def is_integer (self):
        return False

    def is_signed (self):
        raise Exception ("#is_signed for non-integer type")

    def is_pointer (self):
        return False

    def is_array (self):
        return False

    def is_composite_type (self):
        return False

    def is_struct (self):
        return False

    def is_union (self):
        return False

    def is_user_type (self):
        return False

    def is_function (self):
        return False

    # Ability methods (unary)
    def is_allocated_array (self):
        return False

    def is_incomplete_array (self):
        return False

    def is_scalar (self):
        return False

    def is_callable (self):
        return False

    # Ability methods (binary)
    def is_compatible (self, other):
        return

    def is_castable_to (self, target):
        return

    def base_type (self):
        raise Exception ("#base_type called for undereferabke type")

    # Cast methods
    def get_integer_type (self):
        return

    def get_pointer_type (self):
        return

    def get_function_type (self):
        return

    def get_struct_type (self):
        return

    def get_union_type (self):
        return

    def get_composite_type (self):
        return

    def get_array_type (self):
        return


class IntegerType (Type):
    def __init__ (self, size: int, is_signed: bool, name: str):
        super (IntegerType, self).__init__()
        self._size = size
        self._is_signed = is_signed
        self._name = name

    def is_integer(self):
        return True

    def is_signed(self):
        return self._is_signed

    def is_scalar(self):
        return True

    #unsupport signed int
    def min_value (self):
        return 0

    # unsupport signed int
    def max_value (self):
        return 4294967295

    def is_in_domain (self, i: int):
        return self.min_value() <= i and self.max_value() >= i

    def __eq__(self, other):
        if not isinstance(other, IntegerType): return False
        else:
            if self._name == other._name and self._is_signed == other._is_signed and self._name == other._name:
                return True
            else:
                return False

    def is_same_type (self, other):
        return self.__eq__(other)

    def is_compatible(self, other):
        return other.is_integer() and self._size <= other._size()

    def is_castable_to(self, target):
        return target.is_integer() or target.is_pointer()

    def size(self):
        return self._size

    def __str__(self):
        return self._name



