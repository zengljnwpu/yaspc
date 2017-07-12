class Dumper (object):
	__indent_string = "    "

	def Dumper (self):
		self.__num_indent = 0

	def print_class (self, obj, loc = None):
		self.print_indent()
		temp_str = "<<" + type (obj).__name__ + ">>"
		if loc:
			temp_str += "( " + loc + ")"
		print (temp_str)

	def print_member (self, name, memb):
		self.__print_pair(name, str(memb))

	def __print_pair (self, name, value):
		self.print_indent()
		print (name + ": " + value)

	def print_members (self, name, elems):
		self.print_indent()
		print (name + ":")
		self.__indent()
		for elem in elems:
			elem.dump(self)
		self.__unindent()

	def print_vars (self, name, varlist):
		self.print_indent()
		print (name + ":")
		self.__indent()
		for var in varlist:
			self.print_class (var, var.location())
			self.print_member ("_name", var.name())
			self.print_member("_is_private", var.is_private())
			self.print_member("type", var.type())
			self.print_member("initializaer", var.ir())
		self.__unindent()

	def print_funs (self, name, funs):
		self.print_indent()
		print (name + ":")
		self.__indent()
		for var in funs:
			self.print_class (var, var.location())
			self.print_member ("_name", var.name())
			self.print_member("_is_private", var.is_private())
			self.print_member("type", var.type())
			self.print_member("body", var.ir())
		self.__unindent()

	def __indent(self):
		self.__num_indent += 1

	def __unindent(self):
		self.__num_indent -= 1

	def print_indent (self):
		n = self.__num_indent
		while n > 0:
			print (self.__indent_string)
			n -= 1

