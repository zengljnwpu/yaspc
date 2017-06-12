#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Time : 17-5-19 下午5:31

@Author : axiqia
"""

import re
class DAGNode:
    def __init__(self, val=""):
        self.id = []
        self.op = None
        self.left = None
        self.right = None
        self._setNode(val)

    def _setNode(self, val=""):
        """

        :type val: str
        """
        if self.isInt(val) is True:
            self.isCons = 1
            self.value = int(val)
        else:
            self.isCons = 0
            self.id.append(val)

    def isInt(self, x):
        try:
            x = int(x)
            return isinstance(x, int)
        except ValueError:
            return False

    def setChild(self, op, left=None, right=None):
        self.left = left
        self.right = right
        self.op = op


class DAGGraph:
    def __init__(self):
        """

        :rtype: object
        """
        self.node = []

    def getNode(self, var):
        """return the node of var"""
        for nodei in self.node:
            for vari in nodei.id:
                if vari == var:
                    return nodei
        return None

    def findExpRoot(self, op1, op2, op):
        """return a root which is binary operand"""
        op1n = self.getNode(op1)
        op2n = self.getNode(op2)
        for nodei in self.node:
            if nodei.left == op1n and nodei.right == op2n and nodei.op == op:
                return nodei
        return None

    def deleteNode(self, nodei):
        """delete the num-th node"""
        if len(self.node) == 0:
            return
        self.node.remove(nodei)

    def deleteNodeId(self, nodei, var):
        """delete the all variable of num-th node"""
        if len(self.node) == 0:
            return
        index = self.node.index(nodei)
        self.node[index].id.remove(var)

    def insertNode(self, dagn):
        self.node.append(dagn)

    def insertNodeId(self, nodei, var):
        if len(self.node) == 0:
            return
        index = self.node.index(nodei)
        self.node[index].id.append(var)

    def displayGraph(self):
        print("Graph:")
        for nodei in self.node:
            if nodei.isCons == 1 and len(nodei.id) > 0:
                for var in nodei.id:
                    print(var, "=", nodei.value)

            elif nodei.left is not None and nodei.right is not None:
                for var in nodei.id:
                    if nodei.left.isCons == 1:
                        op1 = nodei.left.value
                    else:
                        op1 = nodei.left.id[0]
                    if nodei.right.isCons == 1:
                        op2 = nodei.right.value
                    else:
                        op2 = nodei.right.id[0]
                    print(var, "=", op1, nodei.op, op2)
            elif nodei.left is not None and nodei.right is None:
                for var in nodei.id:
                    print(var, "=", nodei.left.id[0])


class QUA():
    def __init__(self):
        self.type = None
        self.op = None
        self.op1 = None
        self.op2 = None
        self.ans = None


def calCons1(op, op1):
    if op == "!":
        temp = int(op1)
        temp = not temp
        return str(temp)
    if op == "-":
        temp = int(op1)
        temp = -temp
        return str(temp)


def calCons2(op, op1, op2):
    temp = None
    if op == "+":
        temp = int(op1) + int(op2)
    elif op == "-":
        temp = int(op1) - int(op2)
    elif op == "*":
        temp = int(op1) * int(op2)
    elif op == "/":
        temp = int(op1) / int(op2)
    else:
        return None
    return str(int(temp))


def makeDAG(instList):

    graph = DAGGraph()
    for qua in instList:
        newleft = 0
        newright = 0
        nodeB = graph.getNode(qua.op1)
        if nodeB is None:
            """op1--B is not defined"""
            nodeB = DAGNode(qua.op1)
            graph.insertNode(nodeB)
            newleft = 1
        if qua.type == 0:
            """ case0: (=, B, , A) """
            nodeA = graph.getNode(qua.ans)
            if nodeA is not None:
                graph.deleteNodeId(nodeA, qua.ans)
            graph.insertNodeId(nodeB, qua.ans)

        elif qua.type == 1:
            """ case1: (op, B, , A) """
            if nodeB.isCons == 1:
                """op1--B is a number"""
                if newleft == 1:
                    graph.deleteNode(nodeB)
                temp = calCons1(qua.op, qua.op1)
                nodeT = graph.getNode(temp)
                if nodeT is None:
                    nodeT = DAGNode(temp)
                    graph.insertNode(nodeT)
                nodeA = graph.getNode(qua.ans)
                if nodeA is not None:
                    graph.deleteNodeId(nodeA, qua.ans)
                graph.insertNodeId(nodeT, qua.ans)
            else:
                nodeExp = graph.findExpRoot(qua.op1, qua.op)
                if nodeExp is None:
                    nodeA = DAGNode(qua.ans)
                    nodeA.setChild(qua.op, nodeB)
                    nodeT = graph.getNode(qua.ans)
                    if nodeT is not None:
                        graph.deleteNodeId(nodeT, qua.ans)
                    graph.insertNode(nodeA, qua.ans)
                else:
                    nodeT = graph.getNode(qua.ans)
                    if nodeT is not None:
                        graph.deleteNodeId(nodeT, qua.ans)
                    graph.insertNodeId(nodeExp, qua.ans)

        else:
            """ case2: (op, B, C, A) """
            nodeC = graph.getNode(qua.op2)
            if nodeC is None:
                nodeC = DAGNode(qua.op2)
                graph.insertNode(nodeC)
                newright = 1
            if nodeB.isCons == 1 and nodeC.isCons == 1:
                temp = calCons2(qua.op, nodeB.value, nodeC.value)
                if newleft == 1:
                    graph.deleteNode(nodeB)
                if newright == 1:
                    graph.deleteNode(nodeC)
                nodeT = graph.getNode(temp)
                if nodeT is None:
                    nodeT = DAGNode(temp)
                    graph.insertNode(nodeT)
                nodeA = graph.getNode(qua.ans)
                if nodeA is not None:
                    graph.deleteNodeId(nodeA, qua.ans)
                graph.insertNodeId(nodeT, qua.ans)
            else:
                nodeExp = graph.findExpRoot(qua.op1, qua.op2, qua.op)
                if nodeExp is None:
                    nodeA = DAGNode(qua.ans)
                    nodeA.setChild(qua.op, nodeB, nodeC)
                    nodeT = graph.getNode(qua.ans)
                    if nodeT is not None:
                        graph.deleteNodeId(nodeT, qua.ans)
                    graph.insertNode(nodeA)
                else:
                    nodeT = graph.getNode(qua.ans)
                    if nodeT is not None:
                        graph.deleteNodeId(nodeT, qua.ans)
                    graph.insertNodeId(nodeExp, qua.ans)
    graph.displayGraph()

def main():
    with open("inputcode.txt") as inputCode:
        lines = inputCode.readlines()
        instList = []
        for line in lines:
            line.strip()
            split = re.split(r',', line)
            # print(type(split))
            # for index, op in enumerate(split):
            inst = QUA()
            if split[0] == " ":
                inst.type = 0
                inst.op = None
            else:
                inst.op = split[0].strip()
            inst.op1 = split[1].strip()
            if split[2] == " ":
                if inst.type != 0: inst.type = 1
                inst.op2 = None
            else:
                inst.type = 2
                inst.op2 = split[2].strip()
            inst.ans = split[3].strip()
            instList.append(inst)
        for inst in instList:
            print(inst.type, inst.op, inst.op1, inst.op2, inst.ans)

    makeDAG(instList)


if __name__ == '__main__':
    main()
