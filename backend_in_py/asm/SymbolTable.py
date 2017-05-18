

class SymbolTable ():
    __DUMMY_SYMBOL_BASE = "L";
    __dummy = SymbolTable(DUMMY_SYMBOL_BASE);

    def __init__(self, base):
        self.__base = base;
        self.__map = dict ({});
        self.__seq = 0;


    def dummy (self):
        return self.__dummy;

    def __new_string(self):
        new_str = self.__base + str(self.__seq);
        self.__seq += 1;
        return new_str;

    def new_symbol (self):
        return NamedSymbol (__new_string());

    def symbol_string (self, sym):
        str = self.__map.get (sym);
        if str:
            return str;
        else:
            new_str = __new_string(self);
            self.__map[sym] = new_str;
            return new_str;

