import unittest
from backend_in_py.asm.statistics import *

class TestStat (unittest.TestCase):
    def test_register (self):
        a = Statistics()
        b = x86Register()
        self.assertFalse(a.does_register_used(b))
        self.assertEqual(a.num_register_used(b), 0)
        b.collect_statistics(a)
        self.assertTrue(a.does_register_used(b))
        self.assertEqual(a.num_register_used(b), 1)
        a.register_used(b)
        self.assertEqual(a.num_register_used(b), 2)

    def test_symbol (self):
        a = Statistics()
        b = UnnamedSymbol()
        self.assertFalse(a.does_symbol_used(b))
        self.assertEqual(a.num_symbol_used(b), 0)
        b.collect_statistics(a)
        self.assertTrue(a.does_symbol_used(b))
        self.assertEqual(a.num_symbol_used(b), 1)
        a.symbol_used(b)
        self.assertEqual(a.num_symbol_used(b), 2)

    def test_insn (self):
        a = Statistics()
        b = Instruction("jmp")
        self.assertEqual(a.num_instruction_usage(b.mnemonic), 0)
        b.collect_statistics(a)
        self.assertEqual(a.num_instruction_usage(b.mnemonic), 1)
        a.instruction_used(b.mnemonic)
        self.assertEqual(a.num_instruction_usage(b.mnemonic), 2)

if __name__ == '__main__':
    unittest.main()