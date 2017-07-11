from enum import Enum


class Op (Enum):
    ADD = 1
    SUB = 2
    MUL = 3
    S_DIV = 4
    U_DIV = 5
    S_MOD = 6
    U_MOD = 7
    BIT_AND = 8
    BIT_OR = 9
    BIT_XOR = 10,
    BIT_LSHIFT = 11,
    BIT_RSHIFT = 12,
    ARITH_RSHIFT = 13,

    EQ = 20,
    NEQ = 21,
    S_GT = 22,
    S_GTEQ = 23,
    S_LT = 24,
    S_LTEQ = 25,
    U_GT = 26,
    U_GTEQ = 27,
    U_LT = 28,
    U_LTEQ = 29,

    UMINUS = 30,
    BIT_NOT = 31,
    NOT = 32,

    S_CAST = 33,
    U_CAST = 34

    def __eq__(self, other):
        if not isinstance(other, Op):
            return False
        else:
            if self.name == other.name:
                return True
            else:
                return False


    @staticmethod
    def op_factory (op):
        if op == "+":
            return Op.ADD
        elif op == "-" :
            return Op.SUB
        elif op == "*":
            return Op.MUL
        elif op == "/":
                return Op.U_DIV
        elif op == "%":
                return Op.U_MOD
        elif op == "&":
            return Op.BIT_AND
        elif op == "|":
            return Op.BIT_OR
        elif op == "^":
            return Op.BIT_XOR
        elif op == "<<":
            return Op.BIT_LSHIFT
        elif op == ">>":
                return Op.BIT_RSHIFT
        elif op == "==":
            return Op.EQ
        elif op == "!=":
            return Op.NEQ
        elif op == "<":
                return Op.U_LF
        elif op == "<=":
                return Op.U_LTEQ
        elif op == ">":
                return Op.U_GT
        elif op == ">=":
                return Op.U_GTEQ
        else:
           raise Exception ("unknown binary op: " + op)

    @staticmethod
    def intern_binary (op, is_signed):
        if op == "+":
            return Op.ADD
        elif op == "-" :
            return Op.SUB
        elif op == "*":
            return Op.MUL
        elif op == "/":
            if is_signed:
                return Op.S_DIV
            else:
                return Op.U_DIV
        elif op == "%":
            if is_signed:
                return Op.S_MOD
            else:
                return Op.U_MOD
        elif op == "&":
            return Op.BIT_AND
        elif op == "|":
            return Op.BIT_OR
        elif op == "^":
            return Op.BIT_XOR
        elif op == "<<":
            return Op.BIT_LSHIFT
        elif op == ">>":
            if is_signed:
                return Op.ARITH_RSHIFT
            else:
                return Op.BIT_RSHIFT
        elif op == "==":
            return Op.EQ
        elif op == "!=":
            return Op.NEQ
        elif op == "<":
            if is_signed:
                return Op.S_LT
            else:
                return Op.U_LF
        elif op == "<=":
            if is_signed:
                return Op.S_LTEQ
            else:
                return Op.U_LTEQ
        elif op == ">":
            if is_signed:
                return Op.S_GT
            else:
                return Op.U_GT
        elif op == ">=":
            if is_signed:
                return Op.S_GTEQ
            else:
                return Op.U_GTEQ
        else:
           raise Exception ("unknown binary op: " + op)

    @staticmethod
    def intern_unary (op):
        if op == "+":
            raise Exception ("unary+ should not be in the ir")
        elif op == "-":
            return Op.UMINUS
        elif op == "~":
            return Op.BIT_NOT
        elif op == "!":
            return Op.NOT
        else:
            raise Exception ("unknown unary _op: " + op)



