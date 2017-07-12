# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, with_statement

from ast import * #@UnusedWildImport

'''
这个.py文件是用来描述IR的。
每一个function表示了一种IR结构。
它们之间通过嵌套关系组成一个多重字典。
具体IR设计请看IR.md
'''
#program definition
def programExc(programdata,name,line_number,varlist,funclist,labellist,body):
    programdata['object'] = "program_definition"
    programdata['name'] = str(name)
    programdata['line_number'] = int(line_number)
    programdata['variablelist'] = varlist #此list中包含所有用户在最外层定义的变量的指针定义，可供全局使用
    programdata['functionlist'] = funclist #此list中包括function和procedure
    programdata['labellist'] = labellist #此list中的label仅供该program的程序主体部分使用 
    programdata['body'] = body




#function definition
def functionExc(funcdata,name,line_number,functype,paralist,varlist,labellist,body):
    funcdata['object'] = "function_definition"
    funcdata['name'] = str(name)
    funcdata['line_number'] = int(line_number)
    funcdata['type'] = str(functype) #函数的类型为返回值类型
    funcdata['parameterlsit'] = paralist #分为普通变量和引用变量，引用变量通过指针表示
    funcdata['variablelist'] = varlist #此list中包含所有用户在function中定义的变量的指针定义，可供function内使用
    funcdata['labellist'] = labellist   #此list中的label仅供该function的程序主体部分使用
    funcdata['body'] = body


#function definition
def procedureExc(procdata,name,line_number,paralist,varlist,labellist,body):
    procdata['object'] = "procedure_definition"
    procdata['name'] = str(name)
    procdata['line_number'] = int(line_number)
    procdata['type'] = "void" #过程的类型为空类型
    procdata['parameterlsit'] = paralist #分为普通变量和引用变量，引用变量通过指针表示
    procdata['variablelist'] = varlist #此list中包含所有用户在procedure中定义的变量的指针定义，可供procedure内使用
    procdata['labellist'] = labellist #此list中的label仅供该procedure的程序主体部分使用
    procdata['body'] = body


#label
def labelExc(labeldata,name,pos): #本模块仅用于labellist，起到label的符号表的作用。
    labeldata['object'] = "label"
    labeldata['name'] = str(name)
    labeldata['pos'] = int(pos) #pos为该label对应的指令号（在第几条指令定义该label）


#variable
def variableExc(vardata,varname,vartype,const):
    vardata['object'] = "variable"
    vardata['type'] = str(vartype) #变量类型分为普通类型和指针类型，指针类型为普通类型后加*
    vardata['name'] = str(varname)
    vardata['const'] = bool(const)
    vardata['is_private'] = bool(0)



#value
def valueExc(valdata,valtype,value):
    valdata['object'] = "value"
    valdata['type'] = str(valtype) #值类型分为普通类型和指针类型，指针类型为普通类型后加*
    valdata['value'] = value


#variable_definition const=False
def vardefExc(vardefdata,line_number,variablename,var_type,number):
    vardefdata['object'] = "instruction"
    vardefdata['name'] = "variable_definition"
    vardefdata['line_number'] = int(line_number)
    vardefdata['variablename'] = str(variablename)
    vardefdata['var_type'] = str(var_type)
    vardefdata['number'] = int(number) #为数组预留，考虑到数组需要连续的空间，此定义理论上应支持长度的概念
    vardefdata['const'] = False
    vardefdata['initvalue'] = 0 #初值不一定需要，但必须有，默认为0，若不需要，则无意义。
    vardefdata['is_private'] = bool(0) #目前一直为0，不考虑private变量

##variable_definition const=True
def constdefExc(vardefdata,Line_number,variablename,var_type,initvalue):
    vardefdata['object'] = "instruction"
    vardefdata['name'] = "variable_definition"
    vardefdata['line_number'] = int(Line_number)
    vardefdata['variablename'] = str(variablename)
    vardefdata['var_type'] = str(var_type)
    vardefdata['const'] = True
    vardefdata['initvalue'] = initvalue #const必定有初值，需要在IR生成前得到
    vardefdata['is_private'] = bool(0) #目前一直为0，不考虑private变量



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
    loaddata['address'] = address #此load模块的address本身为地址，因此，需将其值当做地址使用，而非给address赋值
    loaddata['value'] = value
    loaddata['name'] = "load"


#store
def storeExc(storedata,line_number,address,value):
    storedata['object'] = "instruction"
    storedata['name'] = "store"
    storedata['line_number'] = int(line_number)
    storedata['address'] = address #此store模块的address本身为地址，因此，需将其值当做地址使用，而非给address赋值
    storedata['value'] = value
    storedata['name'] = "store"


#cjump
def cjumpExc(cjumpdata,line_number,cond,thenlabel,elselabel):
    cjumpdata['object'] = "instruction"
    cjumpdata['line_number'] = int(line_number)
    cjumpdata['cond'] = cond #此cond应为一个临时变量，或值
    cjumpdata['thenlabel'] = str(thenlabel)
    cjumpdata['elselabel'] = str(elselabel)
    cjumpdata['name'] = "cjump"


#jump
def jumpExc(jumpdata,line_number,label):
    jumpdata['object'] = "instruction"
    jumpdata['line_number'] = int(line_number)
    jumpdata['label'] = str(label)
    jumpdata['name'] = "jump"



#call
def callExc(calldata,line_number,functionname,parameterlist,value):
    calldata['object'] = "instruction"
    calldata['line_number'] = line_number
    calldata['functionname'] = functionname #此处为函数或过程名，可通过查表调用
    calldata['parameterlist'] = parameterlist
    calldata['value'] = value #返回值为一临时变量或值
    calldata['name'] = "call"


#return
def retExc(retdata,line_number,ret):
    retdata['object'] = "instruction"
    retdata['line_number'] = line_number
    retdata['ret'] = ret #此ret为一临时变量或值
    retdata['name'] = "return"



#bin
def binExc(bindata,line_number,op,left,right,value):
    bindata['object'] = "instruction"
    bindata['line_number'] = line_number
    bindata['op'] = op
    bindata['left'] = left
    bindata['right'] = right
    bindata['value'] = value #此ret为一临时变量或值
    bindata['name'] = "bin"


#uni
def uniExc(unadata,line_number,op,variable,value):
    unadata['object'] = "instruction"
    unadata['line_number'] = line_number
    unadata['op'] = op
    unadata['variable'] = variable
    unadata['value'] = value #此ret为一临时变量或值
    unadata['name'] = "una"



















