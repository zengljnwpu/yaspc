#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 19:37:34 2017

@author: axiqia hellolzc
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
    def __init__(self, name, context, line_number):
        self.name = name
        self.context = context
        self.line_number = line_number


class CJumpInst(Instruction):
    def __init__(self, name, context, line_number, condition, label):
        super(CJumpInst, self).__init__(name, context, line_number)
        self.condition = condition
        self.gotoLabel = label


class JumpInst(Instruction):
    def __init__(self, name, context, line_number, label):
        super(JumpInst, self).__init__(name, context, line_number)
        self.gotoLabel = label

class BinaryInst(Instruction):
    def __init__(self, name, context, line_number, operator, lOperand, rOperand, result):
        super(BinaryInst, self).__init__(name, context, line_number)
        self.operator = operator
        self.lOperand = lOperand
        self.rOperand = rOperand
        self.result = result


class UnaryInst(Instruction):
    def __init__(self, name, context, line_number, operator, operand, result):
        super(UnaryInst, self).__init__(name, context, line_number)
        self.operator = operator
        self.operand = operand
        self.result = result

class LoadInst(Instruction):
    def __init__(self, name, context, line_number, srcAddress, dst):
        super(LoadInst, self).__init__(name, context, line_number)
        self.srcAddress = srcAddress
        self.dst = dst

class StoreInst(Instruction):
    def __init__(self, name, context, line_number, src, dstAddress):
        super(StoreInst, self).__init__(name, context, line_number)
        self.src = src
        self.dstAddress = dstAddress

class AllocaInst(Instruction):
    def __init__(self, name, context, line_number, ptr):
        super(AllocaInst, self).__init__(name, context, line_number)
        self.ptr = ptr
        # TODO : add the size of the memory to allocate

class CallInst(Instruction):
    def __init__(self, name, context, line_number, paramNum, paramList):
        super(CallInst, self).__init__(name, context, line_number)
        self.paramNum = paramNum
        self.paramList = paramList
        # TODO: add the function address

class RetureInst(Instruction):
    def __init__(self, name, context, line_number, param):
        super(RetureInst, self).__init__(name, context, line_number)
        self.param = param

class LabelInst(Instruction):
    def __init__(self, name, context, line_number, label):
        super(LabelInst, self).__init__(name, context, line_number)
        self.label = label

