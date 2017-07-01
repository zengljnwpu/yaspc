import unittest
from backend_in_py.asm.symbol_table import *

class TestSymbolTable (unittest.TestCase):
    def test_init(self):
        a = SymbolTable ("F")
        self.assertIsInstance(a, SymbolTable)

    def test_string (self):
        a = SymbolTable ("f")
        self.assertEqual(a._new_string(), "f0")
        self.assertEqual(a._new_string(), "f1")

    def test_new_symbol (self):
        a = SymbolTable("f")
        self.assertEqual(a.new_symbol() == NamedSymbol("f0"), True)

    def test_symbol_string(self):
        a = SymbolTable ("f")
        b = NamedSymbol ("Hello")
        self.assertEqual(a.symbol_string(b), "f0")



if __name__ == '__main__':
    unittest.main()