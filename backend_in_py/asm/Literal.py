class Literal ():
    def to_source (self):
        return;

    def to_source (self, table):
        return;

    def dump (self):
        return;

    def collect_statistics (self):
        return;

    def is_zero (self):
        return;

    def plus (self, diff):
        return;

    def cmp (self, i = IntegerLiteral):
        return;

    def cmp (self, sym = NamedSymbol):
        return;

    def cmp (self, sym = UnnamedSymbol):
        return;

    def cmp (self, sym = SuffixedSymbol):
        return;

class IntegerLiteral (Literal):
    def __init__ (self, n):
        self.value = 0;
        self.value = n;

    def equals (self, other):
        return self.value == other.value;

    def value(self):
        return self.value;

    def is_zero(self):
        return self.value == 0;

    def plus (self, diff):
        return IntegerLiteral (self.value + diff);

    def integer_literal (self):
        return self;

    def to_source (self):
        return str(self.value); 

    def to_source(self, table):
        return to_source();

    def compare_to (self, lit = IntegerLiteral):
        return lit.cmp (self);

    def cmp (self, i = IntegerLiteral):
        return i.value() == self.value();

    def cmp (self, sym = NamedSymbol):
        return False;

    def cmp (self, sym = UnnamedSymbol):
        return False;

    def cmp (self, sym = SuffixedSymbol):
        return False;

    def dump (self):
        return "(IntegerLiteral " + str(self.value) + ")";

class Symbol (Literal):
    def name (self):
        return;

    def to_string (self):
        return;

    def dump (self):
        return;

class BaseSymbol (Symbol):
    def is_zero(self):
        return False;

    def collect_statistics(self, stats):
        return stats.symbol_used (self);

    def plus (self, n):
        print ("must not happen: BaseSymbol.plus called");

class NamedSymbol (BaseSymbol):
    def __init__(self, name):
        self.name = name;

    def name(self):
        return self.name;

    def to_source(self):
        return self.name;

    def to_source (self, table):
        return self.name;

    def to_string (self):
        return "#" + self.name;

    def compare_to (self, lit):
        return - (lit.compare_to (self));
    
    def cmp (i = IntegerLiteral):
        return False;
    def cmp (self, sym = NamedSymbol):
        return self.name == sym.name;
    def cmp (self, sym = UnnamedSymbol):
        return False;
    def cmp (self, sym = SuffixedSymbol):
        return to_string() == sym.to_string();
    def dump (self):
        return "(NamedSymbol " + self.name + ")";

class UnnamedSymbol (BaseSymbol):
    def __init__(self):
        super().__init__();

    def name(self):
        print ("unnamed symbol");

    def to_source(self):
        print ("UnnamedSymbol#to_source called");

    def to_source (self, table):
        return table.symbol_string (self);

    def to_string (self):
        return super().to_string();
    
    def compare_to (self, lit = Literal):
        return False
    def cmp (self, i = IntegerLiteral):
        return False;
    def cmp (self, sym = NamedSymbol):
        return False;
    def cmp (self, sym = UnnamedSymbol):
        return to_string() == sym.to_string();
    def cmp (self, sym = SuffixedSymbol):
        return False;
    def dump (self):
        return "(UnnamedSymbol @" + str (hash (self)) + ")";

class SuffixedSymbol (Symbol):
    def __init__(self, base, suffix):
       self.base = Symbol (base);
       self.suffix = str (suffix);

    def is_zero (self):
        return False;

    def collect_statistics(self, stats):
        return self.base.collect_statistics (stats);

    def plus (self, n):
        print ("must not happen: SuffixedSymbol.plus called");

    def name(self):
        return self.base.name();

    def to_source(self):
        return self.base.to_source () + self.suffix;

    def to_source (self, table):
        return self.base.to_source (table) + self.suffix;

    def to_string (self):
        return self.base.to_string() + self.suffix;

    def compare_to (self, lit):
        return lit.compare_to (self);

    def cmp (self, i = IntegerLiteral):
        return False;

    def cmp (self, sym = NamedSymbol):
        return to_string() == sym.to_string();

    def cmp (self, sym = UnnamedSymbol):
        return False;
    
    def cmp (self, sym = SuffixedSymbol):
        return to_string == sym.to_string();

    def dump(self):
        return "(SuffixedSymbol " + self.base.dump() + \
            " " + self.suffix + ")";