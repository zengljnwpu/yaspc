'''
Definitions for nodes in the abstract syntax tree.
'''
from __future__ import absolute_import, print_function

from frontend import typesys

class Node(object):

    def accept(self, visitor, arg=None):
        return visitor.visit(self, arg)

    @property
    def children(self):
        return list()

    def replace(self, child, node):
        keys = self.__dict__.keys()
        for k in keys:
            if self.__dict__[k] != child:
                continue
            self.__dict__[k] = node
            return True

        for c in filter(None, self.children):
            if c.replace(child, node):
                return True

        return False

    @property
    def position(self):
        if hasattr(self, 'pos_info'):
            return self.pos_info

        for c in filter(None, self.children):
            if not isinstance(c, Node):
                continue

            pos_info = c.position
            if pos_info is not None:
                return pos_info

    @property
    def type(self):
        if hasattr(self, '_type'):
            return self._type

    @type.setter
    def type(self, val):
        assert isinstance(val, typesys.Type)
        self._type = val

    def __str__(self):
        return self.name


class ProgramNode(Node):

    def __init__(self, identifier, block, identifier_list=None):
        self.identifier = identifier
        self.identifier_list = identifier_list
        self.block = block

    @property
    def children(self):
        return [self.identifier,
                self.identifier_list,
                self.block]

    def __str__(self):
        return "Program"


class IdentifierListNode(Node):
    def __init__(self, ident, ident_list=None):
        self._children = list()
        if ident_list:
            self._children.extend(ident_list._children)

        self._children.append(ident)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Identifier list"


class BlockNode(Node):

    def __init__(self, label_list, const_list, type_list, var_list, func,
                 stmt):
        self.label_list = label_list
        self.const_list = const_list
        self.type_list = type_list
        self.var_list = var_list
        self.func = func
        self.stmt = stmt

    @property
    def children(self):
        return [self.label_list,
                self.const_list,
                self.type_list,
                self.var_list,
                self.func,
                self.stmt]

    def __str__(self):
        return "Block"


class LabelDeclNode(Node):
    def __init__(self, label_list):
        self.label_list = label_list

    @property
    def children(self):
        return [self.label_list]

    def __str__(self):
        return "Label declaration"


class LabelListNode(Node):
    def __init__(self, label, label_list=None):
        self._children = list()
        if label_list:
            self._children.extend(label_list._children)

        self._children.append(label)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Label list"


class LabelNode(Node):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Label (%s)" % self.name


class ConstListNode(Node):

    def __init__(self, const_def, const_def_list=None):
        self._children = list()
        if const_def_list:
            self._children.extend(const_def_list._children)

        self._children.append(const_def)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Constant list"


class ConstDeclNode(Node):

    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    @property
    def children(self):
        return [self.identifier, self.expr]

    def __str__(self):
        return "Constant declaration"


class BinaryOpNode(Node):

    def __init__(self, op, left, right):
        self.left = left
        self.op = op
        self.right = right

    @property
    def children(self):
        return [self.left, self.op, self.right]

    def __str__(self):
        return "BinaryOp"


class UnaryOpNode(Node):

    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    @property
    def children(self):
        return [self.expr]

    def __str__(self):
        return "UnaryOp (%s)" % self.name


class VarAccessNode(Node):

    def __init__(self, identifier):
        self.identifier = identifier

    @property
    def children(self):
        return [self.identifier]

    def __str__(self):
        return "Variable access"


class ValueNode(Node):
    pass


class StringNode(ValueNode):

    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return "String ('%s')" % str(self.value.replace("\n", "\\n"))


class CharNode(ValueNode):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Char (%s)" % self.value


class IntegerNode(ValueNode):

    def __init__(self, value):
        self.value = int(value)

    def __str__(self):
        return "Integer (%s)" % str(self.value)


class RealNode(ValueNode):

    def __init__(self, value):
        self.value = float(value)

    def __str__(self):
        return "Real (%s)" % str(self.value)


class TypeDeclListNode(Node):
    def __init__(self, typedef, typedecl_list=None):
        self._children = list()
        if typedecl_list:
            self._children.extend(typedecl_list._children)

        self._children.append(typedef)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Type definition list"


class TypeDeclNode(Node):

    def __init__(self, identifier, type_denoter):
        self.identifier = identifier
        self.type_denoter = type_denoter

    @property
    def children(self):
        return [self.identifier, self.type_denoter]

    def __str__(self):
        return "Type definition"


