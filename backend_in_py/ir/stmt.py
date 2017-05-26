

class Stmt ():
	def __init__ (self, loc):
		self._location = loc

	def location(self):
		return self._location

	def dump (self, d):
		d.print_class (self, self._location)
		self._dump (d)

	def _dump (self, d):
		return

class Assign (Stmt):
	def __init__ (self, loc, lhs, rhs):
		super(Assign, self).__init__(loc)
		self._lhs = lhs
		self._rhs = rhs

	def lhs (self):
		return self._lhs

	def rhs (self) :
		return self._rhs

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump(self, d):
		d.print_member ("lhs", self._lhs)
		d.print_member ("rhs", self._rhs)


class CJump (Stmt):
	def __init__ (self, loc, cond, then_label, else_label):
		super().__init__(loc)
		self._cond = cond
		self._then_label = then_label
		self._else_label = else_label

	def cond(self):
		return self._cond

	def then_label(self):
		return self._then_label

	def else_label (self):
		return self._else_label

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump (self, d):
		d.print_member ("cond", self._cond)
		d.print_member ("then_label", self._then_label)
		d.print_member ("else_label", self._else_label)


class ExprStmt (Stmt):
	def __init__ (self, loc, expr):
		super().__init__(loc)
		self._expr = expr

	def expr (self):
		return self._expr

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump(self, d):
		d.print_member ("expr", self._expr)


class Jump (Stmt):
	def __init__(self, loc, label):
		super().__init__(loc)
		self._label = label

	def label (self):
		return self._label

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump(self, d):
		return d.print_member ("label", self._label)


class LabelStmt (Stmt):
	def __init__(self, loc, label):
		super().__init__(loc)
		self._label = label

	def label(self):
		return self._label

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump(self, d):
		d.print_member ("label", self._label)


class Return (Stmt):
	def __init__(self, loc, expr):
		super(Return, self).__init__(loc)
		self._expr = expr

	def expr(self):
		return self._expr

	def accept (self, visitor):
		return visitor.visit (self)

	def _dump(self, d):
		d.print_member ("expr", self._expr)