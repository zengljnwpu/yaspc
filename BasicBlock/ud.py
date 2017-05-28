#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-5-27 下午9:03

@Author : axiqia
"""
import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock

def constrcut_set(block_list):
    pass


def ud_iteration(block_list):
    """

    :type block_list: a list of BasicBlock
    """
    DEBUG = True
    def_inst = (instruction.BinaryInst, instruction.UnaryInst)

    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        block.var_dict = dict()
        block.var_set = set()
        for inst in block.instList:
            if isinstance(inst, def_inst):
                block.var_dict[inst.value["variable"]] = inst.lineth
                block.var_set.add(inst.value["variable"])
        block.gen_set = set(block.var_dict.values())
        block.kill_set = set()

    """ init var_reduce
        key is left value 
        value is a set where the key variable definition 
    """
    var_reduce = dict()
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        for (key, value) in block.var_dict.items():
            var_reduce[key] = set()
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        for (key, value) in block.var_dict.items():
            var_reduce[key].add(value)
    if DEBUG:
        print("===========variable reduce==============")
        for var, def_set in var_reduce.items():
            print(var, end="\tdefine line:")
            for def_num in def_set:
                print(def_num, end="\t")
            print()
        print("===========GEN SET of blocks==============")
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            print("B%d:\t" % block.blockNum, end="")
            for gen_num in block.gen_set:
                print(gen_num, end="\t")
            print()

    """ kill set of blocks"""
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list) - 1:
            continue
        for var in block.var_set:
            block.kill_set = block.kill_set | var_reduce[var]
        block.kill_set = block.kill_set - block.gen_set

    if DEBUG:
        print("===========KILL SET of blocks==============")
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            print("B%d:\t" % block.blockNum, end="")
            for kill_num in block.kill_set:
                print(kill_num, end="\t")
            print()
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        block.in_set = set()
        block.out_set = block.gen_set
    change = True
    while change:
        change = False
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            new_in = set()
            for pre_block in block.preBasicBlock:
                new_in = new_in | pre_block.out_set
            if new_in != block.in_set:
                change = True
                block.in_set = new_in
                block.out_set = (block.in_set - block.kill_set) | block.gen_set
    if DEBUG:
        print("===========IN SET of blocks==============")
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            print("B%d:\t" % block.blockNum, end="")
            for in_num in sorted(block.in_set):
                print(in_num, end="\t")
            print()
        print("===========OUT SET of blocks==============")
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            print("B%d:\t" % block.blockNum, end="")
            for in_num in sorted(block.out_set):
                print(in_num, end="\t")
            print()


