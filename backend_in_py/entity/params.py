class ParamSlot (object):
    def __init__(self, loc, param_descs: list, var_arg: bool):
        self._location = loc
        self._param_descriptors = param_descs
        self._var_arg = var_arg

    def argc (self):
        if self._var_arg:
            raise Exception ("must not happen: Param#argc for var_arg")
        return len (self._param_descriptors)

    def min_argc(self):
        return len (self._param_descriptors)

    def accept_varargs(self):
        self._var_arg = True

    def is_vararg(self):
        return self._var_arg

    @property
    def location(self):
        return self._location

class Params (ParamSlot):
    def __init__(self, loc, param_descs):
        super(Params, self).__init__(loc, param_descs, False)

    @property
    def parameters(self):
        return self._param_descriptors

    def parameters_type_ref (self):
        type_refs = []
        for param in self._param_descriptors:
            type_refs.append(param.type_node().type_ref())
        return ParamTypeRefs (self.location, type_refs, self._var_arg)
    
    def __eq__ (self, other):
        if not isinstance(other, Params):
            return False
        else:
            return other._var_arg == self._var_arg  and other._param_descriptors == self._param_descriptors

    def dump(self, d):
        d.print_node_list ("parameters", self.parameters)

