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
        d = Dumper();
        d.print_class (self, self.source);
        d.print_vars ("variables", self.defvars);
        d.print_funcs ("function", self.defuns);

class Stmt ():
    def __init__ (self, loc):
        self.location = loc;

    def location(self):
        return self.location;

    def dump (self, d):
        d.print_class (self, self.location);
        self._dump (self, d);

    def _dump (self, d):
        return;

class Expr():

    def __init__ (self, type):
        self.type = type;

    def type (self):
        return self.type;

    def is_var(self):
        return False;

    def is_addr (self):
        return False;

    def is_constant (self):
        return False;

    def asm_value (self):
        print ("Expr#asm_value called\n");

    def address (self):
        print("Expr#address called\n");

    def mem_ref (self):
        print("Expr#memref called\n");

    def address_node (self, type):
        print ("unexpected node for LHS: " + str (type));

    def det_entity_force(self):
        return False;

    def accept (self, visitor):
        return;

    def dump (self, d):
        d.print_class (self);
        d.print_member ("type", self.type);
        self._dump (self, d);

    def _dump (self, d):
        return;




