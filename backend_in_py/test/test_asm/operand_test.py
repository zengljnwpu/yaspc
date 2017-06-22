import unittest
from backend_in_py.asm.operand import *
from backend_in_py.asm.statistics import *

class TestImmediate (unittest.TestCase):
    def setUp(self):
        self.a = ImmediateValue (20)

    def test_init(self):
        self.assertIsInstance(ImmediateValue(20), ImmediateValue)
        self.assertIsInstance(ImmediateValue(IntegerLiteral(20)), ImmediateValue)

    def test_eq(self):
        self.assertEqual(self.a, ImmediateValue(20))
        self.assertNotEqual(self.a, UnnamedSymbol())

    def test_collect(self):
        self.assertIsNone(self.a.collect_statistics(dummy))

    def test_to_source(self):
        self.assertEqual(self.a.to_source(dummy), "$20")

    def test_dump(self):
        self.assertEqual(self.a.dump(), "(ImmediateValue (IntegerLiteral 20))")

class TestIndirect(unittest.TestCase):
    def setUp(self):
        self.a = IndirectMemoryReference (20, x86Register())

    def test_init(self):
        self.assertIsInstance(IndirectMemoryReference(20, x86Register()), IndirectMemoryReference)

    def test_reloc(self):
        self.assertIsInstance(IndirectMemoryReference.reloca_table (offset = 20, base = x86Register()), IndirectMemoryReference)

    def test_fix_offset (self):
        with self.assertRaises(Exception):
            self.a.fix_offset(20)
        a = IndirectMemoryReference (20, x86Register(), False)
        a.fix_offset(30)
        self.assertEqual(a.offset.value, 50)
        self.assertTrue(a.offset == IntegerLiteral (50))
        self.assertEqual(a.fixed, True)

    def test_collect(self):
        a = IndirectMemoryReference (0, x86Register())
        b = Statistics()
        self.assertFalse (b.does_register_used(a.base))
        a.collect_statistics(b)
        self.assertTrue(b.does_register_used(a.base))

    def test_to_source (self):
        with self.assertRaises(Exception):
            a = IndirectMemoryReference (20, x86Register(), False)
            a.to_source(dummy)
        a = IndirectMemoryReference (0, x86Register())
        self.assertEqual(a.to_source(dummy), "")
        a = IndirectMemoryReference(20, x86Register())
        self.assertEqual(a.to_source(dummy), "20()")

    def test_compare(self):
        self.assertEqual(self.a.cmp (DirectMemoryReference(20)), -1)
        self.assertEqual(self.a.cmp (IndirectMemoryReference(20, x86Register())), 0)

    def test_dump (self):
        self.assertEqual(self.a.dump(), "(IndirectMemoryReference (IntegerLiteral 20) )")


class TestDirect(unittest.TestCase):
    def setUp(self):
        self.a = DirectMemoryReference (20)

    def test_init(self):
        self.assertIsInstance(DirectMemoryReference(20), DirectMemoryReference)

    def test_fix_offset (self):
        with self.assertRaises(Exception):
            self.a.fix_offset(20)

    def test_collect(self):
        a = DirectMemoryReference (3)
        b = Statistics()
        self.assertIsNone(a.collect_statistics(b))

    def test_to_source (self):
        self.assertEqual(self.a.to_source(dummy), "20")

    def test_compare(self):
        self.assertEqual(self.a.cmp (DirectMemoryReference(20)), 0)
        self.assertEqual(self.a.cmp (IndirectMemoryReference(20, x86Register())), 1)

    def test_dump (self):
        self.assertEqual(self.a.dump(), "(DirectMemoryReference (IntegerLiteral 20))")


if __name__ == '__main__':
    unittest.main()