class TypeNode(Node):

    def __init__(self, identifier, attr=None):
        self.attr = attr
        self.identifier = identifier

    @property
    def children(self):
        return [self.attr,
                self.identifier]

    def __str__(self):
        return "Type"


class EnumTypeNode(Node):

    def __init__(self, identifier_list, attr=None):
        self.attr = attr
        self.identifier_list = identifier_list

    @property
    def children(self):
        return [self.attr,
                self.identifier_list]

    def __str__(self):
        return "Enum type"


class RangeNode(Node):

    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    @property
    def children(self):
        return [self.start, self.stop]

    def __str__(self):
        return "Range"


class ArrayTypeNode(Node):

    def __init__(self, index_list, component_type):
        self.index_list = index_list
        self.component_type = component_type

    @property
    def children(self):
        return [self.index_list, self.component_type]

    def __str__(self):
        return "Array type"


class IndexListNode(Node):
    def __init__(self, index_type, index_list=None):
        self._children = list()
        if index_list:
            self._children.extend(index_list._children)

        self._children.append(index_type)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Index list"


class RecordTypeNode(Node):

    def __init__(self, section_list, variant):
        self.variant = variant
        self.section_list = section_list

    @property
    def children(self):
        return [self.section_list, self.variant]

    def __str__(self):
        return "Record type"


class RecordSectionListNode(Node):

    def __init__(self, section, section_list=None):
        self._children = list()
        if section_list:
            self._children.extend(section_list._children)

        self._children.append(section)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Record section list"


class RecordSectionNode(Node):

    def __init__(self, identifier_list, type_denoter):
        self.identifier_list = identifier_list
        self.type_denoter = type_denoter

    @property
    def children(self):
        return [self.identifier_list, self.type_denoter]

    def __str__(self):
        return "Record section"

    
class VariantPartNode(Node):
    def __init__(self, variant_selector, variant_list):
        self.variant_selector = variant_selector
        self.variant_list = variant_list

    @property
    def children(self):
        return [self.variant_selector, self.variant_list]

    def __str__(self):
        return "Variant part"


class VariantSelectorNode(Node):
    def __init__(self, tag_type, tag_field=None):
        self.tag_type = tag_type
        self.tag_field = tag_field

    @property
    def children(self):
        return [self.tag_type, self.tag_field]

    def __str__(self):
        return "Variant selector"


class VariantListNode(Node):

    def __init__(self, variant, variant_list=None):
        self._children = list()
        if variant_list:
            self._children.extend(variant_list._children)

        self._children.append(variant)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Variant list"


class VariantNode(Node):

    def __init__(self, case_list, record_list, variant_part):
        self.case_list = case_list
        self.record_list = record_list
        self.variant_part = variant_part

    @property
    def children(self):
        return [self.case_list,
                self.record_list,
                self.variant_part]

    def __str__(self):
        return "Variant"


class CaseConstListNode(Node):

    def __init__(self, case_constant, case_constant_list=None):
        self._children = list()
        if case_constant_list:
            self._children.extend(case_constant_list._children)

        self._children.append(case_constant)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Case constant list"


class CaseConstNode(Node):

    def __init__(self, constant):
        self.constant = constant

    @property
    def children(self):
        return [self.constant]

    def __str__(self):
        return "Case constant"


class CaseRangeNode(Node):

    def __init__(self, first_constant, last_constant):
        self.first_constant = first_constant
        self.last_constant = last_constant

    @property
    def children(self):
        return [self.first_constant, self.last_constant]

    def __str__(self):
        return "Case range"


class SetTypeNode(Node):

    def __init__(self, base_type):
        self.base_type = base_type

    @property
    def children(self):
        return [self.base_type]

    def __str__(self):
        return "Set type"

    
class FileTypeNode(Node):

    def __init__(self, component_type):
        self.component_type = component_type

    @property
    def children(self):
        return [self.component_type]

    def __str__(self):
        return "File type"


class PointerTypeNode(Node):

    def __init__(self, domain_type):
        self.domain_type = domain_type

    @property
    def children(self):
        return [self.domain_type]

    def __str__(self):
        return "Pointer type"


class VarDeclListNode(Node):

    def __init__(self, var_decl, var_decl_list=None):
        self._children = list()
        if var_decl_list:
            self._children.extend(var_decl_list._children)

        self._children.append(var_decl)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Variable declaration list"


