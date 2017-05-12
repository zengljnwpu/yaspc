#/bin/env python

# Author : lzc80234@qq.com (liuzhaoci)
# Created : 2017/5/12

import sys
sys.path.append("..")
import Instruction.instruction as instruction
import BasicBlock
import re

def instParser(str):
    split = re.split(r'\s',str)
    if str[-1] == ':':
        print('label')
    elif split[-2] == 'goto':
        print('branch')
    else:
        print('other')

def main():
    #run a example of parser Three-address code and generate Basicblock list
    with open('input.txt','r') as input_file:
        lines = input_file.readlines()
        i = 0
        for line in lines:
            i += 1
            line = line.strip()
            print('%d:\t%s'%(i,line))
            instParser(line)


if __name__ == '__main__':
    main()
