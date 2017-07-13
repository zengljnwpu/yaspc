#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 19:37:34 2017

@author: hellolzc axiqia
"""

class Entity(object):
    """The struct of operand and return value
        entity has two type: value, variable
    """
    def __init__(self, object, type):
        self.object = object
        self.type = type
    def __str__(self):
        pass
    def to_dict(self):
        """json format
        """
        pass
    def is_variable(self):
        """if entity type is variable return true"""
        return self.object == "variable"
    def is_value(self):
        """if entity type is value return true"""
        return self.object == "value"

class Value(Entity):
    """
        e.g.
        "value": {
            "object": "value",
            "type": "s_int16",
            "value": 2
        }
    """
    def __init__(self, object, type, value):
        super(Value, self).__init__(object, type)
        assert object == 'value', 'type error!'
        self.value = value

    def __str__(self):
        return str(self.value)

    def to_dict(self):
        """json IR format
        """
        return {"object": "value", "type": self.type, "value": self.value}

class Variable(Entity):
    """
    e.g.
        "variable": {
            "const": false,
            "object": "variable",
            "type": "s_int16",
            "name": "%1",
            "is_private": false
        }
    """
    def __init__(self, object, type, name, is_private=False, const=False):
        super(Variable, self).__init__(object, type)
        assert object == 'variable', 'type error!'
        self.name = name
        self.is_private = is_private
        self.const = const

    def __str__(self):
        return self.name

    def to_dict(self):
        """json IR format
        """
        return {"object": "variable", "type": self.type, "name": self.name,
                "is_private": self.is_private, "const": self.const}

def auto_gen_entity_from_dict(entity_dict):
    """generate Value or Variable class according to entity_dict['object']
    """
    if entity_dict['object'] == 'value':
        return Value(**entity_dict)
    else:
        return Variable(**entity_dict)

#defination of instructions
class Instruction(object):
    """The base class of all instructions
        name: instruction type (eg. cjump bin ...)
        context: The three address form of this instruction (legacy)
        line_number: the line number in source file (used to report errors)
        object: For Instruction is 'instruction'
        pos: the line number in three address codes of one body
    """
    def __init__(self, name, context=None, line_number=0, pos=0, object='instruction'):
        self.object = object
        self.name = name
        self.context = context
        self.line_number = line_number
        self.pos = pos

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            pass

    def to_dict(self):
        """json IR format
        """
        pass


class CJumpInst(Instruction):
    '''conditional jump instruction'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 cond=None, thenlabel=None, elselabel=None):
        super(CJumpInst, self).__init__(name, context, line_number, pos)
        assert name == 'cjump', 'type error!'
        if isinstance(cond, Entity):
            self.cond = cond
        else:
            self.cond = auto_gen_entity_from_dict(cond)
        self.thenlabel = thenlabel
        self.elselabel = elselabel

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'if %s goto %s else goto %s'% \
                (str(self.cond), self.thenlabel, self.elselabel)
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "cond": self.cond.to_dict(), "thenlabel": self.thenlabel,
                "elselabel": self.elselabel}

class JumpInst(Instruction):
    '''unconditional jump instruction'''
    def __init__(self, name, context=None, line_number=0, pos=0, label=None):
        super(JumpInst, self).__init__(name, context, line_number, pos)
        assert name == 'jump', 'type error!'
        self.label = label
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'goto %s'%self.label
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "label": self.label}

class BinaryInst(Instruction):
    '''二元运算指令'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 op=None, left=None, right=None, value=None):
        super(BinaryInst, self).__init__(name, context, line_number, pos)
        assert name == 'bin', 'type error!'
        self.op = op

        if isinstance(left, Entity):
            self.left = left
        else:
            self.left = auto_gen_entity_from_dict(left)
        if isinstance(right, Entity):
            self.right = right
        else:
            self.right = auto_gen_entity_from_dict(right)
        if isinstance(value, Entity):
            self.value = value
        else:
            self.value = auto_gen_entity_from_dict(value)

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s = %s %s %s'%(str(self.value), str(self.left), self.op, str(self.right))
    # 使用装饰器实现只读属性，下同
    @property
    def left_variable_name(self):
        '''如果左操作数是变量，返回变量名
        如果是值（value），返回值的字符串
        此方法已过时，建议使用下面函数替代
        '''
        if self.left.is_variable():
            return self.left.name
        else:
            return str(self.left.value)
    @property
    def right_variable_name(self):
        '''如果右操作数是变量，返回变量名
        如果是值（value），返回值的字符串
        此方法已过时，建议使用下面函数替代
        '''
        if self.left.is_variable():
            return self.left.name
        else:
            return str(self.left.value)
    @property
    def return_variable_name(self):
        '''返回返回值变量名
        此方法已过时，建议使用下面函数替代
        '''
        return self.value.name
    def is_left_a_variable(self):
        '''if left operand is a variable, return true
        else return false
        此方法已过时，建议使用下面函数替代
        '''
        return self.left.is_variable()
    def is_right_a_variable(self):
        '''if right operand is a variable, return true
        else return false
        此方法已过时，建议使用下面函数替代
        '''
        return self.right.is_variable()
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "op": self.op, "left": self.left.to_dict(), "right": self.right.to_dict(),
                "value": self.value.to_dict()}


class UnaryInst(Instruction):
    '''单目运算指令'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 op=None, variable=None, value=None):
        super(UnaryInst, self).__init__(name, context, line_number, pos)
        assert name == 'uni', 'type error'
        self.op = op
        if isinstance(variable, Entity):
            self.variable = variable
        else:
            self.variable = auto_gen_entity_from_dict(variable)
        if isinstance(value, Entity):
            self.value = value
        else:
            self.value = auto_gen_entity_from_dict(value)
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s = %s %s'%(self.value.name, self.op, self.variable.name)
    # readonly attributions
    @property
    def variable_name(self):
        '''如果操作数是变量，返回变量名
        如果是值（value），返回值的字符串
        此方法已过时，建议使用下面函数替代
        '''
        return self.variable.name
    @property
    def return_variable_name(self):
        '''返回返回值变量名
        此方法已过时，建议使用下面函数替代
        '''
        return self.value.name
    def is_variable_a_variable(self):
        '''if self.variable is a variable, return true
        else return false
        此方法已过时，建议使用下面函数替代
        '''
        return self.variable.is_variable()
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "op": self.op, "variable": self.variable.to_dict(), "value": self.value.to_dict()}

class AllocaInst(Instruction):
    '''same as variable_definition'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 variablename=None, var_type=None):
        super(AllocaInst, self).__init__(name, context, line_number, pos)
        assert name == 'variable_definition', 'type error'
        self.variablename = variablename
        self.var_type = var_type
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'alloca %s type:%s'%(self.variablename, self.var_type)
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "variablename": self.variablename, "var_type": self.var_type}

class LoadInst(Instruction):
    '''load'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 address=None, value=None):
        super(LoadInst, self).__init__(name, context, line_number, pos)
        assert name == 'load', 'type error'
        if isinstance(address, Entity):
            self.address = address
        else:
            self.address = auto_gen_entity_from_dict(address)
        if isinstance(value, Entity):
            self.value = value
        else:
            self.value = auto_gen_entity_from_dict(value)

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'load %s from %s'%(str(self.value), str(self.address))
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "address": self.address.to_dict(), "value": self.value.to_dict()}

class StoreInst(Instruction):
    '''store'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 address=None, value=None):
        super(StoreInst, self).__init__(name, context, line_number, pos)
        assert name == 'store', 'type error'
        if isinstance(address, Entity):
            self.address = address
        else:
            self.address = auto_gen_entity_from_dict(address)
        if isinstance(value, Entity):
            self.value = value
        else:
            self.value = auto_gen_entity_from_dict(value)

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'store %s to %s'%(str(self.value), str(self.address))
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "address": self.address.to_dict(), "value": self.value.to_dict()}

class CallInst(Instruction):
    '''call'''
    def __init__(self, name, context=None, line_number=0, pos=0,
                 functionname=None, parameterlist=None, value=None):
        super(CallInst, self).__init__(name, context, line_number, pos)
        assert name == 'call', 'type error'
        self.functionname = functionname
        self.parameterlist = parameterlist
        if isinstance(value, Entity):
            self.value = value
        else:
            self.value = Variable(**value)

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'call %s'%self.functionname
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "functionname": self.functionname, "parameterlist": self.parameterlist,
                "value": self.value.to_dict()}

class RetureInst(Instruction):
    '''return'''
    def __init__(self, name, context=None, line_number=0, pos=0, ret=None):
        super(RetureInst, self).__init__(name, context, line_number, pos)
        assert name == 'return', 'type error'
        if isinstance(ret, Entity):
            self.ret = ret
        else:
            self.ret = auto_gen_entity_from_dict(ret)

    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return 'return %s'%str(self.ret)
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "ret": self.ret.to_dict()}

class LabelInst(Instruction):
    '''label_definition'''
    def __init__(self, name, context=None, line_number=0, pos=0, labelname=None):
        super(LabelInst, self).__init__(name, context, line_number, pos)
        assert name == 'label_definition', 'type error:%s'%name
        self.labelname = labelname
    def __str__(self):
        if self.context is not None:
            return self.context
        else:
            return '%s:'%self.labelname
    def to_dict(self):
        """json IR format
        """
        return {"object": "instruction", "name": self.name, "line_number": self.line_number,
                "labelname": self.labelname}
