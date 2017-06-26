from backend_in_py.entity.entity import *
import backend_in_py.type.type


#Used to describe scope of variables
class LocalScope (object):
    def __init__(self, local):
        super().__init__()
        self._variables = dict()
        for i in local:
            t = DefinedVariable (priv = False, type = i["type"], init = i["value"], name = i["name"])
            self._variables[i["name"]] = t

    def is_defined_locally (self, name: str):
        return name in self._variables

    def defined_variable (self, var: DefinedVariable):
        if var._name in self._variables:
            raise Exception ("duplicated variable: " + var._name)
        self._variables[var._name] = var

    def allocate_tmp (self, t):
        var = DefinedVariable.tmp (t)
        self.defined_variable(var)
        return var

    def get (self, name):
        var = self._variables.get (name)
        if var:
            return var

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

    def _collect_scope(self, buf):
        buf.append(self)
