#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:54:38 2017

@author: axiqia hellolzc
"""



class BasicBlock:
    def __init__(self, number = 0):
        self.preBasicBlock = set()
        self.succBasicBlock = set()
        self.blockNum = number
        self.instList = []

