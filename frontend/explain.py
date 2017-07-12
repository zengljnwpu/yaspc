# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json

from frontend.ast import * #@UnusedWildImport
from frontend.exchange import * #@UnusedWildImport
from frontend.compiler import * #@UnusedWildImport
from frontend.typesys import * #@UnusedWildImport
from frontend.symtab import * #@UnusedWildImport
from frontend.codegen import * #@UnusedWildImport
'''
此py文件主要将语法树进行进一步解析，生成IR。
主要包括了语法树各个节点的解释。
每个解释函数的基本思路均为通过已知Node找出各个需求的指令的信息，并生成指令字典。
'''

class explain(object):
    varno = 0 #用于对临时变量进行命名
    labelno = 0 #用于对临时label进行命名
    programdata = {} #最终字典
    ctx = [] #符号表

    #store the final data dictionary
    def store(self,json_path):
        with open(json_path, 'w') as json_file:
            json_file.write(json.dumps(self.programdata, sort_keys=True, indent=4))


    #programNode is given by user
    def programExplain(self,programNode):
        if programNode != None:
            v = codegen.CodegenVisitor()
            self.ctx = v.ctx #得到符号表
            name = str(programNode.identifier.name)
            line_number = int(programNode.position.lineno)
            varlist = []
            self.users_var_defExplain(varlist,programNode.block.var_list)
            self.users_con_defExplain(varlist,programNode.block.const_list)
            funclist = []
            self.funclistExplain(funclist,programNode.block.func)
            labellist = []
            body = []
            self.stmtlistExplain(labellist,body,programNode.block.stmt,name)
            programExc(self.programdata,name,line_number,varlist,funclist,labellist,body)


    def users_var_defExplain(self,varlist,varlistNode):#根据varlistNode得到varlist
        if varlistNode != None:
            for i in range(len(varlistNode._children)):
                self.vardefExplain(varlist,varlistNode._children[i])


    def users_con_defExplain(self,varlist,constlistNode):#根据constlistNode得到varlist
        if constlistNode != None:
            for i in range(len(constlistNode._children)):
                self.constdefExplain(varlist,constlistNode._children[i])



    def vardefExplain(self,varlist,vardeclNode):
        if vardeclNode != None:
            if isinstance(vardeclNode.type_denoter,ArrayTypeNode): #若为数组类型，则单独处理，目前数组类型尚存在问题
                arraydefExplain(varlist,vardeclNode.type_denoter)
            else: #若非数组类型
                line_number = int(vardeclNode.position.lineno)
                vartype = str(vardeclNode.type_denoter.identifier.name)+"*" 
                #用户定义的变量类型均为指针，以达到可读可写的标准。
                for i in range(len(vardeclNode.identifier_list._children)): #每个vardeclNode中有很多id
                    vardefdata = {}
                    variablename = str(vardeclNode.identifier_list._children[i].name)
                    vardefExc(vardefdata,line_number,variablename,vartype,1)
                    varlist.append(vardefdata)




    def constdefExplain(self,varlist,constdeclNode):
        if constdeclNode != None:
            value = con_exprExplain(constdeclNode.expr)
            vartype = str(self.typeExplain(constdeclNode.type))+"*"
            #用户定义的变量类型均为指针，以达到可读可写的标准。
            line_number = int(constdeclNode.position.lineno)
            constdefdata = {}
            constname = str(constdeclNode.identifier.name)
            constdefExc(constdefdata,line_number,constname,vartype,value)
            varlist.append(constdefdata)




    def arraydefExplain(self,varlist,arraydeclNode):#目前闲置
        if arraydeclNode != None:
            line_number = int(arraydeclNode.position.lineno)
            vartype = str(arraydeclNode.type_denoter.component_type.identifier.name)+"*"
            for i in range(len(arraydeclNode.identifier_list._children)):
                vardefdata = {}
                variablename = str(arraydeclNode.identifier_list._children[i].name)
                number = 1
                for j in range(len(arraydeclNode.type_denoter.index_list._children)):
                    start = arraydeclNode.type_denoter.index_list._children[j].start.value
                    stop = arraydeclNode.type_denoter.index_list._children[j].stop.value
                    if stop > start:
                        number = number*(stop-start+1)
                    else:
                        number = number*(start-stop+1)
                vardefExc(vardefdata,line_number,variablename,vartype,number)
                varlist.append(vardefdata)




    def funclistExplain(self,funclist,funclistNode):
        if funclistNode != None:
            for i in range(len(funclistNode._children)):
                if isinstance(funclistNode._children[i],FunctionNode):
                    self.funcExplain(funclist,funclistNode._children[i])
                else:
                    self.procExplain(funclist,funclistNode._children[i])




    def funcExplain(self,funclist,funcNode):
        if funcNode != None:
            funcdata = {}
            name = str(funcNode.header.identifier.name)
            line_number = int(funcNode.position.lineno)
            functype = str(self.typeExplain(funcNode.header.return_type))
            paralist = []
            self.paralistExplain(paralist,funcNode.header.param_list)
            varlist = []
            self.users_var_defExplain(varlist,funcNode.block.var_list)
            self.users_con_defExplain(varlist,funcNode.block.const_list)
            labellist = []
            body = []
            self.stmtlistExplain(labellist,body,funcNode.block.stmt,name)
            functionExc(funcdata,name,line_number,functype,paralist,varlist,labellist,body)
            funclist.append(funcdata)



    def procExplain(self,proclist,procNode):
        if procNode != None:
            procdata = {}
            name = str(procNode.header.identifier.name)
            line_number = int(procNode.position.lineno)
            paralist = []
            self.paralistExplain(paralist,procNode.header.param_list)
            varlist = []
            self.users_var_defExplain(varlist,procNode.block.var_list)
            self.users_con_defExplain(varlist,procNode.block.const_list)
            labellist = []
            body = []
            self.stmtlistExplain(labellist,body,procNode.block.stmt,name)
            procedureExc(procdata,name,line_number,paralist,varlist,labellist,body)
            proclist.append(procdata)    



    def paralistExplain(self,paralist,paramlistNode):
        if paramlistNode != None:
            for i in range(len(paramlistNode._children)):
                self.paraExplain(paralist,paramlistNode._children[i])


    def paraExplain(self,paralist,paraNode):
        if paraNode != None:
            if isinstance(paraNode,ValueParameterNode):
                self.ValueParaExplain(paralist,paraNode)
            else:
                self.refparaExplain(paralist,paraNode)


    def ValueParaExplain(self,paralist,paraNode):
        if paraNode != None:
            for i in range(len(paraNode.identifier_list._children)):
                tempdata = {}
                varname = str(paraNode.identifier_list._children[i].name)
                vartype = str(self.typeExplain(paraNode.type))
                variableExc(tempdata,varname,vartype,False)
                paralist.append(tempdata)


    def refparaExplain(self,paralist,paraNode):
        if paraNode != None:
            for i in range(len(paraNode.identifier_list._children)):
                tempdata = {}
                varname = str(paraNode.identifier_list._children[i].name)
                vartype = str(self.typeExplain(paraNode.type))+"*"
                variableExc(tempdata,varname,vartype,False)
                paralist.append(tempdata)






    def exprExplain(self,body,exprNode,value): #对表达式节点进行区分
        if exprNode != None:
            if isinstance(exprNode,BinaryOpNode):#二元
                self.binExplain(body,exprNode,value)
            elif isinstance(exprNode,UnaryOpNode):#一元
                self.unaExplain(body,exprNode,value)
            elif isinstance(exprNode,FunctionCallNode):#函数调用
                self.funccallExplain(body,exprNode,value)
            elif isinstance(exprNode,VarAccessNode):#变量
                self.varExplain(body,exprNode,value)
            elif isinstance(exprNode,VarLoadNode):#varload也是变量，结构多了一层
                if isinstance(exprNode.var_access,IndexedVarNode):
                    self.arrayExplain(body,exprNode,value)
                else:
                    self.varExplain(body,exprNode.var_access,value)
            elif isinstance(exprNode,IdentifierNode):#id
                self.idExplain(body,exprNode,value)
            elif isinstance(exprNode,TypeConvertNode):
                self.typeconvertExplain(body,exprNode,value)
            else:#值
                self.valueExplain(value,exprNode)


    def funccallExplain(self,body,funccallNode,value):
        if funccallNode != None:
            self.newvarExplain(value,str(self.typeExplain(funccallNode.type)))
            calldata = {}
            line_number = int(funccallNode.position.lineno)
            functionname = str(funccallNode.identifier.name)
            parameterlist = []
            self.argulistExplain(parameterlist,body,funccallNode.arg_list)
            callExc(calldata,line_number,functionname,parameterlist,value)
            body.append(calldata)


    def argulistExplain(self,parameterlist,body,argulistNode):#获取参数列表到parameterlist
        if argulistNode != None:
            for i in range(len(argulistNode._children)):
                value = {}
                self.exprExplain(body,argulistNode._children[i].expr,value)
                parameterlist.append(value)




    def binExplain(self,body,binNode,value):
        if binNode != None:
            line_number = int(binNode.position.lineno)
            leftentity = {}
            self.exprExplain(body,binNode.left,leftentity)
            op = opExplain(binNode.op.name,1,0)
            rightentity = {}
            self.exprExplain(body,binNode.right,rightentity)
            self.newvarExplain(value,str(self.typeExplain(binNode.type)))#生成新的临时变量
            bindata = {}
            binExc(bindata,line_number,op,leftentity,rightentity,value)
            body.append(bindata)



    def uniExplain(self,varlist,body,uniNode,value):
        if uniNode != None:
            line_number = str(uniNode.position.lineno)
            op = str(uniNode.name)
            entity = {}
            self.exprExplain(varlist,body,uniNode.expr,entity)
            self.newvarExplain(value,str(self.typeExplain(uniNode.type)))#生成新的临时变量
            varlist.append(value)
            unidata = {}
            uniExc(unidata,line_number,op, value,entity)
            body.append(unidata)



    def varExplain(self,body,varaccessNode,value):
        if varaccessNode != None:
            line_number = int(varaccessNode.position.lineno)
            addrname = str(varaccessNode.identifier.name)
            addrtype = str(self.typeExplain(varaccessNode.type))+"*"
            address = {}
            variableExc(address,addrname,addrtype,False)
            self.newvarExplain(value,str(self.typeExplain(varaccessNode.type)))
            loaddata = {}
            loadExc(loaddata,line_number,address,value)
            body.append(loaddata)
            


    def idExplain(self,body,idNode,value):
        if idNode != None:
            line_number = int(idNode.position.lineno)
            addrname = str(idNode.name)
            vartype = self.ctx.find_typedef(idNode.name)
            addrtype = str(self.typeExplain(vartype))+"*"
            addr = {}
            variableExc(addr,addrname,addrtype,False)
            self.newvarExplain(value,str(self.typeExplain(vartype)))
            loaddata = {}
            loadExc(loaddata,line_number,addr,value)
            body.append(loaddata)



    def typeconvertExplain(self,body,typeconvertNode,value):
        if typeconvertNode != None:
            line_number = int(typeconvertNode.position.lineno)
            valuetype = self.typeExplain(typeconvertNode.type)
            variable = {}
            self.exprExplain(body,typeconvertNode.child,variable)
            self.newuniExplain(body,line_number,"S_CAST",variable,value)



    def valueExplain(self,valuedata,valueNode):
        if valueNode != None:
            valtype = str(self.typeExplain(valueNode.type))
            value = valueNode.value
            valueExc(valuedata,valtype,value)
   


    def arrayExplain(self,body,arrayNode,value):#目前闲置
        valtype = str(self.typeExplain(arrayNode.var_access.var_access.type))+"*"
        line_number = int(arrayNode.position.lineno)
        left = {}
        self.exprExplain(body,arrayNode.var_access.index_expr_list._children[0],left)
        right = {}
        start = arrayNode.type.index_list._children[0].start.value
        stop = arrayNode.type.index_list._children[0].stop.value
        if start > stop:
            valueExc(right,valtype,stop)
        else:
            valueExc(right,valtype,start)
        midaddr = {}
        self.newvarExplain(midaddr,valtype)
        self.newbinExplain(line_number,"SUB",left,right,midaddr)
        for i in range(1,len(arrayNode.var_access.index_expr_list._children)):
            left = midaddr
            right = {}
            start = arrayNode.var_access.type.index_list._children[i].start.value
            stop = arrayNode.var_access.type.index_list._children[i].stop.value
            if start > stop:
                valueExc(right,valtype,start-stop+1)
            else:
                valueExc(right,valtype,stop-start+1)
            midaddr = {}
            self.newvarExplain(midaddr,valtype)
            self.newbinExplain(line_number,"MUL",left,right,midaddr)
            left2 = midaddr
            left = {}
            self.exprExplain(body,arrayNode.var_access.index_expr_list._children[i],midaddr)
            right = {}
            if start > stop:
                valueExc(right,valtype,stop)
            else:
                valueExc(right,valtype,start)
            midaddr = {}
            self.newvarExplain(midaddr,valtype)
            self.newbinExplain(line_number,"SUB",left,right,midaddr)
            right2 = midaddr
            midaddr = {}
            self.newvarExplain(midaddr,valtype)
            self.newbinExplain(line_number,"ADD",left2,right2,midaddr)
        left = midaddr
        right2 = {}
        variableExc(right2,arrayNode.var_access.var_access.identifier.name,valtype,False)
        op2 = "ADD"
        self.newvarExplain(value,valtype)
        bindata = {}
        binExc(bindata,line_number,op2,left,right2,value)
        body.append(bindata)




    def stmtlistExplain(self,labellist,body,stmtlistNode,functionname):
        if stmtlistNode != None:
            for i in range(len(stmtlistNode._children)):
                self.stmtExplain(labellist,body,stmtlistNode._children[i],functionname)


    def stmtExplain(self,labellist,body,stmtNode,functionname):#对指令进行区分
        if stmtNode != None:
            if isinstance(stmtNode,AssignmentNode):#赋值
                if isinstance(stmtNode.var_access,IndexedVarNode):#是否为数组
                    self.asignExplain(body,stmtNode)
                else:
                    if stmtNode.var_access.identifier.name == functionname:#是否为返回值
                        self.retExplain(body,stmtNode)
                    else:
                        self.asignExplain(body,stmtNode)
            elif isinstance(stmtNode, IfNode):#if
                self.ifExplain(labellist,body,stmtNode,functionname)
            elif isinstance(stmtNode, ForNode):#for
                self.forExplain(labellist,body,stmtNode,functionname)


    def retExplain(self,body,retNode):
        if retNode != None:
            value = {}
            self.exprExplain(body,retNode.expr,value)
            line_number = int(retNode.position.lineno)
            retdata = {}
            retExc(retdata,line_number,value)
            body.append(retdata)




    def asignExplain(self,body,asignNode):
        if asignNode != None:
            line_number = int(asignNode.position.lineno)
            address = {}
            if isinstance(asignNode.var_access,IndexedVarNode):#根据数组解析address
                self.arrayExplain(body,asignNode,address)
            elif isinstance(asignNode.var_access,VarAccessNode):#根据变量解析address
                addrname = str(asignNode.var_access.identifier.name)
                addrtype = str(self.typeExplain(asignNode.var_access.type))+"*"
                variableExc(address,addrname,addrtype,False)
            else:#根据id解析address
                addrname = str(asignNode.identifier.name)
                addrtype = str(self.typeExplain(self.ctx.find_typedef(asignNode.identifier.name)))+"*"
                variableExc(address,addrname,addrtype,False)
            value = {}
            self.exprExplain(body,asignNode.expr,value)
            storedata = {}
            storeExc(storedata,line_number,address,value)
            body.append(storedata)


    def ifExplain(self,labellist,body,ifNode,functionname):
        if ifNode != None:
            thenlabelname=str("ifthenlabel_"+str(self.labelno))#if条件通过后的位置
            elselabelname=str("ifelselabel_"+str(self.labelno))#if条件未通过后的位置
            endlabelname=str("ifendlabel_"+str(self.labelno))#if语句结束的位置
            self.labelno=self.labelno+1
            self.cjumpExplain(body,ifNode.expr,thenlabelname,elselabelname)
            self.labeldefExplain(labellist,body,len(body),thenlabelname)#if条件通过后的位置
            self.stmtlistExplain(labellist,body,ifNode.iftrue,functionname)#if条件通过后
            line_number = ifNode.position.lineno
            jumpdata={}
            jumpExc(jumpdata,line_number,endlabelname)#条件通过时最后跳至结尾
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)#if条件未通过后的位置
            self.stmtlistExplain(labellist,body,ifNode.iffalse,functionname)#if条件未通过
            self.labeldefExplain(labellist,body,line_number,endlabelname)#if语句结束的位置
        


    def labeldefExplain(self,labellist,body,line_number,labelname):
        labelpos = int(len(body))
        label = {}
        labelExc(label,labelname,labelpos)
        labellist.append(label)
        labeldefdata = {}
        labeldefExc(labeldefdata,line_number,labelname)
        body.append(labeldefdata)
        
        
    def cjumpExplain(self,body,exprNode,thenlabelname,elselabelname):
        if exprNode != None:
            condvalue = {}
            self.exprExplain(body,exprNode,condvalue)#先得到表达式的结果
            line_number = int(exprNode.position.lineno)
            cjumpdata = {}
            cjumpExc(cjumpdata,line_number,condvalue,thenlabelname,elselabelname)
            body.append(cjumpdata)
        

        
    def forExplain(self,labellist,body,forNode,functionname):
        if forNode != None:
            startlabelname=str("forstartlabel_"+str(self.labelno))#for循环的开头
            thenlabelname=str("forthenlabel_"+str(self.labelno))#for循环体开头
            elselabelname=str("forelselabel_"+str(self.labelno))#for循环条件不满足
            self.labelno = self.labelno + 1
            line_number = int(forNode.position.lineno)
            forvar = {}#循环变量值
            forend = {}#循环变量尾值
            forstart = {}#循环变量初值
            forvaraddress = {}#循环变量地址
            self.exprExplain(body,forNode.var,forvar)#循环变量值
            self.exprExplain(body,forNode.value_end,forend)#循环变量尾值
            self.exprExplain(body,forNode.value_start,forstart)#循环变量初值
            forvartype = str(self.typeExplain(self.ctx.find_typedef(idNode.name)))+"*"
            variableExc(forvaraddress,forNode.var.name,forvartype,False)#循环变量地址
            self.newasignExplain(line_number,body,forvaraddress,forstart)#循环赋初值
            self.labeldefExplain(labellist,body,line_number,startlabelname)#for循环的开头
            condvalue = {}#判断是否跳出循环，判定
            if forNode.direction==1:
                self.newbinExplain(body,line_number,"S_LTEQ",forvar,forend,condvalue)
            else:
                self.newbinExplain(body,line_number,"S_GTEQ",forvar,forend,condvalue)
            self.cjumpExc(body,exprNode,thenlabelname,elselabelname)#判断是否跳出循环，语句
            self.labeldefExplain(labellist,body,line_number,thenlabelname)#for循环体开头
            self.stmtlistExplain(labellist,body,forNode.body,functionname)#循环内语句
            addvalue = {}
            addright = {}
            valueExc(addright,"s_int16",1)
            self.newvarExplain(addvalue,addleft['type'])
            if forNode.direction==1:#循环变量加1
                self.newbinExplain(body,line_number,"ADD",forvar,addright,addvalue)
            else:#循环变量减1
                self.newbinExplain(body,line_number,"SUB",forvar,addright,addvalue)
            self.newasignExplain(line_number,body,forvaraddress,addvalue)#加减1后存入循环变量
            jumpdata={}
            jumpExc(jumpdata,line_number,startlabelname)#返回到循环的开头
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)#for循环条件不满足
        

    def typeExplain(self, vartype):
        if isinstance(vartype,UIntType):
            return "u_int"+str(vartype.width)
        elif isinstance(vartype,SIntType):
            return "s_int"+str(vartype.width)
        elif isinstance(vartype,EnumType):
            return "u_int"+str(vartype.width)
        elif isinstance(vartype,BoolType):
            return "bool"
        elif isinstance(vartype,CharType):
            return "s_int"+str(vartype.width)
        elif isinstance(vartype,StringType):
            return "string"
        else:
            return str(vartype)





