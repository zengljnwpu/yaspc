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
        print ("expr#asm_value called\n");

    def address (self):
        print("expr#address called\n");

    def mem_ref (self):
        print("expr#memref called\n");

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

class Addr (Expr):

	def __init__ (self, type, entity):
		super().__init__(type);
		self.entity = entity;

	def is_addr (self):
		return True;

	def entity (self):
		return self.entity;

	def address (self):
		return self.entity.address();

	def mem_ref(self):
		return self.entity.mem_ref();

	def get_entity_force (self):
		return self.entity;

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("entity", self.entity.name());

class Bin (Expr):
	def __init__ (self, type, op,left, right):
		super().__init__(type);
		self.op = op;
		self.left = left;
		self.right = right;

	def left (self):
		return self.left;

	def right (self):
		return self.right;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump (self, d):
		d.print_member ("op", self.op.to_string());
		d.print_member ("left", self.left);
		d.print_member ("right", self.right);

class Call (Expr):
	def __init__ (self, type, expr, args):
		super.__init__(type);
		self.expr = expr;
		self.args = args;

	def expr(self):
		return self.expr;

	def args(self):
		return self.args;

	def num_args (self):
		return len (self.args);

	#return True is this funcall is NOT a function pointer call
	def is_static_call (self):
		return (self.expr.get_entity_force() is Function);

	#Return a funciton object which is refered by expression
	def function (self):
		ent = self.expr.get_entity_force();
		if ent == False:
			print ("not a static funcall\n");
		else:
			ent;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("expr", self.expr);
		d.print_members ("args", self.args);

class Int (Expr):
	def __init__ (self, type, value):
		super().__init__(type);
		self.value = value;

	def value (self):
		return self.value;

	def is_constant(self):
		return True;

	def asm_value(self):
		return ImmediateValue (IntegerLiteral (value));

	def mem_ref(self):
		print ("must not happen: IntValue#memref\n");

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("value", self.value);

class Mem (Expr):
	def __init__(self, type, expr):
		super().__init__(type);
		self.expr = expr;

	def expr(self):
		return self.expr;

	def address_node (self, type):
		return self.expr;

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("expr", self.expr);

class Str (Expr):
	def __init__(self, type, entry):
		super().__init__(type);
		self.entry = entry;

	def entry(self):
		return self.entry;

	def symbol (self):
		return self.entry.symbol();

	def is_constant(self):
		return True;

	def mem_ref(self):
		return self.entry.mem_ref();

	def address(self):
		return self.entry.address();

	def asm_value(self):
		return self.entry.address();

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("entry", self.entry);

class Uni (Expr):
	def __init__(self, type, op,expr):
		super().__init__(type);
		self.op = op
		self.expr = expr;

	def expr(self):
		return self.expr;

	def op(self):
		return self.op;

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member("op", self.op);
		d.print_member ("expr", self.expr);

class Var (Expr):
	def __init__(self, type, entity):
		super().__init__(type);
		self.entity = entity;

	def is_var (self):
		return True;

	def type(self):
		if (super().type == False):
			print ("Var is too big to load by 1 insn\n");
		else:
			return super().type;

	def name(self):
		return self.entity.name();

	def entity (self):
		return self.entity;

	def address (self):
		return self.entity.address();

	def mem_ref(self):
		return self.entity.mem_ref();

	def address_node(self, type):
		return Addr (type, self.entity);

	def get_entity_force(self):
		return self.entity;

	def accept(self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member("op", self.op);
		d.print_member ("expr", self.expr);