from enum import Enum, auto

class Op (Enum):
    ADD = auto()
    SUB = auto(),
    MUL = auto(),
    S_DIV = auto(),
    U_DIV = auto(),
    S_MOD = auto(),
    U_MOD = auto(),
    BIT_AND = auto(),
    BIT_OR = auto(),
    BIT_XOR = auto(),
    BIT_LSHIFT = auto(),
    BIT_RSHIFT = auto(),
    ARITH_RSHIFT = auto(),

    EQ = auto(),
    NEQ = auto(),
    S_GT = auto(),
    S_GTEQ = auto(),
    S_LT = auto(),
    S_LTEQ = auto(),
    U_GT = auto(),
    U_GTEQ = auto(),
    U_LT = auto(),
    U_LTEQ = auto(),

    UMINUS = auto(),
    BIT_NOT = auto(),
    NOT = auto(),

    S_CAST = auto(),
    U_CAST = auto()

    @staticmethod
    def op_factory (op: str):
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
    def intern_binary (op: str, is_signed: bool):
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
    def intern_unary (op: str):
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



