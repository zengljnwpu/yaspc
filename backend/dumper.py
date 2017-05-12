class Dumper ():
	def Dumper (self, s):
		self.stream = s;
		self.num_indent = 0;
		self.indent_string = "    ";

	def print_class (self, object):
		self.print_indent();
		print ("<<" + type (object).__name__ + ">>" + "\n");

	def print__class (self, object, loc):
		self.print_indent ();
		print ("<<" + type (object).__name__ + ">> (" + str(loc) + ")");

	def print_member (self, name, memb):
		self.print_pair(name + "" + str(memb));

	def print_pair (self, name, value):
		self.print_indent();
		print (name + ": " + value);

	def print_members (self, name, elems):
		self.print_indent();
		print (name + ":");
		self.indent();
		for elem in elems:
			elem.dump(self);
		self.unindent();

	def print_vars (self, name, vars):
		self.print_indent();
		print (name + ":");
		self.indent();
		for var in vars:
			self.print_class (var, var.location());
			self.print_member ("name", var.name());
			self.print_member("is_private", var.is_private());
			self.print_member("type", var.type());
			self.print_member("initializaer", var.ir());
		self.unindent();

	def print_funs (self, name, funs):
		self.print_indent();
		print (name + ":");
		self.indent();
		for var in funs:
			self.print_class (var, var.location());
			self.print_member ("name", var.name());
			self.print_member("is_private", var.is_private());
			self.print_member("type", var.type());
			self.print_member("body", var.ir());
		self.unindent();

	def indent(self):
		self.num_indent += 1;

	def unindent(self):
		self.num_indent -= 1;

	def print_indent (self):
		n = self.num_indent;
		while n > 0:
			print (self.indent_string);
			n -= 1;