#所有带有new开头的函数区别于不带new开头的函数。
#不带new的函数一般用于解析，
#参数一般为Node
#带new的函数一般直接构造，
#参数一般为值或字典


    def newbinExplain(self,body,line_number,op,left,right,value):
        bindata = {}
        binExc(bindata,line_number,op,left,right,value)
        body.append(bindata)
            

    def newuniExplain(self,body,line_number,op,variable,value):
        unadata = {}
        uniExc(unadata,line_number,op,variable,value)
        body.append(unadata)


    def newvarExplain(self,value,vartype):
        varname = str("%"+str(str(self.varno)))
        self.varno = self.varno+1
        variableExc(value,varname,vartype,False)
            

    def newasignExplain(self,line_number,body,address,value):
        storedata = {}
        storeExc(storedata,line_number,address,value)
        body.append(storedata)




def opExplain(op,UorS,OorT):#将op进行翻译
    if op == "+":
        return "ADD"
    elif op == "-":
        if OorT:
            return "UMINUS"
        else:
            return "SUB"
    elif op == "*":
        return "MUL"
    elif op == "/":
        if UorS:
            return "U_DIV"
        else:
            return "S_DIV"
    elif op == "%":
        if UorS:
            return "U_MOD"
        else:
            return "S_MOD"
    elif op == "<<":
        return "BIT_LSHIFT"
    elif op == ">>":
        if UorS:
            return "BIT_RSHIFT"
        else:
            return "ARITH_RSHIFT"
    elif op == "==":
        return "EQ"
    elif op == "!=":
        return "NEQ"
    elif op == ">":
        if UorS:
            return "U_GT"
        else:
            return "S_GT"
    elif op == "<":
        if UorS:
            return "U_LT"
        else:
            return "S_LT"
    elif op == ">=":
        if UorS:
            return "U_GTEQ"
        else:
            return "S_GTRQ"
    elif op == "<=":
        if UorS:
            return "U_LTEQ"
        else:
            return "S_LTEQ"
    elif op == "~":
        return "BIT_NOT"
    elif op == "&":
        return "BIT_AND"
    elif op == "|":
        return "BIT_OR"
    elif op == "^":
        return "BIT_XOR"
    elif op == "!":
        return "NOT"
    elif UorS:
        return "U_CAST"
    else:
        return "S_CAST"




