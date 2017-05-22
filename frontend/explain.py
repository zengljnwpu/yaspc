# -*- coding: utf-8 -*-
import json

from ply import yacc

from frontend import log
from frontend.ast import *
from frontend.exchange import *


class explain:

	varno = 0;
	labelno = 0;

	#store the final data dictionary
	def store(data):
		with open('data.json', 'w') as json_file:
		    json_file.write(json.dumps(data))


	#programNode is given by user
	def programEplain(programNode):
		name = programNode.identifier
		filename = programNode.position().path
		line_number = programNode.position().lineno
		varlist = []
		body = []
		users_var_defExplain(varlist,body,programNode.block.var_list,programNode.block.const_list)
		funclist = []
		funclistExplain(funclist,programNode.block.func)
		labellist = []
		stmtlistExplain(varlist,labellist,body,programNode.block.stmt)
		programdata = {}
		programExc(programdata,name,filename,line_number,varlist,funclist,labellist,body)
		store(programdata)


	def users_var_defExplain(varlist,body,varlistNode,constlistNode)
		for i in range(len(varlistNode))
			vardefExplain(varlist,body,varlistNode[i])
		for i in range(len(constlistNode))
			constdefExplain(varlist,body,constlistNode[i])


	def vardefExplain(varlist,body,vardeclNode)
		vartype = vardeclNode.type_denoter
		fliename = vardeclNode.position().path
		line_namber = vardeclNode.position().lineno
		for i in range(len(vardeclNode.identifier_list))
			vardefdata = {}
			vardata = {}
			variablename = vardeclNode.identifier_list[i]
			vardefExc(vardefdata,filename,line_number,variablename,vartype)
			variableExc(vardata,variablename,vartype,false)
			body.append(vardefdata)
			varlist.append(vardata)



	def constdefExplain(varlist,body,constdeclNode)
		value = {}
		exprExplain(varlist,body,constdeclNode.expr,value)
		vartype = constdeclNode.type()
		fliename = constdeclNode.position().path
		line_namber = constdeclNode.position().lineno
		constdefdata = {}
		vardata = {}
		constname = constdeclNode.identifier
		constdefExc(constdefdata,filename,Line_number,constname,vartype,value)
		variableExc(vardata,constname,vartype,ture)
		body.append(vardefdata)
		varlist.append(vardata)



	def funclistExplain(funclist,funclistNode)
		for i in range(len(funclistNode))
			funcdata = {}
			funcExplain(funcdata,funclistNode[i])
			funclist.append(funcdata)



	def funcExplain(funcdata,funcNode)
		name = funcNode.header.identifer
		filename = funcNode.position().path
		line_number = funcNode.position().lineno
		functype = funcNode.haeder.return_type
		paralist = []
		paralistExplain(paralist,funcNode.haeder.param_list)
		varlist = []
		body = []
		users_var_defExplain(varlist,body,funcNode.block.var_list,funcNode.block.const_list)
		labellist = []
		stmtlistExplain(varlist,labellist,body,funcNode.block.stmt)
		functionExc(funcdata,name,filename,line_number,functype,paralist,varlist,labellist,body)



	def paralistExplain(paralist,paramlistNode)
		for i in range(len(paramlistNode))
			paradata = {}
			paraExplain(paradata,paramlistNode[i])
			paralist.append(paradata)


	def paraExplain(paradata,paraNode)
		if isinstence(paraNode,ValueParameterNode)
			ValueParaExplain(paradata,paraNode)
		else
			refparaExplain(paradata,paraNode)


	def ValueParaExplain(paradata,varname,paraNode)
		for i in range(len(paraNode.identifier_list))
			tempdata = {}
			varname = paraNode.identifier_list[i]
			vartype = paraNode.type_denoter
			variableExc(tempdata,varname,vartype,false)


	def refparaExplain(paradata,varname,paraNode)
		ValueParaExplain(paradata,paraNode)



	def exprExplain(varlist,body,exprNode,value)
		if isinstence(exprNode,BinaryOpNode)
			binExplain(varlist,body,exprNode,value)
		elif isinstence(exprNode,UnaryOpNode)
			uniExplain(varlist,body,exprNode,value)
		elif isinstence(exprNode,VarAccessNode)
			varExplain(value,exprNode)
		else
			valueExplain(value,exprNode)


	def binExplain(varlist,body,binNode,value)
		filename = binNode.position().path
		line_number = binNode.position().lineno
		op = binNode.op
		leftentity = {}
		exprExplain(varlist,body,binNode.expr,leftentity)
		rightentity = {}
		exprExplain(varlist,body,binNode.expr,rightentity)
		varname = "%"+varno
		varno = varno+1
		vartype = binNode.type()
		variableExc(value,varname,vartype,false)
		varlist.expend(value)
		bindata = {}
		binExc(bindata,filename,line_number,op,leftentity,rightentity,value)
		body.expend(bindata)



	def uniExplain(varlist,body,unaNode,value)
		filename = unaNode.position().path
		line_number = unaNode.position().lineno
		op = unaNode.name
		entity = {}
		exprExplain(varlist,body,unaNode.expr,entity)
		varname = "%"+varno
		varno = varno+1
		vartype = uniNode.type()
		variableExc(value,varname,vartype,false)
		varlist.expend(value)
		unadata = {}
		unaExc(unidata,filename,line_number,op,variable,entity)
		body.expend(unadata)



	def varExplain(value,varaccessNode)
		varname = varaccessNode.identifier
		vartype = varaccessNode.type()
		variable(value,varname,vartype,false)


	def valueExplain(valuedata,valueNode)
		valtype = valueNode.type()
		value = valueNode.value
		valueExc(valuedata,valtype,value)


	def stmtlistExplain(varlist,labellist,body,stmtlistNode)
		for i in range(len(stmtlistNode))
			stmtExplain(varlist,labellist,body,stmtlistNode[i])


	def stmtExplain(varlist,labellist,body,stmtNode):
		if isinstance(stmtNode,AssignmentNode):
			asignExplain(varlist,labellist,body,stmtNode)
		elif isinstance(stmtNode, IfNode):
			ifExplain(varlist,labellist,body,stmtNode)
		elif isinstance(stmtNode, ForNode):
			forExplain(varlist,labellist,body,stmtNode)


	def asignExplain(varlist,labellist,body,asignNode)
		filename = asignNode.position().path
		line_number = asignNode.poosition().lineno
		address = {}
		varExplain(value,asignNode.var_access)
		value = {}
		exprExplain(varlist,body,asignNode.expr,value)
		storedata = {}
		storeExc(storedata,filename,line_number,address,value)
		body.expend(storedata)


	def ifExplain(varlist,labellist,body,ifNode)
		thenlabelname="ifthenlabel_"+labelno
		elselabelname="ifelselabel_"+labelno
		endlabelname="ifendlabel_"+labelno
		labelno=labelno+1
		cjumpExplain(varlist,body,ifNode.expr,thenlabelname,elselabelname)
		labeldefExplain(labellist,body,filename,line_number,thenlabelname)
		stmtlistExplain(varlist,labellist,body,ifNode.iftrue)
		filename = ifNode.position().path
		line_number = ifNode.position().lineno
		jumpdata={}
		jumpExc(jumpdata,filename,line_number,endlabelname)
		body.expend(jumpdata)
		labeldefExplain(labellist,body,filename,line_number,elselabelname)
		stmtlistExplain(varlist,labellist,body,ifNode.iffalse)
		labeldefExplain(labellist,body,filename,line_number,endlabelname)
		


	def labeldefExplain(labellist,body,filename,line_number,labelname)
		labelpos = len(body)
		label = {}
		labelExc(label,labelname,labelpos)
		labellist,expend(label)
		labeldefdata = {}
		labeldefExc(labeldefdata,filename,line_number,labelname)
		body.expend(labeldefdata)
		
		
	def cjumpExplain(varlist,body,exprNode,thenlabelname,elselabelname)
		condvalue = {}
		exprExplain(varlist,body,expr,condvalue)
		filename = exprNode.position().path
		line_number = exprNode.position().lineno
		cjumpdata = {}
		cjumpExc(cjumpdata,filename,line_number,condvalue,thenlabelname,elselabelname)
		body.expend(cjumpdata)
		

		
	def forExplain(varlist,labellist,body,forNode)
		startlabelname="forstartlabel_"+labelno
		thenlabelname="forthenlabel_"+labelno
		elselabelname="forelselabel_"+labelno
		labelno = labelno + 1
		filename = forNode.position().path
		line_number = forNode.position().lineno
		asignNode1 = AssignmentNode(forNode.var,forNode.value_start)
		asignExplain(varlist,labellist,body,asignNode1)
		labeldefExplain(labellist,body,filename,line_number,startlabelname)
		if forNode.direction==1
			exprNode=BinaryOpNode(forNode.var,"S_LTEQ",forNode.end_val)
		else
			exprNode=BinaryOpNode(forNode.var,"S_GTEQ",forNode.end_val)
		cjumpExplain(varlist,body,exprNode,thenlabelname,elselabelname)
		labeldefExplain(labellist,body,filename,line_number,thenlabelname)
		stmtlistExplain(varlist,labellist,body,forNode.body)
		varppNode=BinaryOpNode(forNode.var,"ADD",IntegerNode(1))
		asignNode2 = AssignmentNode(forNode.var,varppNode)
		asignExplain(varlist,labellist,body,asignNode2)
		jumpdata={}
		jumpExc(jumpdata,filename,line_number,endlabelname)
		body.append(jumpdata)
		labeldefExplain(labellist,body,filename,line_number,elselabelname)
		









