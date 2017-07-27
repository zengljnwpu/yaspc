import unittest

from backend.asm.inttype import IntType


class TypeTest (unittest.TestCase):
    def test_class (self):
        self.assertEqual(IntType.get(1), IntType.INT8)
        self.assertEqual(IntType.get(2), IntType.INT16)
        self.assertEqual(IntType.get(4), IntType.INT32)
        self.assertEqual(IntType.get(8), IntType.INT64)
        with self.assertRaises(Exception):
            IntType.get(14)

    def test_size(self):
        self.assertEqual(IntType.size(IntType.INT8), 1)
        self.assertEqual(IntType.size(IntType.INT16), 2)
        self.assertEqual(IntType.size(IntType.INT32), 4)
        self.assertEqual(IntType.size(IntType.INT64), 8)


if __name__ == '__main__':
    unittest.main()