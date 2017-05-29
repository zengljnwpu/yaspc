#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-5-27 下午9:03

@Author : axiqia
"""
import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock

DEBUG = True
def_inst = (instruction.BinaryInst, instruction.UnaryInst,\
                instruction.StoreInst)


def ud_set(block_list, var_reduce):
    """
    cal use-def set of every inst
    :param block_list: 
    :return: 
    """
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        block_def_var = dict()
        for inst in block.instList:
            if isinstance(inst, instruction.BinaryInst):
                left_var = inst.left["variable"]
                right_var = inst.right["variable"]
                inst.left_ud = []
                inst.right_ud = []
                if left_var in block_def_var.keys():
                    def_num = block_def_var[left_var]
                    inst.left_ud = [def_num]
                else:
                    inst.left_ud = list(block.in_set & var_reduce[left_var])
                if right_var in block_def_var.keys():
                    def_num = block_def_var[right_var]
                    inst.right_ud = [def_num]
                else:
                    inst.right_ud = list(block.in_set & var_reduce[right_var])

                block_def_var[inst.value["variable"]] = inst.lineth
            elif isinstance(inst, instruction.UnaryInst):
                var = inst.variable["variable"]
                if inst.variable["variable"] in block_def_var.keys():
                    inst.var_ud = (block_def_var[var])
                else:
                    inst.var_ud = list(block.in_set & var_reduce[left_var])
                block_def_var[inst.value["variable"]] = inst.lineth
            elif isinstance(inst, instruction.StoreInst):
                var = inst.address["variable"]
                block_def_var[var] = inst.lineth

    if DEBUG:
        print("===========UD SET==============")
        for (block_index, block) in enumerate(block_list):
            if block_index == 0 or block_index == len(block_list) - 1:
                continue
            print("B%d:\t" % block.blockNum)
            for inst in block.instList:
                if isinstance(inst, instruction.BinaryInst):
                    print(inst.lineth, ":\t", inst.left_ud, "\t", inst.right_ud)
                elif isinstance(inst, instruction.UnaryInst):
                    print(inst.lineth, ":\t", inst.var_ud)
            print()
def reach_def_iteration(block_list):
    """
    cal reaching-definition of every block
    :type block_list: a list of BasicBlock
    """

    """ 
        find all variable of block
        map variable defined to inst num
    """
    for (block_index, block) in enumerate(block_list):
        if block_index == 0 or block_index == len(block_list)-1:
            continue
        block.var_dict = dict()
        block.var_set = set()
        for inst in block.instList:
            if isinstance(inst, def_inst):
                if isinstance(inst, instruction.StoreInst):
                    block.var_dict[inst.address["variable"]] = inst.lineth
                    block.var_set.add(inst.address["variable"])
                else:
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
    return var_reduce


def new_entity(entity_type, value):
    entity = dict()
    entity["object"] = "entity"
    entity["type"] = "int32"
    entity["name"] = entity_type
    entity[entity_type] = value
    entity["const"] = value.isdigit()
    return entity


def constant_propagation(block_list, var_reduce, inst_list):
    change = True
    while change:
        change = False
        for block in block_list:
            for inst in block.instList:
                if isinstance(inst, instruction.BinaryInst):
                    left_ud = inst.left_ud
                    right_ud = inst.right_ud
                    if len(left_ud) == 1 and isinstance(inst_list[left_ud[0]], instruction.StoreInst):
                        inst.left = new_entity("value", inst_list[left_ud[0]].value["value"])
                    if len(right_ud) == 1 and isinstance(inst_list[right_ud[0]], instruction.StoreInst):
                        inst.right = new_entity("value", inst_list[right_ud[0]].value["value"])
                elif isinstance(inst, instruction.UnaryInst):
                    pass

    if(DEBUG):
        for inst in inst_list:
            print(inst)


def live_variable_analysis(block_list):
    for block in block_list:
        block.live_def_set = set()
        block.live_use_set = set()
        block.live_in_set = set()
        block.live_out_set = set()
        for inst in block.instList:
            if isinstance(inst, instruction.BinaryInst):
                left_var = inst.left["variable"]
                right_var = inst.right["variable"]
                value = inst.value["variable"]
                if left_var not in block.live_def_set:
                    block.live_use_set.add(left_var)
                if right_var not in block.live_def_set:
                    block.live_use_set.add(right_var)
                if value not in block.live_use_set:
                    block.live_def_set.add(value)
            elif isinstance(inst, instruction.UnaryInst):
                var = inst.variable["variable"]
                value = inst.value["variable"]
                if var not in block.live_def_set:
                    block.live_use_set.add(var)
                if value not in block.live_use_set:
                    block.live_def_set.add(value)
    if (DEBUG):
        for block in block_list:
            print(block.blockNum, "def:", block.live_def_set, ";\t", block.live_use_set)
    change = True
    while change:
        change = False
        for block in block_list[::-1]:
            for succblock in block.succBasicBlock:
                block.live_out_set = block.live_out_set | succblock[0].live_in_set
            new_in = (block.live_out_set-block.live_def_set) | block.live_use_set
            if new_in != block.live_in_set:
                change = True
                block.live_in_set = new_in
