'''
Base class of node visitors in frontend
'''
from __future__ import absolute_import, print_function

from frontend import ast


class NodeVisitor(object):

    def visit(self, node, arg=None):
        if node is not None and isinstance(node, ast.Node):
            # print log_prefix(node)
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.default_visit)
            return visitor(node, arg)

    def missing_visit(self, node, arg=None):
        for c in node.children:
            if isinstance(c, ast.Node):
                self.default_visit(c, arg)

    def default_visit(self, node, arg=None):
        for c in filter(None, node.children):
            if isinstance(c, ast.Node):
                c.accept(self, arg)


class DefaultVisitor(NodeVisitor):

    def default_visit(self, node, arg=None):
        name = node.__class__.__name__
        if name.endswith('ListNode'):
            return self._visit_ListNode(node, arg)
        else:
            return NodeVisitor.default_visit(self, node, arg)

    def _visit_ListNode(self, node, arg):
        l = []
        for c in filter(None, node.children):
            val = c.accept(self, arg)
            if isinstance(val, list):
                l.extend(val)
            elif val is not None:
                l.append(val)

        return l


class PrintVisitor(NodeVisitor):

    def __init__(self):
        self.level = 0

    def visit_VarDeclListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_StatementListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_ConstListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_FunctionListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_ParameterListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_ArgumentListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_IdentifierListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_TypeDefListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_RecordSectionListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_CaseListElementListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_CaseConstListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_LabelListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_SetMemberListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def visit_VariantListNode(self, node, arg=None):
        NodeVisitor.default_visit(self, node, arg)

    def default_visit(self, node, arg=None):
        self.print_node(node)

        self.level += 1
        for c in filter(None, node.children):
            if isinstance(c, ast.Node):
                c.accept(self)
            else:
                self.print_string(c)

        self.level -= 1

    def print_string(self, node, arg=None):
        pos = '?'

        prefix = pos + '  \t'
        spacer = ''.join([' ' * (2 * self.level)])
        print((prefix + spacer + str(node)))

    def print_node(self, node, arg=None):
        pos = node.position
        if not pos:
            pos = '?'

        ty = node.type
        if not ty:
            ty = '(?)'

        prefix = str(pos) + '  \t' + str(ty.__class__.__name__[0:-4]) + '  \t'
        # prefix = str(pos) + '  \t' + str(ty) + '  \t'

        spacer = ''.join([' ' * (2 * self.level)])
        print((prefix + spacer + str(node)))
