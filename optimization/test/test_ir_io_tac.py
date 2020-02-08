#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author : lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/24

'''
read .tac.txt and get instruction lists
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import optimization.BasicBlock.ConstructBasicBlock as ConstructBasicBlock
import optimization.BasicBlock.DestructBasicBlock as DestructBasicBlock
import optimization.IR_IO.irParser as irParser

def test_module():
    '''
    run a example of IR and print instructions list
    now is only support main function
    '''
    with open('test.tac.txt', 'r') as input_file:
        ir_strs = input_file.readlines()
    print(ir_strs)
    print('=====================================')

    inst_list = irParser.decode_TAC_list(ir_strs)
    print('TAC parsed successfully.\n')
    for inst in inst_list:
        print('%3d\t%s'%(inst.pos, str(inst)))
    print('=====================================')
    block_list = ConstructBasicBlock.ConstructBlockList(inst_list)

    inst_list = DestructBasicBlock.BlockList_to_InstList(block_list)
    new_labellist = DestructBasicBlock.generate_labellist(inst_list)
    print(json.dumps(new_labellist, sort_keys=True, indent=4))

if __name__ == '__main__':
    test_module()
