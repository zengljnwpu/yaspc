import unittest
from backend_in_py.asm.Assembly import *
from backend_in_py.asm.SymbolTable import *
from backend_in_py.asm.Statistics import *

class TestAssembly(unittest.TestCase):
    def setUp(self):
        self.a = Assembly()
        self.table = SymbolTable ("Hello")
        self.stats = Statistics()

    def test_to_source_empty (self):
        self.assertFalse(self.a.to_source(self.table))

    def test_dump (self):
        self.assertFalse (self.a.dump())

    def test_is_instruction (self):
        self.assertFalse (self.a.is_instruction())

    def test_is_label (self):
        self.assertFalse (self.a.is_label())

    def test_is_direct (self):
        self.assertFalse(self.a.is_directive())

    def test_is_comment (self):
        self.assertFalse(self.a.is_comment())

    def test_is_stat(self):
        self.assertFalse(self.a.collect_statistics(self.stats))


class TestLabel(unittest.TestCase):
    def setUp(self):
        self.a = Label()
        self.table = SymbolTable ("Hello")

    def test_init (self):
        self.assertTrue(Label())
        self.assertTrue(Label(NamedSymbol ("Hello")))
        self.assertTrue(Label (SuffixedSymbol (12,32)))

    def test_is_label (self):
        self.assertTrue(self.a.is_label())

    def test_dump (self):
        self.assertTrue(self.a.dump())

    def test_to_source (self):
        self.assertTrue(self.a.to_source(self.table))

class TestInst (unittest.TestCase):
    def setUp(self):
        self.a = Instruction("Test")
        self.table = SymbolTable ("Hello")

    def test_init (self):
        self.assertTrue(Label())
        self.assertTrue(Label(NamedSymbol ("Hello")))
        self.assertTrue(Label (SuffixedSymbol (12,32)))

    def test_build (self):
        self.assertTrue(self.a.is_label())

    def test_is_insn (self):
        self.assertTrue(self.a.is_instruction())

    def test_is_jump (self):
        self.assertTrue(self.a.is_instruction())

    def test_num_operands (self):

    def test_operand1 (self):

    def test_operand2 (self):

    def test_jump (self):

    def test_collect_stats(self):

    def test_to_source (self):

    def test_str(self):

    def test_dump(self):


class TestDirective (unittest.TestCase):

class TestComment (unittest.TestCase):

if __name__ == '__main__':
    unittest.main()