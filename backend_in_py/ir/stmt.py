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

class Assign (Stmt):
	def __init__ (self, loc, lhs, rhs):
		super(Stmt, loc).__init__;
		self.lhs = lhs;
		self.rhs = rhs;

	def lhs (self):
		return self.lhs;

	def rhs (self) :
		return self.rhs;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("lhs", self.lhs);
		d.print_member ("rhs", self.rhs);

class CJump (Stmt):
	def __init__ (self, loc, cond, then_label, else_label):
		super().__init__(loc);
		self.cond = cond;
		self.then_label = then_label;
		self.else_label = else_label;

	def cond(self):
		return self.cond;

	def then_label(self):
		return self.then_label;

	def else_label (self):
		return self.else_label;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump (self, d):
		d.print_member ("cond", self.cond);
		d.print_member ("then_label", self.then_label);
		d.print_member ("else_label", self.else_label);

class ExprStmt (Stmt):
	def __init__ (self, loc, expr):
		super().__init__(loc);
		self.expr = expr;

	def expr (self):
		return self.expr;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("expr", self.expr);

class Jump (Stmt):
	def __init__(self, loc, label):
		super().__init__(loc);
		self.label = label;

	def label (self):
		return self.label;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		return d.print_member ("label", self.label);

class LabelStmt (Stmt):
	def __init__(self, loc, label):
		super().__init__(loc);
		self.label = label;

	def label(self):
		return self.label;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("label", self.label);

class Return (Stmt):
	def __init__(self, loc, expr):
		super().__init__(loc);
		self.expr = expr;

	def expr(self):
		return self.expr;

	def accept (self, visitor):
		return visitor.visit (self);

	def _dump(self, d):
		d.print_member ("expr", self.expr);