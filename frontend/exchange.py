# -*- coding: utf-8 -*-

from ply import yacc

from frontend import log
from frontend.ast import *
from frontend.explain import *

#blockExc is used in main module, function or  process
def blockExc(blockdata,blockNode):
    blockdata['object']="block"
    blockdata['filename']=blockNode.position().path
    blockdata['line_number']=blockNode.position().lineno
	constlist=[]
    constlistExplain(constlist,blockNode.const_list)
    blockdata['consts']=constlist
	varlist=[]
	varlistExplain(varlist,blockNode.var_list)
	blockdata['variable']=varlist
'''	typelist=[]
	typelistExt(typelist,blockNode.type_list)
    blockdata['typelist']=typelist
	labellist=[]
	labellistExt(labellist,blockNode.label_list)
    blockdata['labellist']=labellist
	funclist=[]
	funclistExt(funclist,blockNode.func)
    blockdata['functionlist']=funclist
'''
	stmtlist=[]
	stmtlistExplain(stmtlist,blockNode.stmt)
    blockdata['statements']=stmtlist
'''
block
{
    "object": "block",
    "filename": "test.pas",
    "line_number": "2",
    "consts": [...],
    "variable": [...],
    "typelist": [...],
    "labellist": [...],
    "functionlist": [...],
    "statements": [...]
}'''




def constExc(constdata,constNode):
    constdata['object']="const_definition"
    constdata['filename']=constNode.position().path
    constdata['line_number']=constNode.position().lineno
    constdata['name']=constNode.identifier
    constdata['type']=constNode.type()
'''
const
{
    "object": "const_definition",
    "filename": "test.cl",
    "line_number": 3,
    "name": "a",
    "type": "int8",
    
}
'''


def varExc(vardata,varNode):
    vardata['object']="variable_definition"
    vardata['filename']=varNode.position().path
    vardata['line_number']=varNode.position().lineno
    vardata['name']=varNode.identifier
    vardata['type']=varNode.type()
'''
variable
{
    "object": "variable_definition",
    "filename": "test.cl",
    "line_number": 3,
    "name": "a",
    "type": "int8",
}
'''


def exprExc(exprdata,exprNode)
	exprdata['object']="expression"
    exprdata['type']=exprNode.type
	templist=[]
	stmtExc(templist,exprNode)
	instruction=templist[0]
	exprdata['instruction']=instruction


# assign lhs rhs
def asignExc(stmtdata,lhsNode,rhsNode)
	stmtdata['object']="instruction"
    stmtdata['filename']=lhsNode.position().path
    stmtdata['line_number']=lhsNode.position().lineno	
	stmtdata['name']="assign"
	v_acdata={}
	exprExc(v_acdata,stmtNode.var_access)
	stmtdata['lhs']=v_acdata
	exprdata={}
	exprExc(exprdata,stmtNode.expr)
	stmtdata['rhs']=exprdata
	
	
#bin op left right
def binExc(stmtdata,op,left,right)
	stmtdata['object']="instruction"
    stmtdata['filename']=left.position().path
    stmtdata['line_number']=left.position().lineno	
	stmtdata['name']="bin"
	stmtdata['op']=op
	leftdata={}
	exprExc(leftdata,left)
	stmtdata['left']=leftdata
	rightdata={}
	exprExc(rightdata,right)
	stmtdata['right']=rightdata


def cjumpExc(cjumpdata,exprNode,thenlabelname,elselabelname)
	cjumpdata['object']="instruction"
    cjumpdata['filename']=exprNode.position().path
    cjumpdata['line_number']=exprNode.position().lineno	
	cjumpdata['name']="cjump"
	exprdata={}
	exprExc(exprdata,exprNode)
	cjumpdata['cond']=exprdata
	cjumpdata['thenLabel']=thenlabelname
	cjumpdata['elseLabel']=elselabelname

def labelstmtExc(labelstmtdata,stmtNode,labelname)
	labelstmtdata['object']="instruction"
    labelstmtdata['filename']=stmtNode.position().path
    labelstmtdata['line_number']=stmtNode.position().lineno	
	labelstmtdata['name']="labelstmt"
	labelstmtdata['label']=labelname

def jumpExc(jumpstmt,stmtNode,labelname)
	jumpstmt['object']="instruction"
    jumpstmt['filename']=stmtNode.position().path
    jumpstmt['line_number']=stmtNode.position().lineno
	jumpstmt['name']="jump"
	jumpstmt['label']=labelname




















