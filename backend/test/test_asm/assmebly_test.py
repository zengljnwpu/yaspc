import unittest
from backend.asm.assembly import *
from backend.asm.symbol_table import *
from backend.asm.statistics import *

class TestAssembly(unittest.TestCase):
    def setUp(self):
        self.a = Assembly()
        self.table = dummy
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
        self.a = Label(NamedSymbol("Hello"))
        self.table = dummy

    def test_init (self):
        self.assertIsInstance(Label (NamedSymbol("Hello")), Label)
        self.assertIsInstance(Label (), Label)

    def test_is_label (self):
        self.assertTrue(self.a.is_label())

    def test_to_source (self):
        self.assertEqual(Label(NamedSymbol("Hello")).to_source(self.table), "Hello:")

    def test_dump (self):
        self.assertEqual(self.a.dump(), "(Label (NamedSymbol Hello))")

class TestInst (unittest.TestCase):
    def setUp(self):
        self.a = Instruction ("jmp")

    def test_init(self):
        a = Instruction ("jmp")
        self.assertIsInstance(a, Instruction)


    def test_build (self):
        a = Instruction ("jmp")
        self.assertIsInstance(a.build ("jne", x86Register()), Instruction)

    def test_is_jump (self):
        a = Instruction ("jmp")
        b = Instruction ("add")
        self.assertTrue (a.is_jump_instruction())
        self.assertFalse(b.is_jump_instruction())

    def test_is_insn (self):
        self.assertTrue(Instruction("jmp"))

    def test_num_operands(self):
        a = Instruction ("jne")
        self.assertEqual(a.num_operands(), 0)
        a = Instruction ("jmp", suffix= "", a1 = AbsoluteAddress(x86Register()))
        self.assertEqual(a.num_operands(), 1)
        a = Instruction("jmp", suffix="", a1=AbsoluteAddress(x86Register()), a2 = x86Register())
        self.assertEqual(a.num_operands(), 2)

    def test_op1(self):
        a = x86Register()
        b = Instruction ("jne", suffix="", a1 = a)
        self.assertEqual(b.operand1(), a)

    def test_op2(self):
        a = x86Register()
        c = x86Register ()
        b = Instruction("jne", suffix="", a1=a, a2 = c)
        self.assertEqual(b.operand2(), c)
        return

    def test_jmp_dest(self):
        a = DirectMemoryReference(20)
        b = Instruction("jmp", suffix="", a1=a)
        self.assertTrue(b.jmp_destination() == IntegerLiteral (20))

    def test_collect(self):
        a = Instruction ("jmp")
        b = Statistics()
        self.assertEqual(b.num_instruction_usage(a.mnemonic), 0)
        a.collect_statistics(b)
        self.assertEqual(b.num_instruction_usage(a.mnemonic), 1)

    def test_str(self):
        a = Instruction("jmp")
        self.assertEqual(str(a), "#<Insn jmp>")

class TestDirective (unittest.TestCase):
    def setUp(self):
        self.a = Directive (" Hello ")
        self.table = dummy

    def test_is_dit (self):
        self.assertTrue(self.a.is_directive())

    def test_to_source (self):
        self.assertEqual(self.a.to_source(self.table), " Hello ")

    def test_dump (self):
        self.assertEqual(self.a.dump(), "(Directive Hello)")

class TestComment (unittest.TestCase):
    def setUp(self):
        self.a = Comment ("Hello", 1)
        self.table = dummy

    def test_is_cmt (self):
        self.assertTrue(self.a.is_comment())

    def test_to_source (self):
        self.assertEqual(self.a.to_source(self.table), "\t  # Hello")

    def test_indent (self):
        self.assertEqual(self.a.indent(), "  ")


    def test_dump (self):
        self.assertEqual(self.a.dump(), "(Comment Hello)")


if __name__ == '__main__':
    unittest.main()