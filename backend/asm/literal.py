class Literal (object):
    def to_source(self, table=None):
        return

    def dump(self):
        return

    def collect_statistics(self, stats):
        return

    def is_zero(self):
        return

    def plus(self, diff):
        return

    def cmp(self, sym):
        return


class IntegerLiteral(Literal):
    def __init__(self, n):
        self._value = int(n)

    def value(self):
        return self._value

    def __int__(self):
        return self._value

    def __eq__(self, other):
        if not isinstance(other, IntegerLiteral):
            return False
        else:
            return other._value == self._value

    def __hash__(self):
        return hash(self._value)

    def __str__(self):
        return str(self._value)

    def equals(self, other):
        return self.__eq__(other)

    def is_zero(self):
        return self._value == 0

    def __add__(self, diff):
        return IntegerLiteral(self._value + diff)

    def plus(self, diff):
        return self.__add__(diff)

    def integer_literal(self):
        return self

    def to_source(self, table=None):
        return str(self._value)

    def collect_statistics(self, stats):
        return

    def compare_to(self, lit):
        return self.cmp(lit)

    def cmp(self, i):
        if isinstance(i, IntegerLiteral):
            return self.cmp(i._value)
        elif isinstance(i, NamedSymbol):
            return -1
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return -1
        elif isinstance(i, int):
            if self._value > i:
                return 1
            elif self._value == i:
                return 0
            else:
                return -1

    def dump(self):
        return "(IntegerLiteral " + str(self._value) + ")"


class Symbol(Literal):
    def __init__(self):
        return

    def name(self):
        return

    def dump(self):
        return ""


class BaseSymbol(Symbol):
    def is_zero(self):
        return False

    def collect_statistics(self, stats):
        stats.symbol_used(self)

    def __str__(self):
        return str(hash(self))

    def plus(self, n):
        raise Exception("must not happen: BaseSymbol.plus called")


class NamedSymbol (BaseSymbol):
    def __init__(self, name):
        super(NamedSymbol, self).__init__()
        if name == "":
            raise Exception("NamedSymbol must have _name")
        self._name = name

    def name(self):
        return self._name

    def to_source(self, table=None):
        return self._name

    def __str__(self):
        return "#" + self._name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        if not isinstance(other, NamedSymbol):
            return False
        else:
            return self._name == other._name

    def compare_to(self, lit):
        return self.cmp(lit)

    def cmp(self, i):
        if isinstance(i, IntegerLiteral):
            return 1
        elif isinstance(i, NamedSymbol):
            return (self._name > i._name) - (self._name < i._name)
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return (str(self) > str(i)) - (str(self) < str(i))

    def dump(self):
        return "(NamedSymbol " + self._name + ")"


class UnnamedSymbol (BaseSymbol):
    def name(self):
        raise Exception("unnamed symbol")

    def to_source(self, tabke=None):
        raise Exception("UnnamedSymbol#to_source called")

    def __str__(self):
        return super().__str__()

    def compare_to(self, lit):
        return self.cmp(lit)

    def cmp(self, i):
       if isinstance(i, IntegerLiteral):
           return 1
       elif isinstance(i, NamedSymbol):
           return 1
       elif isinstance(i, UnnamedSymbol):
           return (str(self) > str(i)) - (str(self) < str(i))
       else:
           return 1

    def dump(self):
        return "(UnnamedSymbol @" + str(self) + ")"


class SuffixedSymbol (Symbol):
    def __init__(self, base, suffix):
       super(SuffixedSymbol, self).__init__()
       self._base = base
       self._suffix = suffix

    def is_zero(self):
        return False

    def collect_statistics(self, stats):
        return self._base.collect_statistics(stats)

    def plus(self, n):
        raise Exception("must not happen: SuffixedSymbol.plus called")

    def name(self):
        return self._base.name()

    def to_source(self, table=None):
        return self._base.to_source(table) + self._suffix

    def __hash__(self):
        return hash(str(self._base) + self._suffix)

    def __eq__(self, other):
        if not isinstance(other, SuffixedSymbol):
            return False
        else:
            return (self._base == other._base) and (self._suffix == other._base)

    def __str__(self):
        return str(self._base) + self._suffix

    def compare_to(self, lit):
        return self.cmp(lit)

    def cmp(self, i):
        if isinstance(i, IntegerLiteral):
            return 1
        elif isinstance(i, NamedSymbol):
            return (str(self) > str(i)) - (str(self) < str(i))
        elif isinstance(i, UnnamedSymbol):
            return -1
        elif isinstance(i, SuffixedSymbol):
            return (str(self) > str(i)) - (str(self) < str(i))

    def dump(self):
        return "(SuffixedSymbol " + self._base.dump() + \
            " " + self._suffix + ")"
