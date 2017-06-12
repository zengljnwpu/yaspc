#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-6-12 下午10:09

@Author : axiqia
"""

import yaspc.Optimization.BasicBlock.BasicBlock
import copy


def insert(n, loop, stack):
    if n not in loop:
        loop = loop.add(n)
        stack.append(n)


def find_loop(d, n, block_list):
    stack = list()
    loop = set()

    loop.add(d)
    insert(n)
    while len(stack):
        m = stack.pop()
        block = block_list[m]
        for pre_block in block.preBasicBlock:
            insert(pre_block.blockNum, loop, stack)
    return loop


def dominator(block_list):
    """ init set N, D"""
    N = set()
    for i in range(len(block_list)):
        N.add(i)
    print(N)
    D = dict()
    for i in range(len(block_list)):
        D[i] = set()
    D[0].add(0)
    for i in range(1, len(block_list)):
        D[i] = N
    change = True
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

    loop_list = list()
    for n in D:
        dom_set = D[n]
        for d in dom_set:
            if block_list[n].succBasicBlock == block_list[d]:
                loop = find_loop(d, n, block_list)
                loop_list.append(loop)
