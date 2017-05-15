import expr;
import stmt;
import dumper;
from enum import Enum;

class Op (Enum):
    ADD = 0,
    SUB = 1,
    MUL = 2,
    S_DIV = 3,
    U_DIV = 4,
    S_MOD = 5,
    U_MOD = 6,
    BIT_AND = 7,
    BIT_OR = 8,
    BIT_XOR = 9,
    BIT_LSHIFT = 10,
    BIT_RSHIFT = 11,
    ARITH_RSHIFT = 12,

    EQ = 13,
    NEQ = 14,
    S_GT = 15,
    S_GTEQ = 16,
    S_LT = 17,
    S_LTEQ = 18,
    U_GT = 19,
    U_GTEQ = 20,
    U_LT = 21,
    U_LTEQ = 22,

    UMINUS = 23,
    BIT_NOT = 24,
    NOT = 25,

    S_CAST = 26,
    U_CAST = 27;


    def intern_binary (op, is_signed = False):
        if op == "+":
            return Op.ADD;
        elif op == "-" :
            return Op.SUB;
        elif op == "*":
            return Op.MUL;
        elif op == "/":
            if is_signed:
                return Op.S_DIV;
            else:
                return Op.U_DIV;
        elif op == "%":
            if is_signed:
                return Op.S_MOD;
            else:
                return Op.U_MOD;
        elif op == "&":
            return Op.BIT_AND;
        elif op == "|":
            return Op.BIT_OR;
        elif op == "^":
            return Op.BIT_XOR;
        elif op == "<<":
            return Op.BIT_LSHIFT;
        elif op == ">>":
            if is_signed:
                return Op.ARITH_RSHIFT;
            else:
                return Op.BIT_RSHIFT;
        elif op == "==":
            return Op.EQ;
        elif op == "!=":
            return Op.NEQ;
        elif op == "<":
            if is_signed:
                return Op.S_LT;
            else:
                return Op.U_LF;
        elif op == "<=":
            if is_signed:
                return Op.S_LTEQ;
            else:
                return Op.U_LTEQ;
        elif op == ">":
            if is_signed:
                return Op.S_GT;
            else:
                return Op.U_GT;
        elif op == ">=":
            if is_signed:
                return Op.S_GTEQ;
            else:
                return Op.U_GTEQ;
        else:
            print ("unknown binary op: " + op);

    @staticmethod
    def intern_unary (op):
        if op == "+":
            print ("unary + should not be in the IR");
        elif op == "-":
            return Op.UMINUS;
        elif op == "~":
            return Op.BIT_NOT;
        elif op == "!":
            return Op.NOT;
        else:
            print ("unknown unary op: " + op);




class IR ():
    def __init__ (self, source,
                  defvars,
                  defuns,
                  funcdecls,
                  scope,
                  constant_table):
        self.source = source;
        self.defvars = defvars;
        self.defuns = defuns;
        self.funcdecls = funcdecls;
        self.scope = scope;
        self.constant_table = constant_table;
        self.gvars = [];
        self.comms = [];

    def file_name (self):
        return self.source.souce_name();

    def location (self):
        return self.source;

    def defined_variables (self):
        return self.defvars;

    def is_function_defined (self):
        if self.defuns.is_empty():
            return True;
        else:
            return False;

    def defined_funcitons(self):
        return self.defuns;

    def scope (self):
        return self.scope;

    def all_functions (self):
        result = [];
        result.append(self.defuns);
        result.append(self.funcdecls);
        return result;

    def init_variables (self):
        self.comms = [];
        self.comms = [];
        for var in self.scope.defined_glabal_scope_variables():
            if var.has_initializer == True:
                self.gvars.append(var);
            else:
                self.comms.append(var);


    #a list of all defined/declared global-scope variables
    def all_global_variables (self):
        return self.scope.all_global_variables;

    def is_global_variable_defined (self):
        if self.defined_global_variables.is_empty():
            return True;
        else:
            return False;

    #Returns the list of global variables.
    def defined_global_variables (self):
        if len (self.gvars) == 0:
            self.init_variables(self);
        else:
            return self.gvars;

    def is_common_symbol_defined(self):
        if self.defined_common_symbols().is_empty() == False:
            return True;
        else:
            return False;

    def defined_common_symbols (self):
        if (len (self.comms) == 0):
            self.init_variables(self);
        else:
            return self.comms;

    def is_string_literal_defined(self):
        if self.constant_table.is_empty() == True:
            return False;
        else:
            return True;
    def const_table (self):
        return self.constant_table;

    def dump (self):
        d = dumper.Dumper();
        d.print_class (self, self.source);
        d.print_vars ("variables", self.defvars);
        d.print_funcs ("function", self.defuns);

class Case():
    def __init__(self, value, label):
        self.value = value;
        self.label = label;

    def dump (self, d):
        d.print_class (self);
        d.print_member ("value", self.value);
        d.print_member ("label", self.label);







