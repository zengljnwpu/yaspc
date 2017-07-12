from enum import Enum


class Type (Enum):
    INT8 = 1
    INT16 = 2
    INT32 = 4
    INT64 = 8

    @classmethod
    def get (cls, size):
        if size == 1:
            return cls.INT8
        elif size == 2:
            return cls.INT16
        elif size == 4:
            return cls.INT32
        elif size == 8:
            return cls.INT64
        else:
            raise Exception ("Unsupported asm type size: " + size)

    def size(self):
        if self.name == self.INT8.name:
            return 1
        elif self.name == self.INT16.name:
            return 2
        elif self.name == self.INT32.name:
            return 4
        elif self.name == self.INT64.name:
            return 8
        else:
            raise Exception ("must not happen")

