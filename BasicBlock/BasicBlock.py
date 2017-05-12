#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 10:54:38 2017

@author: axiqia hellolzc
"""



class BasicBlock:
    def __init__(self):
        self.preBasicBlock = set()
        self.succBasicBlock = set()
        self.no = 0
        self.instList = []

