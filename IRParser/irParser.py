#/bin/env python

# Author : lzc80234@qq.com (liuzhaoci) , axiqia
# Created : 2017/5/24

'''
read .json and get instruction lists
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json

import yaspc.Instruction.instruction as instruction


def inst_parser_from_json_dict(inst_dict):
    '''
    Read a instruction dict (json format) and generate a Instruction Object
    TODO: need support for more instruction
    '''
    if(inst_dict['name'] == 'cjump'):
        pass
    # TODO: complete this function

def test_module():
    '''
    run a example of IR and print instructions list
    now is only support main function
    '''
    inst_list = []
    with open('dsq.ir.json', 'r') as input_file:
        ir_str = input_file.read()
        ir_json = json.loads(ir_str)
    #print(ir_str)
    #print(ir_json)
    #print(json.dumps(ir_json, sort_keys=True, indent=4))
    #print(json.dumps(ir_json['body'], sort_keys=True, indent=4))
    print(json.dumps(ir_json['functionlist'][0]['body'], sort_keys=True, indent=4))

if __name__ == '__main__':
    test_module()
