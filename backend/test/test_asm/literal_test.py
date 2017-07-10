import unittest
from backend.asm.literal import *
from backend.asm.symbol_table import *
from backend.asm.statistics import *

class TestInteger(unittest.TestCase):
    def setUp(self):
        self.a = IntegerLiteral(10)

    def test_equal (self):
        tmp = Symbol()
        self.assertFalse (self.a == tmp)
        tmp = IntegerLiteral (10)
        self.assertTrue(self.a == tmp)
        tmp = IntegerLiteral (20)
        self.assertFalse(self.a == tmp)

        tmp = Symbol()
        self.assertFalse(self.a.equals(tmp))
        tmp = IntegerLiteral(10)
        self.assertTrue(self.a.equals(tmp))
        tmp = IntegerLiteral(20)
        self.assertFalse(self.a.equals(tmp))

    def test_is_zero (self):
        tmp = IntegerLiteral (0)
        self.assertTrue(tmp.is_zero())
        tmp = IntegerLiteral (10)
        self.assertFalse(tmp.is_zero())

    def test_add (self):
        tmp = IntegerLiteral (10)
        self.assertEqual(tmp + 20, IntegerLiteral (30))

        tmp = IntegerLiteral(10)
        self.assertEqual(tmp.plus (20), IntegerLiteral(30))

    def test_integer (self):
        self.assertTrue(self.a.integer_literal())

    def test_to_source (self):
        self.assertEqual(self.a.to_source(), "10")

    def test_compare (self):
        self.assertEqual(self.a.compare_to(5), 1)
        self.assertEqual(self.a.compare_to(10), 0)
        self.assertEqual(self.a.compare_to(20), -1)

        tmp = IntegerLiteral (10)
        self.assertEqual(self.a.compare_to(tmp), 0)
        tmp = IntegerLiteral(4)
        self.assertEqual(self.a.compare_to(tmp), 1)
        tmp = IntegerLiteral(20)
        self.assertEqual(self.a.compare_to(tmp), -1)

        tmp = NamedSymbol ("Hello")
        self.assertEqual(self.a.compare_to(tmp), -1)
        tmp = UnnamedSymbol ()
        self.assertEqual(self.a.compare_to(tmp), -1)
        tmp = SuffixedSymbol (10, 20)
        self.assertEqual(self.a.compare_to(tmp), -1)

    def test_dump (self):
        self.assertEqual(self.a.dump(), "(IntegerLiteral 10)")
        return

class TestBase (unittest.TestCase):
    def test_collect(self):
        a = BaseSymbol ()
        b = Statistics ()
        self.assertFalse(b.does_symbol_used(a))
        self.assertIsNone(a.collect_statistics(b))
        self.assertTrue (b.does_symbol_used(a))

    def test_str (self):
        a = BaseSymbol()
        self.assertTrue(str(a))

    def test_plus (self):
        a = BaseSymbol()
        with self.assertRaises(Exception):
            a.plus (10)

class TestNamedSymbol (unittest.TestCase):
    def setUp(self):
        self.a = NamedSymbol ("F")

    def test_init (self):
        self.assertTrue (NamedSymbol(2))
        self.assertTrue(NamedSymbol ("2"))
        with self.assertRaises(Exception):
            NamedSymbol("")
        a = NamedSymbol (2)
        self.assertIsInstance(a, NamedSymbol)

    def to_source (self):
        self.assertEqual(self.a.to_source(), "F")

    def to_str (self):
        self.assertEqual(str(self.a), "#F")

    def test_compare (self):
        tmp = IntegerLiteral (10)
        self.assertEqual(self.a.compare_to(tmp), 1)
        tmp = NamedSymbol ("F")
        self.assertEqual(self.a.compare_to(tmp), 0)
        tmp = UnnamedSymbol ()
        self.assertEqual(self.a.compare_to(tmp), -1)
        tmp = SuffixedSymbol (10, str(20))
        self.assertNotEqual(self.a.compare_to(tmp), 1)

    def test_dump (self):
        self.assertEqual (self.a.dump(), "(NamedSymbol F)")

class TestUnnamedSymbol (unittest.TestCase):
    def setUp(self):
        self.a = UnnamedSymbol ()

    def test_name(self):
        with self.assertRaises(Exception):
            self.a.name()

    def test_to_source(self):
        with self.assertRaises(Exception):
            self.a.to_source()

    def test_str (self):
        self.assertTrue (str(self.a))

    def test_compare(self):
        tmp = IntegerLiteral(10)
        self.assertEqual(self.a.compare_to(tmp), 1)
        tmp = NamedSymbol("F")
        self.assertEqual(self.a.compare_to(tmp), 1)
        tmp = UnnamedSymbol()
        self.assertNotEqual(self.a.compare_to(tmp), 0)
        tmp = SuffixedSymbol(10, str(20))
        self.assertEqual(self.a.compare_to(tmp), 1)

    def test_dump (self):
        self.assertTrue(self.a.dump())

class TestSuffixedSymbol (unittest.TestCase):
    def setUp(self):
        a = NamedSymbol("Hello")
        self.a = SuffixedSymbol (a, "World")

    def test_is_zero (self):
        self.assertFalse(self.a.is_zero())

    def test_collect(self):
        b = Statistics()
        self.assertFalse(b.does_symbol_used(self.a))
        self.a.collect_statistics(b)
        self.assertTrue(b.does_symbol_used(self.a))

    def test_name(self):
        self.assertEqual(self.a.name(), "Hello")

    def test_to_source (self):
        self.assertEqual(self.a.to_source(), "HelloWorld")

    def test_str(self):
        self.assertEqual(str(self.a), "#HelloWorld")

    def test_compare(self):
        tmp = IntegerLiteral(10)
        self.assertEqual(self.a.compare_to(tmp), 1)
        tmp = NamedSymbol("HelloWorld")
        self.assertEqual(self.a.compare_to(tmp), 0)
        tmp = UnnamedSymbol()
        self.assertEqual(self.a.compare_to(tmp), -1)
        tmp = SuffixedSymbol(NamedSymbol("Hello"), "World")
        self.assertEqual(self.a.compare_to(tmp), 0)

    def test_dump (self):
        self.assertTrue(self.a.dump())

if __name__ == '__main__':
    unittest.main()