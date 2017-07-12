import unittest

from backend.asm.type import Type


class TypeTest (unittest.TestCase):
    def test_class (self):
        self.assertEqual(Type.get(1), Type.INT8)
        self.assertEqual(Type.get(2), Type.INT16)
        self.assertEqual(Type.get(4), Type.INT32)
        self.assertEqual(Type.get(8), Type.INT64)
        with self.assertRaises(Exception):
            Type.get(14)

    def test_size(self):
        self.assertEqual(Type.size(Type.INT8), 1)
        self.assertEqual(Type.size(Type.INT16), 2)
        self.assertEqual(Type.size(Type.INT32), 4)
        self.assertEqual(Type.size(Type.INT64), 8)


if __name__ == '__main__':
    unittest.main()