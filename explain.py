# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, with_statement

import json

from frontend.ast import *    
from frontend.exchange import *
from frontend.compiler import *
from frontend.typesys import *
from frontend import typesys




class explain(object):

    varno = 0;
    labelno = 0;

    #store the final data dictionary
    def store(self,data):
        with open('data.json', 'w') as json_file:
            json_file.write(json.dumps(data))


    #programNode is given by user
    def programEplain(self,programNode):
        if programNode != None:
            name = str(programNode.identifier.name)
            line_number = int(programNode.position.lineno)
            varlist = []
            body = []
            self.users_var_defExplain(varlist,body,programNode.block.var_list,programNode.block.const_list)
            funclist = []
            self.funclistExplain(funclist,programNode.block.func)
            labellist = []
            self.stmtlistExplain(varlist,labellist,body,programNode.block.stmt)
            programdata = {}
            programExc(programdata,name,line_number,varlist,funclist,labellist,body)
            self.store(programdata)


    def users_var_defExplain(self,varlist,body,varlistNode,constlistNode):
        if varlistNode != None:
            for i in range(len(varlistNode._children)):
                self.vardefExplain(varlist,body,varlistNode._children[i])
        if constlistNode != None:
            for i in range(len(constlistNode._children)):
                self.constdefExplain(varlist,body,constlistNode._children[i])



    def vardefExplain(self,varlist,body,vardeclNode):
        if vardeclNode != None:
            vartype = str(vardeclNode.type_denoter.identifier.name)
            line_number = int(vardeclNode.position.lineno)
            for i in range(len(vardeclNode.identifier_list._children)):
                vardefdata = {}
                vardata = {}
                variablename = str(vardeclNode.identifier_list._children[i].name)
                vardefExc(vardefdata,line_number,variablename,vartype)
                variableExc(vardata,variablename,vartype,False)
                body.append(vardefdata)
                varlist.append(vardata)



    def constdefExplain(self,varlist,body,constdeclNode):
        if constdeclNode != None:
            value = {}
            exprExplain(varlist,body,constdeclNode.expr,value)
            vartype = str(self.typeExplain(constdeclNode.type))
            line_namber = int(constdeclNode.position.lineno)
            constdefdata = {}
            vardata = {}
            constname = str(constdeclNode.identifier.name)
            constdefExc(constdefdata,Line_number,constname,vartype,value)
            variableExc(vardata,constname,vartype,ture)
            body.append(vardefdata)
            varlist.append(vardata)



    def funclistExplain(self,funclist,funclistNode):
        if funclistNode != None:
            for i in range(len(funclistNode._children)):
                funcdata = {}
                self.funcExplain(funcdata,funclistNode._children[i])
                funclist.append(funcdata)



    def funcExplain(self,funcdata,funcNode):
        if funcNode != None:
            name = str(funcNode.header.identifier.name)
            line_number = int(funcNode.position.lineno)
            functype = str(self.typeExplain(funcNode.header.return_type))
            paralist = []
            self.paralistExplain(paralist,funcNode.header.param_list)
            varlist = []
            body = []
            self.users_var_defExplain(varlist,body,funcNode.block.var_list,funcNode.block.const_list)
            labellist = []
            self.stmtlistExplain(varlist,labellist,body,funcNode.block.stmt)
            functionExc(funcdata,name,line_number,functype,paralist,varlist,labellist,body)



    def paralistExplain(self,paralist,paramlistNode):
        if paramlistNode != None:
            for i in range(len(paramlistNode._children)):
                paradata = {}
                self.paraExplain(paradata,paramlistNode._children[i])
                paralist.append(paradata)


    def paraExplain(self,paradata,paraNode):
        if paraNode != None:
            if isinstance(paraNode,ValueParameterNode):
                self.ValueParaExplain(paradata,paraNode)
            else:
                self.refparaExplain(paradata,paraNode)


    def ValueParaExplain(self,paradata,paraNode):
        if paraNode != None:
            for i in range(len(paraNode.identifier_list._children)):
                tempdata = {}
                varname = str(paraNode.identifier_list._children[i].name)
                vartype = str(self.typeExplain(paraNode.type_denoter))
                variableExc(tempdata,varname,vartype,False)


    def refparaExplain(self,paradata,paraNode):
        if paraNode != None:
            self.ValueParaExplain(paradata,paraNode)



    def exprExplain(self,varlist,body,exprNode,value):
        if exprNode != None:
            if isinstance(exprNode,BinaryOpNode):
                self.binExplain(varlist,body,exprNode,value)
            elif isinstance(exprNode,UnaryOpNode):
                self.uniExplain(varlist,body,exprNode,value)
            elif isinstance(exprNode,FunctionCallNode):
                self.funccallExplain(varlist,body,exprNode,value)
            elif isinstance(exprNode,VarAccessNode):
                self.varExplain(value,exprNode)
            elif isinstance(exprNode,VarLoadNode):
                self.varExplain(value,exprNode.var_access)
            else:
                self.valueExplain(value,exprNode)


    def funccallExplain(self,varlist,body,funccallNode,value):
        if funccallNode != None:
            varname = str("%"+str(str(self.varno)))
            self.varno = self.varno+1
            vartype = str(self.typeExplain(funccallNode.type))
            variableExc(value,varname,vartype,False)
            varlist.append(value)
            calldata = {}
            line_number = int(funccallNode.position.lineno)
            functionname = str(funccallNode.identifier.name)
            paramaterlist = []
            self.argulistExplain(paramaterlist,varlist,body,funccallNode.arg_list)
            callExc(calldata,line_number,functionname,paramaterlist,value)
            


    def argulistExplain(self,paramaterlist,varlist,body,argulistNode):
        if argulistNode != None:
            for i in range(len(argulistNode._children)):
                value = {}
                self.exprExplain(varlist,body,argulistNode._children[i].expr,value)
                paramaterlist.append(value)



    def binExplain(self,varlist,body,binNode,value):
        if binNode != None:
            line_number = int(binNode.position.lineno)
            op = binNode.op.name
            leftentity = {}
            self.exprExplain(varlist,body,binNode.left,leftentity)
            rightentity = {}
            self.exprExplain(varlist,body,binNode.right,rightentity)
            varname = str("%"+str(str(self.varno)))
            self.varno = self.varno+1
            vartype = str(self.typeExplain(binNode.type))
            variableExc(value,varname,vartype,False)
            varlist.append(value)
            bindata = {}
            binExc(bindata,line_number,op,leftentity,rightentity,value)
            body.append(bindata)



    def uniExplain(self,varlist,body,unaNode,value):
        if unaNode != None:
            line_number = str(unaNode.position.lineno)
            op = str(unaNode.name)
            entity = {}
            self.exprExplain(varlist,body,unaNode.expr,entity)
            varname = str("%"+str(self.varno))
            self.varno = self.varno+1
            vartype = str(self.typeExplain(uniNode.type))
            variableExc(value,varname,vartype,False)
            varlist.append(value)
            unadata = {}
            unaExc(unidata,line_number,op,variable,entity)
            body.append(unadata)



    def varExplain(self,value,varaccessNode):
        if varaccessNode != None:
            varname = str(varaccessNode.identifier.name)
            vartype = str(self.typeExplain(varaccessNode.type))
            variableExc(value,varname,vartype,False)


    def valueExplain(self,valuedata,valueNode):
        if valueNode != None:
            valtype = str(self.typeExplain(valueNode.type))
            value = valueNode.value
            valueExc(valuedata,valtype,value)


    def stmtlistExplain(self,varlist,labellist,body,stmtlistNode):
        if stmtlistNode != None:
            for i in range(len(stmtlistNode._children)):
                self.stmtExplain(varlist,labellist,body,stmtlistNode._children[i])


    def stmtExplain(self,varlist,labellist,body,stmtNode):
        if stmtNode != None:
            if isinstance(stmtNode,AssignmentNode):
                self.asignExplain(varlist,labellist,body,stmtNode)
            elif isinstance(stmtNode, IfNode):
                wqt1=1
                self.ifExplain(varlist,labellist,body,stmtNode)
            elif isinstance(stmtNode, ForNode):
                wqt1=1
                self.forExplain(varlist,labellist,body,stmtNode)


    def asignExplain(self,varlist,labellist,body,asignNode):
        if asignNode != None:
            line_number = int(asignNode.position.lineno)
            address = {}
            self.varExplain(address,asignNode.var_access)
            value = {}
            self.exprExplain(varlist,body,asignNode.expr,value)
            storedata = {}
            storeExc(storedata,line_number,address,value)
            body.append(storedata)


    def ifExplain(self,varlist,labellist,body,ifNode):
        if ifNode != None:
            thenlabelname=str("ifthenlabel_"+str(self.labelno))
            elselabelname=str("ifelselabel_"+str(self.labelno))
            endlabelname=str("ifendlabel_"+str(self.labelno))
            self.labelno=self.labelno+1
            self.cjumpExplain(varlist,body,ifNode.expr,thenlabelname,elselabelname)
            self.labeldefExplain(labellist,body,line_number,thenlabelname)
            self.stmtlistExplain(varlist,labellist,body,ifNode.ifTrue)
            line_number = ifNode.position.lineno
            jumpdata={}
            jumpExc(jumpdata,line_number,endlabelname)
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)
            self.stmtlistExplain(varlist,labellist,body,ifNode.ifFalse)
            self.labeldefExplain(labellist,body,line_number,endlabelname)
        


    def labeldefExplain(self,labellist,body,line_number,labelname):
        labelpos = int(len(body))
        label = {}
        labelExc(label,labelname,labelpos)
        labellist,append(label)
        labeldefdata = {}
        labeldefExc(labeldefdata,line_number,labelname)
        body.append(labeldefdata)
        
        
    def cjumpExplain(self,varlist,body,exprNode,thenlabelname,elselabelname):
        if exprNode != None:
            condvalue = {}
            self.exprExplain(varlist,body,expr,condvalue)
            line_number = int(exprNode.position.lineno)
            cjumpdata = {}
            cjumpExc(cjumpdata,line_number,condvalue,thenlabelname,elselabelname)
            body.append(cjumpdata)
        

        
    def forExplain(self,varlist,labellist,body,forNode):
        if forNode != None:
            startlabelname=str("forstartlabel_"+str(self.labelno))
            thenlabelname=str("forthenlabel_"+str(self.labelno))
            elselabelname=str("forelselabel_"+str(self.labelno))
            self.labelno = self.labelno + 1
            line_number = int(forNode.position.lineno)
            asignNode1 = AssignmentNode(forNode.var,forNode.value_start)
            self.asignExplain(varlist,labellist,body,asignNode1)
            self.labeldefExplain(labellist,body,line_number,startlabelname)
            if forNode.direction==1:
                exprNode=BinaryOpNode(forNode.var,"S_LTEQ",forNode.end_val)
            else:
                exprNode=BinaryOpNode(forNode.var,"S_GTEQ",forNode.end_val)
            self.cjumpExplain(varlist,body,exprNode,thenlabelname,elselabelname)
            self.labeldefExplain(labellist,body,line_number,thenlabelname)
            self.stmtlistExplain(varlist,labellist,body,forNode.body)
            varppNode=BinaryOpNode(forNode.var,"ADD",IntegerNode(1))
            asignNode2 = AssignmentNode(forNode.var,varppNode)
            self.asignExplain(varlist,labellist,body,asignNode2)
            jumpdata={}
            jumpExc(jumpdata,line_number,endlabelname)
            body.append(jumpdata)
            self.labeldefExplain(labellist,body,line_number,elselabelname)
        

    def typeExplain(type,vartype):
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
        
wqttest = Compiler("a.pas")
wqttest.analyze()
test = explain()
test.programEplain(wqttest.ast)






