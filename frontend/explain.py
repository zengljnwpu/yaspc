

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json

from frontend.ast import * #@UnusedWildImport
from frontend.exchange import * #@UnusedWildImport
from frontend.compiler import * #@UnusedWildImport
from frontend.typesys import * #@UnusedWildImport

class explain(object):
    varno = 0
    labelno = 0
    programdata = {}
    ctx = None

    #store the final data dictionary
    def store(self):
        with open('data.json', 'w') as json_file:
            json_file.write(json.dumps(self.programdata))


    #programNode is given by user
    def programEplain(self,programNode,realctx):
        if programNode != None:
            # ctx = realctx
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


    def users_var_defExplain(self,varlist,varlistNode):
        if varlistNode != None:
            for i in range(len(varlistNode._children)):
                self.vardefExplain(varlist,varlistNode._children[i])


    def users_con_defExplain(self,varlist,constlistNode):
        if constlistNode != None:
            for i in range(len(constlistNode._children)):
                self.constdefExplain(varlist,constlistNode._children[i])



    def vardefExplain(self,varlist,vardeclNode):
        if vardeclNode != None:
            line_number = int(vardeclNode.position.lineno)
            if isinstance(vardeclNode.type_denoter,ArrayTypeNode):
                vartype = str(vardeclNode.type_denoter.component_type.identifier.name)+"*"
                for i in range(len(vardeclNode.identifier_list._children)):
                    vardefdata = {}
                    variablename = str(vardeclNode.identifier_list._children[i].name)
                    number = 1
                    for j in range(len(vardeclNode.type_denoter.index_list._children)):
                        start = vardeclNode.type_denoter.index_list._children[j].start.value
                        stop = vardeclNode.type_denoter.index_list._children[j].stop.value
                        if stop > start:
                            number = number*(stop-start+1)
                        else:
                            number = number*(start-stop+1)
                    vardefExc(vardefdata,line_number,variablename,vartype,number)
                    varlist.append(vardefdata)
            else:
                vartype = str(vardeclNode.type_denoter.identifier.name)+"*"
                for i in range(len(vardeclNode.identifier_list._children)):
                    vardefdata = {}
                    variablename = str(vardeclNode.identifier_list._children[i].name)
                    vardefExc(vardefdata,line_number,variablename,vartype,1)
                    varlist.append(vardefdata)


    def constdefExplain(self,varlist,constdeclNode):
        if constdeclNode != None:
            value = con_exprExplain(constdeclNode.expr)
            vartype = str(self.typeExplain(constdeclNode.type))+"*"
            line_number = int(constdeclNode.position.lineno)
            constdefdata = {}
            constname = str(constdeclNode.identifier.name)
            constdefExc(constdefdata,line_number,constname,vartype,value)
            varlist.append(constdefdata)



    def funclistExplain(self,funclist,funclistNode):
        if funclistNode != None:
            for i in range(len(funclistNode._children)):
                if isinstance(funclistNode._children[i],FunctionNode):
                    funcdata = {}
                    self.funcExplain(funcdata,funclistNode._children[i])
                    funclist.append(funcdata)
                else:
                    procdata = {}
                    self.procExplain(procdata,funclistNode._children[i])
                    funclist.append(procdata)



    def funcExplain(self,funcdata,funcNode):
        if funcNode != None:
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



    def procExplain(self,procdata,procNode):
        if procNode != None:
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






    def exprExplain(self,body,exprNode,value):
        if exprNode != None:
            if isinstance(exprNode,BinaryOpNode):
                self.binExplain(body,exprNode,value)
            elif isinstance(exprNode,UnaryOpNode):
                self.unaExplain(body,exprNode,value)
            elif isinstance(exprNode,FunctionCallNode):
                self.funccallExplain(body,exprNode,value)
            elif isinstance(exprNode,VarAccessNode):
                self.varExplain(body,exprNode,value)
            elif isinstance(exprNode,VarLoadNode):
                if isinstance(exprNode.var_access,IndexedVarNode):
                    self.arrayExplain(body,exprNode,value)
                else:
                    self.varExplain(body,exprNode.var_access,value)
            elif isinstance(exprNode,IdentifierNode):
                self.idExplain(body,exprNode,value)
            else:
                self.valueExplain(value,exprNode)


    def funccallExplain(self,body,funccallNode,value):
        if funccallNode != None:
            self.newvarExplain(value,str(self.typeExplain(funccallNode.type)))
            calldata = {}
            line_number = int(funccallNode.position.lineno)
            functionname = str(funccallNode.identifier.name)
            paramaterlist = []
            self.argulistExplain(paramaterlist,body,funccallNode.arg_list)
            callExc(calldata,line_number,functionname,paramaterlist,value)
            body.append(calldata)


    def argulistExplain(self,paramaterlist,body,argulistNode):
        if argulistNode != None:
            for i in range(len(argulistNode._children)):
                value = {}
                self.exprExplain(body,argulistNode._children[i].expr,value)
                paramaterlist.append(value)




    def binExplain(self,body,binNode,value):
        if binNode != None:
            line_number = int(binNode.position.lineno)
            leftentity = {}
            self.exprExplain(body,binNode.left,leftentity)
            op = opExplain(binNode.op.name,1,0)
            rightentity = {}
            self.exprExplain(body,binNode.right,rightentity)
            self.newvarExplain(value,str(self.typeExplain(binNode.type)))
            bindata = {}
            binExc(bindata,line_number,op,leftentity,rightentity,value)
            body.append(bindata)



    def uniExplain(self,varlist,body,uniNode,value):
        if uniNode != None:
            line_number = str(uniNode.position.lineno)
            op = str(uniNode.name)
            entity = {}
            self.exprExplain(varlist,body,uniNode.expr,entity)
            varname = str("%"+str(self.varno))
            self.varno = self.varno+1
            vartype = str(self.typeExplain(uniNode.type))
            variableExc(value,varname,vartype,False)
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
            addrtype = str(self.typeExplain(idNode.type))+"*"
            address = {}
            variableExc(address,addrname,addrtype,False)
            self.newvarExplain(value,str(self.typeExplain(idNode.type)))
            loaddata = {}
            loadExc(loaddata,line_number,address,value)
            body.append(loaddata)

    def valueExplain(self,valuedata,valueNode):
        if valueNode != None:
            valtype = str(self.typeExplain(valueNode.type))
            value = valueNode.value
            valueExc(valuedata,valtype,value)
   


    def arrayExplain(self,body,arrayNode,value):
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


    def stmtExplain(self,labellist,body,stmtNode,functionname):
        if stmtNode != None:
            if isinstance(stmtNode,AssignmentNode):
                if isinstance(stmtNode.var_access,IndexedVarNode):
                    self.asignExplain(body,stmtNode)
                else:
                    if stmtNode.var_access.identifier.name == functionname:
                        self.retExplain(labellist,body,stmtNode)
                    else:
                        self.asignExplain(body,stmtNode)
            elif isinstance(stmtNode, IfNode):
                self.ifExplain(labellist,body,stmtNode,functionname)
            elif isinstance(stmtNode, ForNode):
                self.forExplain(labellist,body,stmtNode,functionname)


    def retExplain(self,labellist,body,retNode):
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
            if isinstance(asignNode.var_access,IndexedVarNode):
                self.arrayExplain(body,asignNode,address)
            elif isinstance(asignNode.var_access,VarAccessNode):
                addrname = str(asignNode.var_access.identifier.name)
                addrtype = str(self.typeExplain(asignNode.var_access.type))+"*"
                variableExc(address,addrname,addrtype,False)
            else:
                addrname = str(asignNode.var_access.name)
                addrtype = str(self.typeExplain(asignNode.var_access.type))+"*"
                variableExc(address,addrname,addrtype,False)
            value = {}
            self.exprExplain(body,asignNode.expr,value)
            storedata = {}
            storeExc(storedata,line_number,address,value)
            body.append(storedata)


    def ifExplain(self,labellist,body,ifNode,functionname):
        if ifNode != None:
            thenlabelname=str("ifthenlabel_"+str(self.labelno))
            elselabelname=str("ifelselabel_"+str(self.labelno))
            endlabelname=str("ifendlabel_"+str(self.labelno))
            self.labelno=self.labelno+1
            self.cjumpExplain(body,ifNode.expr,thenlabelname,elselabelname)
            self.labeldefExplain(labellist,body,len(body),thenlabelname)
            self.stmtlistExplain(labellist,body,ifNode.iftrue,functionname)
            line_number = ifNode.position.lineno
            jumpdata={}
            jumpExc(jumpdata,line_number,endlabelname)
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)
            self.stmtlistExplain(labellist,body,ifNode.iffalse,functionname)
            self.labeldefExplain(labellist,body,line_number,endlabelname)
        


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
            self.exprExplain(body,exprNode,condvalue)
            line_number = int(exprNode.position.lineno)
            cjumpdata = {}
            cjumpExc(cjumpdata,line_number,condvalue,thenlabelname,elselabelname)
            body.append(cjumpdata)
        

        
    def forExplain(self,labellist,body,forNode,functionname):
        if forNode != None:
            startlabelname=str("forstartlabel_"+str(self.labelno))
            thenlabelname=str("forthenlabel_"+str(self.labelno))
            elselabelname=str("forelselabel_"+str(self.labelno))
            self.labelno = self.labelno + 1
            line_number = int(forNode.position.lineno)
            address1 = {}
            variableExc(address1,forNode.var.name,forNode.var.type,False)
            value1 = {}
            self.exprExplain(body,forNode.value_start,value1)
            self.newasignExplain(line_number,body,address1,value1)
            self.labeldefExplain(labellist,body,line_number,startlabelname)
            if forNode.direction==1:
                exprNode=BinaryOpNode(OpNode("S_LTEQ"),VarAccessNode(forNode.var),forNode.value_end)
            else:
                exprNode=BinaryOpNode(OpNode("S_GTEQ"),VarAccessNode(forNode.var),forNode.value_end)
            self.cjumpExplain(body,exprNode,thenlabelname,elselabelname)
            self.labeldefExplain(labellist,body,line_number,thenlabelname)
            self.stmtlistExplain(labellist,body,forNode.body,functionname)
            BinaryOpNode(OpNode("ADD"),VarAccessNode(forNode.var),IntegerNode(1))
            addleft = {}
            self.exprExplain(body,forNode.var,addleft)
            addright = {}
            valueExc(addright,"s_int16",1)
            addvalue = {}
            self.newvarExplain(addvalue,addleft['type'])
            self.newbinExplain(body,line_number,"ADD",addleft,addright,addvalue)
            address2 = {}
            self.exprExplain(body,forNode.var,address2)
            self.newasignExplain(line_number,body,address2,addvalue)
            jumpdata={}
            jumpExc(jumpdata,line_number,startlabelname)
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)
        

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



    def newbinExplain(self,body,line_number,op,left,right,value):
        bindata = {}
        binExc(bindata,line_number,op,left,right,value)
        body.append(bindata)
            


    def newvarExplain(self,value,vartype):
        varname = str("%"+str(str(self.varno)))
        self.varno = self.varno+1
        variableExc(value,varname,vartype,False)
            

    def newasignExplain(self,line_number,body,address,value):
        storedata = {}
        storeExc(storedata,line_number,address,value)
        body.append(storedata)





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



def opExplain(op,UorS,OorT):
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













