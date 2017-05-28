#/bin/env python

# Author : axiqia, lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/12
'''
read input.txt and print basicblock.json
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import re
import json
import yaspc.Instruction.instruction as instruction
import yaspc.BasicBlock.BasicBlock as BasicBlock
import yaspc.BasicBlock.ConstructBasicBlock as ConstructBasicBlock
import yaspc.IRParser.irParser as irParser
#import yaspc.BasicBlock.ud as ud

def main():
    '''
    run a example of parser Three-address code and generate Basicblock list
    '''
    inst_list = []
    with open('dsq.ir.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    # print(ir_str)
    # print(ir_json)
    # print(json.dumps(ir_json, sort_keys=True, indent=4))
    # print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))
    for inst_dict in ir_json['functionlist'][0]['body']:
        inst_dict.pop('object')
        inst_list.append(irParser.parse_single_inst_from_json(inst_dict))
    print('function 0 body parse successfully.\n')
    for inst in inst_list:
        print(inst)
    ConstructBasicBlock.ConstructBlockList(inst_list)

if __name__ == '__main__':
    main()
