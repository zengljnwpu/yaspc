#/bin/env python

# Author : lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/12
'''
read input.txt and print basicblock.json
'''
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import re
import BasicBlock
import ConstructBasicBlock
sys.path.append("..")
import Instruction.instruction as instruction



def instParser(instString,lineNum):
    '''
    Read a instruction and generate a Instruction Object
    TODO: need support for more instruction
    '''
    split = re.split(r'\s', instString)
    if instString[-1] == ':':
        print('label')
        label = instString[0:-2]
        return instruction.LabelInst('label', instString, lineNum, label)
    elif split[-2] == 'goto':
        print('branch')
        if len(split) > 2:
            label = split[-1]
            condition = ''
            for term in split[1:-3]:
                condition += term
            return instruction.CJumpInst('cjump', instString, lineNum, condition, label)
        else:
            label = split[-1]
            return instruction.JumpInst('jump', instString, lineNum, label)

    else:
        print('other')
        return instruction.Instruction('other', instString, lineNum)

def main():
    '''
    run a example of parser Three-address code and generate Basicblock list
    '''
    instList = []
    with open('input.txt', 'r') as input_file:
        lines = input_file.readlines()
        i = 0
        for line in lines:
            i += 1
            line = line.strip()
            print('%d:\t%s'%(i, line))
            inst = instParser(line, i)
            instList.append(inst)
        #return instList
    ConstructBasicBlock.ConstructBlockList(instList)


if __name__ == '__main__':
    main()
