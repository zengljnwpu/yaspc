class Literal ():
    def to_source (self, table = None):
        return

    def dump (self):
        return

    def collect_statistics (self, stats):
        return

    def is_zero (self):
        return

    def plus (self, diff):
        return

    def cmp (self, sym):
        return


class IntegerLiteral (Literal):
    def __init__ (self, n:int):
        self.value = int(n)

    def __eq__ (self, other):
        if not isinstance(other, IntegerLiteral):
            return False
        else:
            return other.value == self.value

    def __hash__ (self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def equals (self, other):
        return self.__eq__ (other)

    def is_zero(self):
        return self.value == 0

    def __add__ (self, diff):
        return IntegerLiteral (self.value + diff)

    def plus (self, diff):
        return self.__add__ (diff)

    def integer_literal (self):
        return self

    def to_source (self, table = None):
        return str (self.value)

    def collect_statistics(self, stats):
        return

    def compare_to (self, lit):
        return self.cmp (lit)

    def cmp (self, i):
        if isinstance(i, IntegerLiteral):
            return self.cmp(i.value)
        elif isinstance(i, NamedSymbol):
            return -1
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return -1
        elif isinstance(i, int):
            if self.value > i:
                return 1
            elif self.value == i:
                return 0
            else:
                return -1

    def dump (self):
        return "(IntegerLiteral " + str(self.value) + ")"


class Symbol (Literal):
    def __init__ (self):
        return

    def name (self):
        return

    def dump (self):
        return ""

class BaseSymbol (Symbol):
    def is_zero(self):
        return False

    def collect_statistics(self, stats):
        stats.symbol_used (self)

    def __str__(self):
        return str (hash (self))

    def plus (self, n):
        raise Exception("must not happen: BaseSymbol.plus called")

class NamedSymbol (BaseSymbol):
    def __init__(self, name):
        super().__init__()
        if name == "":
            raise Exception ("NamedSymbol must have _name")
        self.name = str(name)

    def name (self):
        return self.name

    def to_source(self, table = None):
        return self.name

    def __str__ (self):
        return "#" + self.name

    @property
    def __hash__ (self):
        return hash(self.name)

    def __eq__ (self, other):
        if not isinstance (other, NamedSymbol):
            return False
        else:
            return self.name == other.name

    def compare_to (self, lit):
        return self.cmp (lit)

    def cmp (self, i):
        if isinstance(i, IntegerLiteral):
            return 1
        elif isinstance(i, NamedSymbol):
            return (self.name > i.name) - (self.name < i.name)
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return (str(self) > str(i)) - (str(self) < str(i))

    def dump (self):
        return "(NamedSymbol " + self.name + ")"

class UnnamedSymbol (BaseSymbol):
    def name(self):
        raise Exception("unnamed symbol")

    def to_source(self, tabke = None):
        raise Exception("UnnamedSymbol#to_source called")

    def __str__ (self):
        return super().__str__()
    
    def compare_to (self, lit):
        return self.cmp (lit)

    def cmp (self, i):
       if isinstance(i, IntegerLiteral):
           return 1
       elif isinstance(i, NamedSymbol):
           return 1
       elif isinstance(i, UnnamedSymbol):
           return (str(self) > str(i)) - (str(self) < str (i))
       else:
           return 1

    def dump (self):
        return "(UnnamedSymbol @" + str (self) + ")"


class SuffixedSymbol (Symbol):
    def __init__(self, base: Symbol, suffix: str):
       super().__init__()
       self.base = base
       self.suffix = suffix

    def is_zero (self):
        return False

    def collect_statistics(self, stats):
        return self.base.collect_statistics (stats)

    def plus (self, n):
        raise Exception("must not happen: SuffixedSymbol.plus called")

    def name(self):
        return self.base.name

    def to_source (self, table = None):
        return self.base.to_source (table) + self.suffix

    def __hash__ (self):
        return hash (str(self.base) + self.suffix)

    def __eq__ (self, other):
        if not isinstance (other, SuffixedSymbol):
            return False
        else:
            return (self.base == other.base) and (self.suffix == other.base)

    def __str__ (self):
        return str(self.base) + self.suffix

    def compare_to (self, lit):
        return self.cmp (lit)

    def cmp (self, i):
        if isinstance(i, IntegerLiteral):
            return 1
        elif isinstance(i, NamedSymbol):
            return (str(self) > str(i)) - (str(self) < str (i))
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return (str(self) > str(i)) - (str(self) < str(i))

    def dump(self):
        return "(SuffixedSymbol " + self.base.dump() + \
            " " + self.suffix + ")"