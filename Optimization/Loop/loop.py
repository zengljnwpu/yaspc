#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-6-12 下午10:09

@Author : hellolzc axiqia
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
from yaspc.Optimization.BasicBlock import BasicBlock
from yaspc.Optimization.DataFlow import ud
from yaspc.Optimization.Instruction import instruction

DEBUG = False

# Loop-invariant code motion – this can vastly improve efficiency by moving a computation
#  from inside the loop to outside of it, computing a value just once before the loop begins.


def find_dominator(block_list):
    """ find dominator of all blocks
    In control flow graphs, a node d dominates a node n
    if every path from the entry node to n must go through d.
    Notationally, this is written as d dom n (or sometimes d >> n).
    By definition, every node dominates itself.
    参考蒋立源、康慕宁《编译原理》P312程序8-4
    """
    # init set N, D
    N = set()
    for i in range(len(block_list)):
        N.add(i)
    # print(N)
    # The sets of dominator of all nodes
    D = dict()
    for i in range(len(block_list)):
        D[i] = set()
    D[0].add(0)
    for i in range(1, len(block_list)):
        D[i] = N
    change = True
    # print(D)
    while change:
        change = False
        for i in range(1, len(block_list)):
            block = block_list[i]
            newD = copy.deepcopy(N)
            for pre_block in block.preBasicBlock:
                newD = newD & D[pre_block.blockNum]
            newD.add(i)
            if D[i] != newD:
                change = True
                D[i] = newD
    print('=============DOMINATOR SET=================')
    for key in D:
        print(key, D[key])
    return D


def __insert(n, loop_set, stack):
    if n not in loop_set:
        loop_set.add(n)
        stack.append(n)


def find_loop(d, n, block_list):
    """给定回边 n->d，确定此循环的全部节点
    参考蒋立源、康慕宁《编译原理》P314程序8-5
    loop_set : The set of blockNum in the loop
    """
    stack = list()
    loop_set = set()

    loop_set.add(d)
    __insert(n, loop_set, stack)
    while len(stack) > 0:
        m = stack.pop()
        block = block_list[m]
        for pre_block in block.preBasicBlock:
            __insert(pre_block.blockNum, loop_set, stack)
    return loop_set

