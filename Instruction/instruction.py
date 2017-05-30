#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 19:37:34 2017

@author: hellolzc axiqia
"""
#from enum import Enum

#defination of operator
'''class BinaryOpertor(Enum):
    """Enumeration defination of binary operator"""
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    SHL = 5

class UnaryOperator(Enum):
    """Enumeration defination of unary operator"""
    INVERT = 1

class Operand(object):
    """The struct of operand"""
    def __init__(self, opValue, opType):
        self.opValue = opValue
        self.opType = opType
'''
def get_entity_name_string(entity_dict):
    '''get name of a entity'''
    return str(entity_dict[entity_dict['name']])


#defination of instructions
class Instruction(object):
    """The base class of all instructions
        name: instruction type (eg. cjump bin ...)
        context: The three address form of this instruction (legacy)
        line_number: the line number in source file (used to report errors)
        object: For Instruction is 'instruction'
        pos: the line number in three address codes of one body
    """
    def __init__(self, name, context=None, line_number=0, filename='',
                 pos=0, object='instruction'):
        self.object = 'instruction'
        self.name = name
        self.filename = filename
        self.context = context
        self.line_number = line_number
        self.pos = pos

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            pass


class CJumpInst(Instruction):
    '''conditional jump instruction'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 cond=None, thenlabel=None, elselabel=None):
        super(CJumpInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'cjump', 'type error!'
        self.cond = cond
        self.thenlabel = thenlabel
        self.elselabel = elselabel
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'if %s goto %s else goto %s'% \
                (get_entity_name_string(self.cond), self.thenlabel, self.elselabel)

class JumpInst(Instruction):
    '''unconditional jump instruction'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0, label=None):
        super(JumpInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'jump', 'type error!'
        self.label = label
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'goto %s'%self.label

class BinaryInst(Instruction):
    '''二元运算指令'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 op=None, left=None, right=None, value=None):
        super(BinaryInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'bin', 'type error!'
        self.op = op
        self.left = left
        self.right = right
        self.value = value
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s = %s %s %s'%(get_entity_name_string(self.value), \
                    get_entity_name_string(self.left), self.op, get_entity_name_string(self.right))

class UnaryInst(Instruction):
    '''单目运算指令'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 op=None, variable=None, value=None):
        super(UnaryInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'uni', 'type error'
        self.op = op
        self.variable = variable
        self.value = value
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s = %s %s'%(get_entity_name_string(self.value), self.op, \
                    get_entity_name_string(self.variable))

class AllocaInst(Instruction):
    '''same as variable_definition'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 variablename=None, var_type=None):
        super(AllocaInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'variable_definition', 'type error'
        self.variablename = variablename
        self.var_type = var_type
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'alloca %s type:%s'%(self.variablename, self.var_type)

class LoadInst(Instruction):
    '''load'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 address=None, value=None):
        super(LoadInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'load', 'type error'
        self.address = address
        self.value = value
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'load %s from %s'%(get_entity_name_string(self.value),
                                      get_entity_name_string(self.address))

class StoreInst(Instruction):
    '''store'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 address=None, value=None):
        super(StoreInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'store', 'type error'
        self.address = address
        self.value = value
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'store %s to %s'%(get_entity_name_string(self.value),
                                     get_entity_name_string(self.address))


class CallInst(Instruction):
    '''call'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0,
                 functionname=None, parameterlist=None, value=None):
        super(CallInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'call', 'type error'
        self.functionname = functionname
        self.parameterlist = parameterlist
        self.value = value
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'call %s'%self.functionname


class RetureInst(Instruction):
    '''return'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0, ret=None):
        super(RetureInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'return', 'type error'
        self.ret = ret
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'return %s'%get_entity_name_string(self.ret)


class LabelInst(Instruction):
    '''label_definition'''
    def __init__(self, name, context=None, line_number=0, filename='', pos=0, labelname=None):
        super(LabelInst, self).__init__(name, context, line_number, filename, pos)
        assert name == 'label_definition', 'type error:%s'%name
        self.labelname = labelname
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s:'%self.labelname

