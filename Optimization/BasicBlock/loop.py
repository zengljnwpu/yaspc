#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-6-12 下午10:09

@Author : axiqia
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import yaspc.Optimization.BasicBlock.BasicBlock


DEBUG = False

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
    if DEBUG:
        print(N)
    # The sets of dominator of all nodes
    D = dict()
    for i in range(len(block_list)):
        D[i] = set()
    D[0].add(0)
    for i in range(1, len(block_list)):
        D[i] = N
    change = True
    if DEBUG:
        print(D)
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
    print(D)
    return D


def __insert(n, loop, stack):
    if n not in loop:
        loop = loop.add(n)
        stack.append(n)


def find_loop(d, n, block_list):
    """给定回边 n->d，确定此循环的全部节点
    参考蒋立源、康慕宁《编译原理》P314程序8-5
    """
    stack = list()
    loop = set()

    loop.add(d)
    __insert(n, loop, stack)
    while len(stack) > 0:
        m = stack.pop()
        block = block_list[m]
        for pre_block in block.preBasicBlock:
            __insert(pre_block.blockNum, loop, stack)
    return loop

def do_loop_optimization(block_list):
    """the main function of Loop optimization
    """
    D = find_dominator(block_list)
    loop_list = list()
    for n in range(len(D)):
        dom_set = D[n]
        for d in dom_set:
            for succ, description in block_list[n].succBasicBlock:
                if succ == block_list[d]:
                    print("find a back edge %d -> %d"%(n, d))
                    loop = find_loop(d, n, block_list)
                    loop_list.append(loop)
    print(loop_list)
