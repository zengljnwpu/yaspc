# -*- coding: utf-8 -*-
import json

from ply import yacc

from frontend import log
from frontend.ast import *
from frontend.exchange import *

#store the final data dictionary
def store(data):
    with open('data.json', 'w') as json_file:
        json_file.write(json.dumps(data))


#programNode is given by user
def programEplain(programNode):
	data = {}
	functionlist = []
	functionlsitExplain(functionlist,programNode.block.func)
	mainfunctiondata = {}
	mainfunctionExplain(mainfunctiondata,programNode.block)
    functionlist.append(mainfunctiondata)
	programExc(data,programNode.identifier,functionlist)
    store(data)

#main function is not exist real, but only used to def programNode.block.stmt
def mainfunctionExplain(mainfunctiondata,blockNode):
	mainfunctionNode=FunctionNode("main",blockNode)
	functionExc(mainfunctiondata,mainfunctionNode)

#Explain the body by block
def bodyExplain(labellist,bodylist,blockNode)
	labellistExplain(labellist,blockNode.label_list)
	constlistExplain(bodylist,blockNode.const_list)
	varlistExplain(bodylist,blockNode.var_list)
	stmtlistExplain(labellist,bodylist,blockNode.stmt)


#const definition
def constlistExplain(constlist,constlistNode)
    for i in range(len(constlistNode))
		tempdata={}
		constdefExc(tempdata,constlistNode[i])
		constlist.append(templist)

#variable definition
def varlistExplain(varlist,varlistNode)
    for i in range(len(varlistNode))
		tempdata={}
		vardefExc(tempdata,varlistNode[i])
		varlist.append(templist)

#stmtlist
def stmtlistExplain(labellist,bodylist,stmtlistNode)
for i in range(len(stmtlistNode))
		stmtExplain(labellist,bodylist,stmtlistNode[i])


#clasify the stmtNode
def stmtExplain(labellist,bodylist,stmtNode):
	if isinstance(stmtNode, AssignmentNode):
		stmtdata={}
		asignExc(stmtdata,stmtNode.var_access,stmtNode.expr)
		stmtlist.append(stmtdata)
	elif isinstance(stmtNode, BinaryOpNode):
		stmtdata={}
		binExc(stmtdata,stmtNode.op,stmtNode.left,stmtNode.right)
		stmtlist.append(stmtdata)
	elif isinstance(stmtNode, IfNode):
		ifExplain(stmtlist,stmtNode)
	elif isinstance(stmtNode, ForNode):
		forExplain(stmtlist,stmtNode)


#thenlabel elselabel endlabel
def ifExplain(stmtlist,stmtNode)
	thenlabelname="ifthenlabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	elselabelname="ifelselabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	endlabelname="ifendlabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	cjumpdata={}
	cjumpExc(cjumpdata,stmtNode.expr,thenlabelname,elselabelname)
	stmtlist.append(cjumpdata)
	thenlabelstmtdata={}
	labelstmtExc(thenlabelstmtdata,stmtNode,thenlabelname)
	stmtlist.append(thenlabelstmtdata)
	stmtlistExplain(thenstmtlist,stmtNode.iftrue)
	jumpdata={}
	jump(jumpdata,stmtNode,endlabelname)
	stmtlist.append(jumpdata)
	elselabelstmtdata={}
	labelstmtExc(elselabelstmtdata,stmtNode,elselabelname)
	stmtlist.append(elselabelstmtdata)
	stmtlistExplain(stmtlist,stmtNode.iffalse)
	endlabelstmtdata={}
	labelstmtExc(endlabelstmtdata,stmtNode,endlabelname)
	stmtlist.append(endlabelstmtdata)

#assign lhs rhs
def forExplain(stmtlist,stmtNode)
	startlabelname="forstartlabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	thenlabelname="forthenlabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	elselabelname="forelselabel_"+stmtNode.position.path+stmtNode.position().lineno+stmtNode.position().lexpos
	assigndata={}
	assignExc(assigndata,stmtNode.var,stmtNode.init_val)
	stmtlist.append(assigndata)
	startlabelstmtdata={}
	labelstmtExc(startlabelstmtdata,stmtNode,startlabelname)
	stmtlist.append(startlabelstmtdata)
	cjumpdata={}
	if stmtNode.direction==1
		exprNode=BinaryOpNode(stmtNode.var,"S_LTEQ",stmtNode.end_val)
		cjumpExc(cjumpdata,exprNode,thenlabelname,elselabelname)
	else
		exprNode=BinaryOpNode(stmtNode.var,"S_GTEQ",stmtNode.end_val)
		cjumpExc(cjumpdata,exprNode,thenlabelname,elselabelname)
	stmtlist.append(cjumpdata)
	thenlabelstmtdata={}
	labelstmtExc(thenlabelstmtdata,stmtNode,thenlabelname)
	stmtlist.append(thenlabelstmtdata)
	stmtlistExplain(stmtlist,stmtNode.body)
	varppdata={}
	varppNode=BinaryOpNode(stmtNode.var,"ADD",IntegerNode(1))
	assignExc(varppdata,stmtNode.var,varppNode)
	stmtlist.append(varppdata)
	jumpdata={}
	jumpExc(jumpdata,stmtNode,startlabelname)
	stmtlist.append(jumpdata)
	elselabelstmtdata={}
	labelstmtExc(elselabelstmtdata,stmtNode,elselabelname)
	stmtlist.append(elselabelstmtdata)