class Loop(object):
    """a class to save information of a loop
    """
    def __init__(self, blockNum_set, entrance):
        self.blockNum_set = blockNum_set
        self.entrance = entrance
        self.exit = []
        self.inst_set = set()

    def find_exit(self, block_list):
        """find the exit blocks of a loop
        return a list of blockNum
        """
        exit_blockNum = []
        for block in block_list:
            if block.blockNum not in self.blockNum_set:
                continue
            for succ, _ in block.succBasicBlock:
                if not succ.blockNum in self.blockNum_set:
                    exit_blockNum.append(block.blockNum)
        self.exit = exit_blockNum
        return exit_blockNum

    def update_inst_set(self, block_list):
        """inst_set: record the pos of instructions in the loop
           use this function to update the set
        """
        inst_set_of_loop = set()
        for block in block_list:
            if not block.blockNum in self.blockNum_set:
                continue
            for inst in block.instList:
                inst_set_of_loop.add(inst.pos)
        self.inst_set = inst_set_of_loop
        if DEBUG:
            print("Instructions in the loop:")
            print(inst_set_of_loop)

    def __check_a_operand(self, operand, var_reduce):
        """if a operand is constant or a variable defined out of loop,
           return True else return False
        """
        if operand.is_value():
            return True
        ud_in_loop = set(var_reduce[operand.name]) & self.inst_set
        if len(ud_in_loop) == 0:
            # definition is out of L
            return True
        else:
            return False

    def mark_unchanged_computation(self, block_list, var_reduce):
        """参考蒋立源、康慕宁《编译原理》P315
        对于循环L中的四元式r，若 "它的各运算对象是常数，或者是定值点在L之外的变量",则标记四元式r.
        处理这个四元式后，重复进行标记工作
        Parameters :
            block_list :
            loop : The set of blockNum in the loop
        Add unchanged_flag attribution for instructions in loop
        Attention: You must analysis reaching definitions first
        """
        self.update_inst_set(block_list)
        # reset unchanged_flag of all instructions
        for block in block_list:
            if not block.blockNum in self.blockNum_set:
                continue
            for inst in block.instList:
                inst.unchanged_flag = False

        for block in block_list:
            if not block.blockNum in self.blockNum_set:
                continue
            # iterate until all unchanged expressions are marked
            loop_changed_flag = True
            while loop_changed_flag:
                loop_changed_flag = False
                for inst in block.instList:
                    if inst.unchanged_flag is True:
                        continue
                    # BinaryInst
                    if isinstance(inst, instruction.BinaryInst):
                        # check left operand
                        left_flag = self.__check_a_operand(inst.left, var_reduce)
                        # check right operand
                        right_flag = self.__check_a_operand(inst.right, var_reduce)
                        # make a dicision
                        if left_flag and right_flag:
                            inst.unchanged_flag = True
                            loop_changed_flag = True
                    # UnaryInst
                    elif isinstance(inst, instruction.UnaryInst):
                        if self.__check_a_operand(inst.variable, var_reduce):
                            inst.unchanged_flag = True
                            loop_changed_flag = True

        if DEBUG:
            print("==========Unchanged Computation===========")
            print("pos\tunchanged_flag\tinst")
            for block in block_list:
                if block.blockNum in self.blockNum_set:
                    for inst in block.instList:
                        print('%d\t%s\t%s'%(inst.pos, str(inst.unchanged_flag), str(inst)))


    def __check_expression(self, block_list, the_block, the_inst, dominator_dict, var_reduce):
        """check whether the expression can be hoisted
        对循环L中每一个不变运算s:
            (s)  A := B OP C 或 A := OP B
        可以提出到循环外的运算必须满足下面条件：
            (1)s是L中A的唯一定值点。
            (2)对于A在L中的全部引用点，只有A在（s）的定值才能到达
            (3) a. s所在的基本块是L的各出口节点的必经节点
            或  b. 当控制从L的出口节点离开循环时，变量A不再活跃
        """
        # (1)s是L中A的唯一定值点
        if DEBUG:
            print('Test condition 1...')
        var_A_name = the_inst.value.name
        var_reduce_in_loop = set(var_reduce[var_A_name]) & self.inst_set
        if not len(var_reduce_in_loop) == 1:
            return False

        # (2)对于A在L中的全部引用点，只有A在（s）的定值才能到达
        if DEBUG:
            print('Test condition 2...')
        for block in block_list:
            if not block.blockNum in self.blockNum_set:
                continue
            for inst in block.instList:
                if isinstance(inst, instruction.BinaryInst):
                    if inst.left.is_variable() and inst.left.name == var_A_name:
                        # print(inst.left_ud)
                        if len(inst.left_ud) != 1 or inst.left_ud[0] != the_inst.pos:
                            return False
                    if inst.right.is_variable() and inst.right.name == var_A_name:
                        # print(inst.right_ud)
                        if len(inst.right_ud) != 1 or inst.right_ud[0] != the_inst.pos:
                            return False
                if isinstance(inst, instruction.UnaryInst):
                    if inst.variable.is_variable() and inst.variable.name == var_A_name:
                        # print(inst.var_ud)
                        if len(inst.var_ud) != 1 or inst.var_ud[0] != the_inst.pos:
                            return False
        # (3) a. s所在的基本块是L的各出口节点的必经节点
        # 或  b. 当控制从L的出口节点离开循环时，变量A不再活跃
        if DEBUG:
            print('Test condition 3...')
        self.find_exit(block_list)
        for block in block_list:
            if block.blockNum in self.exit:
                if the_block.blockNum not in dominator_dict[block.blockNum]:
                    # print('%d not in %s'%(the_block.blockNum, str(dominator_dict[block.blockNum])))
                    return False
        # 三个条件均满足，返回真
        return True

    def __hoist_expression(self, block_list, the_block, the_inst):
        """Find the front node of the loop first, 
        then hoist the expression which meet conditions.
        Return True if hoisted successfully.
        """
        for block in block_list:
            if block.blockNum == self.entrance:
                entrance_block = block
                break
        # get list of front nodes
        pre_entrance_block_list = []
        for pre_block in entrance_block.preBasicBlock:
            if pre_block.blockNum not in self.blockNum_set:
                # 前置节点必须只有一个出口
                if len(pre_block.succBasicBlock) == 1:
                    pre_entrance_block_list.append(pre_block)
                else:
                    return False
        # Insert instructions in front nodes
        for pre_block in pre_entrance_block_list:
            if isinstance(pre_block.get_last_inst(), (instruction.CJumpInst, instruction.JumpInst)):
                pre_block.instList.insert(-1, the_inst)
            else:
                pre_block.instList.append(the_inst)
        # Remove loo-invariant expressions in the loop
        for num, inst in enumerate(the_block.instList):
            if inst.pos == the_inst.pos:
                the_block.instList.pop(num)
                return True

    def hoist_loop_invariant_expressions(self, block_list, dominator_dict, var_reduce):
        """Hoist Loop-invariant expressions out of loops
            Attention: You must analysis reaching definitions first
        """
        loop_changed_flag = True
        while loop_changed_flag:
            loop_changed_flag = False
            # mark unchanged computation
            self.mark_unchanged_computation(block_list, var_reduce)
            # find computation which can be moved
            for block in block_list:
                if block.blockNum in self.blockNum_set:
                    for inst in block.instList:
                        if inst.unchanged_flag is True:
                            if self.__check_expression(block_list, block, inst, dominator_dict, var_reduce):
                                if DEBUG:
                                    print("Loop-invariant expression Found: %d\n"%inst.pos)
                                # Loop-invariant expressions can be hoisted out of loops
                                loop_changed_flag = self.__hoist_expression(block_list, block, inst)


def do_loop_optimization(block_list, debug_print=True):
    """the main function of Loop optimization
    """
    global DEBUG
    DEBUG = debug_print
    # find dominator
    D = find_dominator(block_list)

    # find loop
    loop_list = []
    count = 0
    for n in range(len(D)):
        dom_set = D[n]
        for d in dom_set:
            for succ, description in block_list[n].succBasicBlock:
                if succ == block_list[d]:
                    count = count + 1
                    print("\nFind a back edge %d -> %d"%(n, d))
                    loop_set = find_loop(d, n, block_list)
                    loop = Loop(loop_set, d)
                    loop_list.append(loop)

    if count == 0:
        print("No Loop founded")
        return
    print('Find %d loops:'%count)
    for number, loop in enumerate(loop_list):
        print(number+1, '\tEntrance:', loop.entrance)
        print('\tBlocks in loop:', loop.blockNum_set)

    for loop in loop_list:
        # analysis reaching definitions
        print('INFO: Analysis reaching definition...')
        ud.set_debug_print(False)
        var_reduce = ud.reach_def_iteration(block_list)
        ud.ud_set(block_list, var_reduce)
        ud.set_debug_print(True)
        # Loop-invariant expressions can be hoisted out of loops
        loop.hoist_loop_invariant_expressions(block_list, D, var_reduce)