'''
后面用于const类型，先闲置
'''

def con_exprExplain(exprNode):
    if exprNode != None:
        if isinstance(exprNode,BinaryOpNode):
            return con_binExplain(exprNode)
        elif isinstance(exprNode,UnaryOpNode):
            return con_unaExplain(exprNode)
        else:
            return con_valueExplain(exprNode)
    else:
        return 0


def con_binExplain(binNode):
    if binNode != None:
        if binNode.op.name == "+":
            return con_exprExplain(binNode.left)+con_exprExplain(binNode.right)
        elif binNode.op.name == "-":
            return con_exprExplain(binNode.left)-con_exprExplain(binNode.right)
        elif binNode.op.name == "*":
            return con_exprExplain(binNode.left)*con_exprExplain(binNode.right)
        elif binNode.op.name == "/":
            return con_exprExplain(binNode.left)/con_exprExplain(binNode.right)
        elif binNode.op.name == "%":
            return con_exprExplain(binNode.left)%con_exprExplain(binNode.right)
        elif binNode.op.name == "==":
            return con_exprExplain(binNode.left)==con_exprExplain(binNode.right)
        elif binNode.op.name == "!=":
            return con_exprExplain(binNode.left)!=con_exprExplain(binNode.right)
        elif binNode.op.name == ">":
            return con_exprExplain(binNode.left)>con_exprExplain(binNode.right)
        elif binNode.op.name == ">=":
            return con_exprExplain(binNode.left)>=con_exprExplain(binNode.right)
        elif binNode.op.name == "<":
            return con_exprExplain(binNode.left)<con_exprExplain(binNode.right)
        elif binNode.op.name == "<=":
            return con_exprExplain(binNode.left)<=con_exprExplain(binNode.right)
        elif binNode.op.name == "&":
            return con_exprExplain(binNode.left)&con_exprExplain(binNode.right)
        elif binNode.op.name == "|":
            return con_exprExplain(binNode.left)|con_exprExplain(binNode.right)
        elif binNode.op.name == "^":
            return con_exprExplain(binNode.left)^con_exprExplain(binNode.right)
        elif binNode.op.name == "<<":
            return con_exprExplain(binNode.left)<<con_exprExplain(binNode.right)
        elif binNode.op.name == ">>":
            return con_exprExplain(binNode.left)>>con_exprExplain(binNode.right)
        else:
            return 0
    else:
        return 0



def con_unaExplain(unaNode):
    if unaNode != None:
        if unaNode.name == "-":
            return -con_exprExplain(unaNode.expr)
        elif unaNode.name == "~":
            return ~con_exprExplain(unaNode.expr)
        elif unaNode.name == "!":
            return not con_exprExplain(unaNode.expr)
        else:
            return 0
    else:
        return 0


def con_valueExplain(valueNode):
    if valueNode != None:
        return valueNode.value
    else:
        return 0















