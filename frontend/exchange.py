# -*- coding: utf-8 -*-

from ply import yacc

from ast import *


#program definition
def programExc(programdata,name,line_number,varlist,funclist,labellist,body):
    programdata['object'] = "program_definition"
    programdata['name'] = str(name)
    programdata['line_number'] = int(line_number)
    programdata['variablelist'] = varlist
    programdata['functionlist'] = funclist
    programdata['labellist'] = labellist
    programdata['body'] = body




#function definition
def functionExc(funcdata,name,line_number,functype,paralist,varlist,labellist,body):
    funcdata['object'] = "function_definition"
    funcdata['name'] = str(name)
    funcdata['line_number'] = int(line_number)
    funcdata['type'] = str(functype)
    funcdata['parameterlsit'] = paralist
    funcdata['variablelsit'] = varlist
    funcdata['labellist'] = labellist
    funcdata['body'] = body


#label
def labelExc(labeldata,name,pos):
    labeldata['object'] = str(label)
    labeldata['name'] = str(name)
    labeldata['pos'] = int(pos)


#variable
def variableExc(vardata,varname,vartype,const):
    vardata['object'] = "entity"
    vardata['type'] = str(vartype)
    vardata['name'] = "variable"
    vardata['variable'] = str(varname)
    vardata['const'] = bool(const)



#value
def valueExc(valdata,valtype,value):
    valdata['entity'] = "entity"
    valdata['type'] = str(valtype)
    valdata['name'] = "value"
    valdata['value'] = int(value)


#variable_definition const=False
def vardefExc(vardefdata,line_number,variablename,var_type):
    vardefdata['object'] = "instruction"
    vardefdata['name'] = "variable_definition"
    vardefdata['line_number'] = int(line_number)
    vardefdata['variablename'] = str(variablename)
    vardefdata['var_type'] = str(var_type)
    vardefdata['const'] = False


##variable_definition const=True
def constdefExc(vardefdata,Line_number,variablename,var_type,entitydata):
    vardefdata['object'] = "instruction"
    vardefdata['name'] = "variable_definition"
    vardefdata['line_number'] = int(Line_number)
    vardefdata['variablename'] = str(variablename)
    vardefdata['var_type'] = str(var_type)
    vardefdata['const'] = True
    vardefdata['value'] = entitydata



#label_definition
def labeldefExc(labeldefdata,line_number,labelname):
    labeldefdata['object'] = "instruction"
    labeldefdata['name'] = "label_definition"
    labeldefdata['line_number'] = int(line_number)
    labeldefdata['labelname'] = str(labelname)


#load
def loadExc(loaddata,line_number,address,value):
    loaddata['object'] = "instruction"
    loaddata['name'] = "load"
    loaddata['line_number'] = int(line_number)
    loaddata['address'] = address
    loaddata['value'] = value


#store
def storeExc(storedata,line_number,address,value):
    storedata['object'] = "instruction"
    storedata['name'] = "store"
    storedata['line_number'] = int(line_number)
    storedata['address'] = address
    storedata['value'] = value


#cjump
def cjumpExc(cjumpdata,line_number,cond,thenlabel,elselabel):
    cjumpdata['object'] = "instruction"
    cjumpdata['line_number'] = int(line_number)
    cjumpdata['cond'] = cond
    cjumpdata['thenlabel'] = str(thenlabel)
    cjumpdata['elselabel'] = str(elselabel)


#jump
def jumpExc(jumpdata,line_number,label):
    jumpdata['object'] = "instruction"
    jumpdata['line_number'] = int(line_number)
    jumpdata['label'] = str(label)



#call
def callExc(calldata,line_number,functionname,paramaterlist,value):
    calldata['object'] = "instruction"
    calldata['line_number'] = line_number
    calldata['functionname'] = functionname
    calldata['paramaterlist'] = paramaterlist
    calldata['value'] = value


#return
def retExc(retdata,line_number,ret):
    retdata['object'] = "instruction"
    retdata['line_number'] = line_number
    retdata['ret'] = ret



#bin
def binExc(bindata,line_number,op,left,right,value):
    bindata['object'] = "instruction"
    bindata['line_number'] = line_number
    bindata['op'] = op
    bindata['left'] = left
    bindata['right'] = right
    bindata['value'] = value


#uni
def uniExc(unidata,line_number,op,variable,value):
    unidata['object'] = "instruction"
    unidata['line_number'] = line_number
    unidata['op'] = op
    unidata['variable'] = variable
    unidata['value'] = value




















