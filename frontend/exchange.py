# -*- coding: utf-8 -*-

from ply import yacc

from frontend import log
from frontend.ast import *
from frontend.explain import *


#program definition
def programExc(programdata,name,filename,line_number,varlist,funclist,labellist,body)
	programdata['object'] = "program_definition"
	programdata['name'] = name
	programdata['fiename'] = filename
    programdata['line_number'] = line_number
	programdata['variablelist'] = varlist
	programdata['functionlist'] = funclist
	programdata['labellist'] = labellist
	programdata['body'] = body




#function definition
def functionExc(funcdata,name,filename,line_number,functype,paralist,varlist,labellist,body)
	funcdata['object'] = "function_definition"
	funcdata['name'] = name
	funcdata['filename'] = filename
    funcdata['line_number'] = line_number
	funcdata['type'] = functype
	funcdata['parameterlsit'] = paralist
	funcdata['variablelsit'] = varlist
	funcdata['labellist'] = labellist
	funcdata['body'] = body


#label
def labelExc(labeldata,name,pos)
	labeldata['object'] = label
	labeldata['name'] = name
	labeldata['pos'] = pos


#variable
def variableExc(vardata,varname,vartype,const)
	vardata['object'] = "entity"
	vardata['type'] = vartype
	vardata['name'] = "variable"
	vardata['variable'] = varname
	vardata['const'] = const



#value
def valueExc(valdata,valtype,value)
	valdata['entity'] = "entity"
	valdata['type'] = valtype
	valdata['name'] = "value"
	valdata['value'] = value


#variable_definition const=false
def vardefExc(vardefdata,filename,line_number,variablename,var_type)
	vardefdata['object'] = "instruction"
	vardefdata['name'] = "variable_definition"
	vardefdata['filename'] = filename
    vardefdata['line_number'] = line_number
	vardefdata['variablename'] = variablename
	vardefdata['var_type'] = var_type
	vardefdata['const'] = false


##variable_definition const=true
def constdefExc(vardefdata,filename,Line_number,variablename,var_type,entitydata)
	vardefdata['object'] = "instruction"
	vardefdata['name'] = "variable_definition"
	vardefdata['filename'] = filename
    vardefdata['line_number'] = Line_number
	vardefdata['variablename'] = variablename
	vardefdata['var_type'] = var_type
	vardefdata['const'] = true
	vardefdata['value'] = entitydata



#label_definition
def labeldefExc(labeldefdata,filename,line_number,labelname)
	labeldefdata['object'] = "instruction"
	labeldefdata['name'] = "label_definition"
	labeldefdata['filename'] = filename
    labeldefdata['line_number'] = line_number
	labeldefdata['labelname'] = labelname


#load
def loadExc(loaddata,filename,line_number,address,value)
	loaddata['object'] = "instruction"
	loaddata['name'] = "load"
	loaddata['filename'] = filename
    loaddata['line_number'] = line_number
	loaddata['address'] = address
	loaddata['value'] = value


#store
def storeExc(storedata,filename,line_number,address,value)
	storedata['object'] = "instruction"
	storedata['name'] = "store"
	storedata['filename'] = filename
	storedata['line_number'] = line_number
	storedata['address'] = address
	storedata['value'] = value


#cjump
def cjumpExc(cjumpdata,filename,line_number,cond,thenlabel,elselabel)
	cjumpdata['object'] = "instruction"
	cjumpdata['filename'] = filename
	cjumpdata['line_number'] = line_number
	cjumpdata['cond'] = cond
	cjumpdata['thenlabel'] = thenlabel
	cjumpdata['elselabel'] = elselabel


#jump
def jumpExc(jumpdata,filename,line_number,label)
	jumpdata['object'] = "instruction"
	jumpdata['filename'] = filename
	jumpdata['line_number'] = line_number
	jumpdata['label'] = label



#call
def callExc(calldata,filename,line_number,functionname,paramaterlist,value)
	calldata['object'] = "instruction"
	calldata['fliename'] = filename
	calldata['line_number'] = line_number
	calldata['functionname'] = functionname
	calldata['paramaterlist'] = paramaterlist
	calldata['value'] = value


#return
def retExc(retdata,filename,line_number,ret)
	retdata['object'] = "instruction"
	retdata['filename'] = filename
	retdata['line_number'] = line_number
	retdata['ret'] = ret



#bin
def binExc(bindata,filename,line_number,op,left,right,value)
	bindata['object'] = "instruction"
	bindata['filename'] = filename
	bindata['line_number'] = line_number
	bindata['op'] = op
	bindata['left'] = left
	bindata['right'] = right
	bindata['value'] = value


#uni
def uniExc(unidata,filename,line_number,op,variable,value)
	unidata['object'] = "instruction"
	unidata['filename'] = filename
	unidata['line_number'] = line_number
	unidata['op'] = op
	unidata['variable'] = variable
	unidata['value'] = value




















