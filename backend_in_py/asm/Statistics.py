from backend_in_py.asm.Assembly import *


class Statistics ():
    def __init__ (self):
        self.register_usage = dict ({})
        self.insn_usage = dict({})
        self.symbol_usage = dict ({})

    def collect (self, assemblies):
        stats = Statistics()
        for asm in assemblies:
            asm.collect_statistics (stats)
        return stats

    def does_register_used (self, reg):
        return self.does_register_used(reg) > 0

    def num_register_used (self, reg):
        return self.fetch_count (self.register_usage, reg)

    def register_used (self, reg):
        self.increment_count (self.register_usage, reg)

    def num_instruction_usage (self, insn):
        return self.fetch_count (self.insn_usage, insn)

    def instruction_used(self, insn):
        self.increment_count(self.insn_usage, insn)

    def does_symbol_used (self, sym):
        if isinstance(sym, Label):
            return self.does_symbol_used(sym.symbol)
        else:
            return self.num_symbol_used(sym) > 0

    def num_symbol_used (self, sym):
        return self.fetch_count (self.symbol_usage, sym)

    def symbol_used (self, sym):
        self.increment_count (self.symbol_usage, sym)

    def fetch_count (self,m, key):
        n = dict(m).get (key)
        if n:
            return n
        else:
            return 0

    def increment_count (self, m, key):
        dict(m)[key] = self.fetch_count (m, key) + 1