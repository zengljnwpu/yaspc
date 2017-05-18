class Statistics ():
    def __init__ (self):
        self.__register_usage = dict ({});
        self.__insn_usage = dict({});
        self.__symbol_usage = dict ({});

    def collect (self, assemblies):
        stats = Statistics();
        for asm in assemblies:
            asm.collect_statistics (self.stats);
        return stats;

    def does_register_used (self, reg):
        return does_register_used(reg) > 0

    def num_register_used (self, reg):
        return fetch_count (self.__register_usage, reg);

    def register_used (self, reg):
        increment_count (self.__register_usage, reg);

    def num_instruction_usage (self, insn):
        return fetch_count (self.__insn_usage, reg);

    def instruction_used(self, reg):
        increment_count(self.__insn_usage, reg);

    def does_symbol_used (self, sym):
        if isinstance(sym, Label):
            return num_symbol_used (sym.symbol()) > 0;
        else:
            return num_symbol_used(sym) > 0;

    def num_symbol_used (self, sym):
        return fetch_count (self.__symbol_usage, sym);

    def symbol_used (self, sym):
        increment_count (self.__symbol_usage, sym);

    def fetch_count (m, key):
        n = m.get (key);
        if n:
            return n;
        else:
            return 0;

    def increment_count (m, key):
        m[key] = fetch_count (m, key) + 1;