class VarDeclNode(Node):

    def __init__(self, identifier_list, type_denoter):
        self.identifier_list = identifier_list
        self.type_denoter = type_denoter

    @property
    def children(self):
        return [self.identifier_list, self.type_denoter]

    def __str__(self):
        return "Variable declaration"


class FunctionListNode(Node):

    def __init__(self, func, func_list=None):
        self._children = list()
        if func_list:
            self._children.extend(func_list._children)

        self._children.append(func)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Function list"


class ProcedureNode(Node):

    def __init__(self, header, block, attr=None):
        self.attr = attr
        self.header = header
        self.block = block

    @property
    def children(self):
        return [self.attr,
                self.header,
                self.block]

    def __str__(self):
        return "Procedure"


class ProcedureHeadNode(Node):

    def __init__(self, identifier, param_list=None):
        self.identifier = identifier
        self.param_list = param_list

    @property
    def children(self):
        return [self.identifier, self.param_list]

    def __str__(self):
        return "Procedure head"


class ParameterListNode(Node):

    def __init__(self, param, param_list=None):
        self._children = list()
        if param_list:
            self._children.extend(param_list._children)

        self._children.append(param)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Parameter list"


class ValueParameterNode(Node):

    def __init__(self, identifier_list, type_denoter):
        self.identifier_list = identifier_list
        self.type_denoter = type_denoter

    @property
    def children(self):
        return [self.identifier_list, self.type_denoter]

    def __str__(self):
        return "Value parameter"


class RefParameterNode(Node):

    def __init__(self, identifier_list, type_denoter):
        self.identifier_list = identifier_list
        self.type_denoter = type_denoter

    @property
    def children(self):
        return [self.identifier_list, self.type_denoter]

    def __str__(self):
        return "Reference parameter"


class FunctionNode(Node):

    def __init__(self, header, block, attr=None):
        self.attr = attr
        self.header = header
        self.block = block

    @property
    def children(self):
        return [self.attr,
                self.header,
                self.block]

    def __str__(self):
        return "Function"


class FunctionHeadNode(Node):

    def __init__(self, ret, identifier=None, param_list=None):
        self.return_type = ret
        self.identifier = identifier
        self.param_list = param_list

    @property
    def children(self):
        return [self.identifier, self.param_list]

    def __str__(self):
        return "Function head"


class StatementListNode(Node):

    def __init__(self, stmt, stmt_list=None):
        self._children = list()

        if stmt_list:
            self._children.extend(stmt_list._children)

        if isinstance(stmt, StatementListNode):
            self._children.extend(stmt._children)
        else:
            self._children.append(stmt)

    @property
    def children(self):
        return filter(None, self._children)

    def __str__(self):
        return "Statement list"


class LabeledStatementNode(Node):

    def __init__(self, label, stmt):
        self.label = label
        self.stmt = stmt

    @property
    def children(self):
        return [self.label, self.stmt]

    def __str__(self):
        return "Labeled Statement"


class RepeatNode(Node):

    def __init__(self, body, cond):
        self.body = body
        self.cond = cond

    @property
    def children(self):
        return [self.cond, self.body]

    def __str__(self):
        return "Repeat"


class WhileNode(Node):

    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    @property
    def children(self):
        return [self.cond, self.body]

    def __str__(self):
        return "While"


class ForNode(Node):

    def __init__(self, var, init_val, dir_, end_val, body):
        self.var = var
        self.value_start = init_val
        self.direction = dir_
        self.value_end = end_val
        self.body = body

    @property
    def children(self):
        return [self.var,
                self.value_start,
                self.value_end,
                self.body]

    def __str__(self):
        return "For (%s)" % self.direction


class WithNode(Node):

    def __init__(self, rec_var_list, statement_list):
        self.rec_var_list = rec_var_list
        self.statement_list = statement_list

    @property
    def children(self):
        return [self.rec_var_list, self.statement_list]

    def __str__(self):
        return "With"


class IfNode(Node):

    def __init__(self, expr, true_stmt, false_stmt=None):
        self.expr = expr
        self.iftrue = true_stmt
        self.iffalse = false_stmt

    @property
    def children(self):
        return [self.expr, self.iftrue, self.iffalse]

    def __str__(self):
        return "If"


