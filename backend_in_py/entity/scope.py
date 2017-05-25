from backend_in_py.entity.entity import *

class Scope (object):
    def __init__(self):
        self._children = []

    def is_toplevel (self):
        return

    def toplevel (self):
        return

    def parent(self):
        return

    def add_child (self, s: LocalScope):
        self._children.append(s)

    def get (self, name: str):
        raise Exception

class LocalScope (Scope):
    def __init__(self, parent: Scope):
        super().__init__()
        self._parent = parent
        self._parent.add_child(self)
        self._variables = dict ({})

    def is_toplevel(self):
        return False

    def toplevel(self):
        return self._parent.toplevel()

    @property
    def parent(self):
        return self._parent

    @property
    def children (self):
        return self._children

    def is_defined_locally (self, name: str):
        return name in self._variables

    def defined_variable (self, var: DefinedVariable):
        if var.name in self._variables:
            raise Exception ("duplicated variable: " + var.name)
        self._variables[var.name] = var

    def allocate_tmp (self, t):
        var = DefinedVariable.tmp (t)
        self.defined_variable(var)
        return var

    def get (self, name):
        var = self._variables.get (name)
        if var:
            return var
        else:
            return self.parent.get (name)

    #
    # Returns all local variables in this scope,
    # The result DOES includes all nested local variables,
    # while it does NOT include static local variables
    def all_local_variables (self):
        result = []
        for s in self._all_local_scopes():
            result.extend(s.local_variables())
        return result

    #
    # Return local variables defined in this scope.
    # Does NOT includes children's local variables.
    # Does NOT include static local variables.
    #
    def local_variables (self):
        result = []
        for var in self._variables.values():
            if not var.is_private():
                result.append(var)
        return result

    #
    # Returns all static local variables defined in this scope
    def static_local_variables (self):
        result = []
        for s in self._all_local_scopes ():
            for var in s.variables.values():
                if var.is_private():
                    result.append(var)
        return result

    def _all_local_scopes(self):
        result = []
        self._collect_scope (result)
        return result

    def _collect_scope (self, buf):
        buf.append(self)
        for s in self.children:
            s._collect_scope (buf)

    def check_references (self):
        for var in self._variables.values():
            if not var.is_refered():
                print (str (var.location()) + "unused variable: " + str(var.name))
        for c in self.children:
            c.check_references()


class ToplevelScope (Scope):
    def __init__(self):
        super().__init__()
        self._entities = dict({})
        self._static_local_variables = []

    def is_toplevel(self):
        return True

    def toplevel(self):
        return self

    def parent(self):
        return None

    # Declare variable or funcito globally
    #
    def declare_entity (self, entity: Entity):
        e = self._entities.get (entity.name)
        if e:
            raise Exception ("duplicated declaration: " + entity.name + ":" + e.location() + " and" + entity.location())
        self._entities[entity.name] = entity

    # Define variable or function globally
    def define_entity (self, entity: Entity):
        e = self._entities.get(entity.name)
        if e and e.is_defined():
            raise Exception("duplicated declaration: " + entity.name + ":" + e.location() + " and" + entity.location())
        self._entities[entity.name] = entity

    def get (self, name: str):
        ent = self._entities.get(name)
        if not ent:
            raise Exception ("Unsolved referenmce: " + name)
        return ent

    # Returns a list of all global variables
    # All global variable means:
    #
    #   * has global scope
    #   * defined or undefined
    #   * public or private
    def all_global_variables(self):
        result = []
        for ent in self._entities.values():
            if isinstance(ent, Variable):
                result.append(ent)
        result.extend(self.static_local_variables())
        return result

    def defined_global_scope_variables (self):
        result = []
        for ent in self._entities.values():
            if isinstance(ent, DefinedVariable):
                result.append(ent)
        result.extend(self.static_local_variables())
        return result

    def static_local_variables (self):
        if not self._static_local_variables:
            self._static_local_variables = []
            for s in self._children:
                self._static_local_variables.extend(s._static_local_variables())
            seq_table = dict({})
            for var in self._static_local_variables:
                seq = seq_table.get (var.name)
                if not seq:
                    var.set_sequence (0)
                    seq_table[var.name] = 1
                else:
                    var.set_sequence (seq)
                    seq_table[var.name] = seq + 1
        return self._static_local_variables

    def check_references (self):
        for ent in self._entities.values():
            if ent.is_defined() and ent.is_private() and not ent.is_constant() and not ent.is_refered():
                print (ent.location() + "unused variable: " + ent.name)
        for fun_scope in self._children:
            for s in fun_scope._children:
                s.check_references()



