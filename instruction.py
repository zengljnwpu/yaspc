#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 19:37:34 2017

@author: axiqia
"""
from enum import Enum

#defination of operator
class BinaryOpertor(Enum):
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
        
#defination of instructions
class Instruction(object):
    """The base class of all instructions"""
    def __init__(self, name, context, lineNum):
        self.name = name
        self.context = context
        self.lineNum = lineNum
        
    
class CJumpInst(Instruction):
    def __init__(self, name, context, lineNum, condition, label):
        super(CJumpInst, self).__init__(name, context, lineNum)
        self.condition = condition
        self.label = label
        
       
class JumpInst(Instruction):
    def __init__(self, name, context, lineNum, label):
        super(JumpInst, self).__init__(name, context, lineNum)
        self.label = label

class BinaryInst(Instruction):
    def __init__(self, name, context, lineNum, operator, lOperand, rOperand, result):
        super(BinaryInst, self).__init__(name, context, lineNum) 
        self.operator = operator
        self.lOperand = lOperand
        self.rOperand = lOperand
        self.result = result
    
    
class UnaryInst(Instruction):
    def __init__(self, name, context, lineNum, operator, operand, result):
        super(UnaryInst, self).__init__(name, context, lineNum) 
        self.operator = operator
        self.operand = operand
        self.result = result
        
class LoadInst(Instruction):
    def __init__(self, name, context, lineNum, src, dst):
        super(LoadInst, self).__init__(name, context, lineNum)
        self.src = src
        self.dst = dst
        
class StoreInst(Instruction):
    def __init__(self, name, context, lineNum, src, dst):
        super(StoreInst, self).__init__(name, context, lineNum)
        self.src = src
        self.dst = dst

class AllocaInst(Instruction):
    def __init__(self, name, context, lineNum, ptr):
        super(AllocaInst, self).__init__(name, context, lineNum)
        self.ptr = ptr

class CallInst(Instruction):
    def __init__(self, name, context, lineNum, paramNum, paramList):
        super(CallInst, self).__init__(name, context, lineNum)
        self.paramNum = paramNum
        self.paramList

class RetureInst(Instruction):
    def __init__(self, name, context, lineNum, param):
        super(RetureInst, self).__init__(name, context, lineNum)
        self.param = param

class LabelInst(Instruction):
    def __init__(self, name, context, lineNum, label):
        super(LabelInst, self).__init__(name, context, lineNum)
        self.label = label