class AssignmentNode(Node):

    def __init__(self, var_access, expr):
        self.var_access = var_access
        self.expr = expr

    @property
    def children(self):
        return [self.var_access, self.expr]

    def __str__(self):
        return "Assignment"


class PointerAccessNode(Node):

    def __init__(self, var_access):
        self.var_access = var_access

    @property
    def children(self):
        return [self.var_access]

    def __str__(self):
        return "Pointer access"


class IndexedVarNode(Node):

    def __init__(self, var_access, index_expr_list):
        self.var_access = var_access
        self.index_expr_list = index_expr_list

    @property
    def children(self):
        return [self.var_access, self.index_expr_list]

    def __str__(self):
        return "Indexed variable"


class ExprListNode(Node):
    def __init__(self, expr, expr_list=None):
        self._children = list()
        if expr_list:
            self._children.extend(expr_list._children)

        self._children.append(expr)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Expression list"


class FieldAccessNode(Node):
    def __init__(self, var_access, identifier):
        self.var_access = var_access
        self.identifier = identifier

    @property
    def children(self):
        return [self.var_access, self.identifier]

    def __str__(self):
        return "Field access"


class FunctionCallNode(Node):

    def __init__(self, identifier, arg_list=None):
        self.identifier = identifier
        self.arg_list = arg_list

    @property
    def children(self):
        return [self.identifier, self.arg_list]

    def __str__(self):
        return "Function call"


class ArgumentListNode(Node):
    def __init__(self, expr, expr_list=None):
        self._children = list()
        if expr_list:
            self._children.extend(expr_list._children)

        self._children.append(expr)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Argument list"


class ArgumentNode(Node):

    def __init__(self, expr):
        self.expr = expr

    @property
    def children(self):
        return [self.expr]

    def __str__(self):
        return "Argument"


class GotoNode(Node):

    def __init__(self, label):
        self.label = label

    @property
    def children(self):
        return [self.label]

    def __str__(self):
        return "Goto"


class CaseStatementNode(Node):

    def __init__(self, case_index, case_list_element_list, otherwise=None):
        self.case_index = case_index
        self.case_list_element_list = case_list_element_list
        self.otherwise = otherwise

    @property
    def children(self):
        return [self.case_index, self.case_list_element_list, self.otherwise]

    def __str__(self):
        return "Case statement"


class CaseListElementListNode(Node):

    def __init__(self, case_list_element, case_list_element_list=None):
        self._children = list()
        if case_list_element_list:
            self._children.extend(case_list_element_list._children)

        self._children.append(case_list_element)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Case list element list"


class CaseListElementNode(Node):

    def __init__(self, case_constant_list, statement):
        self.case_constant_list = case_constant_list
        self.statement = statement

    @property
    def children(self):
        return [self.case_constant_list, self.statement]

    def __str__(self):
        return "Case list element"


class VarLoadNode(Node):

    def __init__(self, var_access):
        self.var_access = var_access

    @property
    def children(self):
        return [self.var_access]

    def __str__(self):
        return "Variable load"


class NullNode(Node):

    def __str__(self):
        return "Null"


class SetNode(Node):

    def __init__(self, member_list):
        self.member_list = member_list

    @property
    def children(self):
        return [self.member_list]

    def __str__(self):
        return "Set"


class SetEmptyNode(Node):

    def __str__(self):
        return "Set empty"


class SetMemberListNode(Node):

    def __init__(self, member, member_list=None):
        self._children = list()
        if member_list:
            self._children.extend(member_list._children)

        self._children.append(member)

    @property
    def children(self):
        return self._children

    def __str__(self):
        return "Set member list"


class SetMemberRangeNode(Node):

    def __init__(self, member, expr):
        self.member = member
        self.expr = expr

    @property
    def children(self):
        return [self.member, self.expr]

    def __str__(self):
        return "Set member range"


class OpNode(Node):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Operator (%s)" % str(self.name)


class IdentifierNode(Node):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Identifier (%s)" % self.name

class TypeConvertNode(Node):

    def __init__(self, child):
        assert isinstance(child, Node)
        self.child = child

    @property
    def children(self):
        return [self.child]

    def __str__(self):
        return "Type convert"


class VarReferenceNode(Node):

    def __init__(self, var_access):
        self.var_access = var_access

    @property
    def children(self):
        return [self.var_access]

    def __str__(self):
        return "Variable reference"