# TAC IR Format:
三地址码格式IR，又称四元式格式的IR，是优化部分内部使用的一种IR格式，
使用它是为了方便写测试代码。

格式约定如下：

一行为一个语句，语句分为三种：注释，函数定义，指令。
行内使用空格作为分隔符。指令的操作数都是Entity类型。

## Entity
Entity分为两种：var(variable)， val(value)。
类型全部按`int32`处理。

格式举例：
```
var:i
val:1
```


## 注释
注释以`# `开头

格式举例：
```
# 这是一条注释
```
## 函数定义
函数定义格式为`function name param1 param2 ...`
格式举例：
```
function add var:a var:b
```

## 指令
共有十种指令，每种指令格式如下：
###   cjump
`cjump   cond thenlabel elselabel`
###   jump
`jump    label`
###   label_definition
`label_definition      labelname`
###   variable_definition
`variable_definition   variablename var_type`
###   load
`load    adress value`
###   store
`store   adress value`
###   bin
`bin     op left right value`
###   uni
`uni     op variable value`
###   call
`call    functionname parameterlist value`
###   return
`return  ret`

## 完整示例
```
# one comment
function main
label_definition label1
variable_definition   a int32
uni     NOT var:a var:a
cjump   var:a label1 label2
jump    label2
label_definition      label2
variable_definition   var:b int32
load    var:b var:a
store   var:b var:a
bin     ADD var:a var:b var:%1
call    function1 var:a,var:b var:ret1
return  var:ret1

function function1 var:a var:b
bin     ADD var:a var:b var:%1
ret     var:%1
```
