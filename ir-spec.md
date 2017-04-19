# YASCC IR 规范

树状 IR，非 SSA，包含类型信息。打印格式是 JSON，便于各语言解析以及表示原有抽象语法树结构。

## 代码块

```JSON
{
    "object": "block",
    "filename": "test.cl",
    "line_number": "",
    "sub_blocks": [
        {
            "object": "block",
            ...
        },
        ...
    ],
    "functions": [
        {
            "object": "function_definition",
            ...
        },
        ...
    ],
    "variables": [
        {
            "object": "variable_definition",
            ...
        },
        ...
    ]
}
```
## 函数定义
```JSON
{
    "object": "function_definition",
    "filename": "test.cl",
    "line_number": 2,
    "name": "main",
    "is_private": true, 
    "type": "int32(int32,int8**)",
    "body": [
        {
            "object": "instrument",
            ...
        }, 
        ...
    ]
}
```
注：`is_private` 属性表示此函数是否为 `static`，变量声明同。

## 变量声明
```JSON
{
    "object": "variable_definition",
    "filename": "test.cl",
    "line_number": 3,
    "name": "a",
    "is_private": true, 
    "type": "int8",
}
```
## 表达式
```JSON
{
    "object": "expression",
    "type": "int32",
    "instrument": {
        "object": "instrument",
        ...
    }
}
```
注：`type` 为该表达式的值。每个表达式包含一个指令。

## 标签
```JSON
{
    "object": "label",
    "name": "ruaruarua"
}
```
## 情况
```JSON
{
    "object": "case",
    "value": 1,
    "label": {
        "object": "label",
        ...
    }
}
```
注：仅用于 `switch` 指令。
## 实体
```JSON
{
    "object": "entity",
    "type": "int8",
    "value": 1,
    "name": ""
}
```
注：类型可以为所有类型名称或 "variable"，表示变量的值。

当此实体非变量时，`value` 属性为一个整数或字符串，表示字面值，此时忽略 `name` 属性。

当此实体为变量时，请忽略 `value` 属性，此时 `name` 属性表示变量名。


## 指令

指令的打印格式为一个 JSON 对象，`type` 属性为 `instruction`，`name` 属性为此指令名称，每个操作数分别为一个属性，属性名即下文中的操作数名。

以 `assign` 为例：
```JSON
{
    "object": "instruction",
    "name": "assign",
    "filename": "test.cl",
    "line_number": 4,
    "lhs": {
        "object": "expression",
        ...
    },
    "rhs": {
        "object": "expression",
        ...
    }
}
```

`assign lhs rhs`
赋值，`lhs` 和 `rhs` 均为表达式

`cjump cond thenLabel elseLabel`
条件跳转，`cond` 为表达式，`thenLabel` 和 `elseLabel` 均为标签。

`jump label`
无条件跳转，`label` 为标签

`switch cond cases defaultLabel`
switch 跳转，`cond` 为表达式，`cases` 为情况的列表，`defaultLabel` 为标签

`labelStmt label`
定义标签，`label` 为标签

`exprStmt expr`
执行表达式，`expr` 为表达式

`return expr`
返回，`expr` 为表达式

`uni op expr`
单目运算，`op` 为运算符，`expr` 为表达式

`bin op left right`
双目运算，`op` 为运算符，`left` 和 `right` 均为表达式

`call expr args`
调用表达式，`expr` 为表达式，`args` 为表达式的列表

`addr expr`
取地址，`expr` 为表达式

`mem expr`
取值，`expr` 为表达式

`var entity`
变量值，`entity` 为实体

`int value`
整数型值，`value` 为实体

`str entry`
字符串值，`entry` 为实体

## 类型和运算符

### 类型

在打印格式中均用一个字符串表示。

`int8`
8 bit 整数

`int16`
16 bit 整数

`int32`
32 bit 整数

`int64`
64 bit 整数

`string`
字符串

### 运算符

在打印格式中均用一个字符串表示。

`ADD`
加 `+`

`SUB`
减 `-`

`MUL`
乘 `*`

`S_DIV`
有符号除 `/`

`U_DIV`
无符号除 `/`

`S_MOD`
有符号取模 `%`

`U_MOD`
无符号取模 `%`

`BIT_AND`
位逻辑与 `&`

`BIT_OR`
位逻辑或 `|`

`BIT_XOR`
位逻辑异或 `^`

`BIT_LSHIFT`
逻辑左移（无符号） `<<`

`BIT_RSHIFT`
逻辑右移（无符号） `>>`

`ARITH_RSHIFT`
算术右移（有符号） `>>`

`EQ`
比较 `==`

`NEQ`
比较 `!=`

`S_GT`
有符号数值比较 `>`

`S_GTEQ`
有符号数值比较 `>=`

`S_LT`
有符号数值比较 `<`

`S_LTEQ`
有符号数值比较 `<=`

`U_GT`
无符号数值比较 `>`

`U_GTEQ`
无符号数值比较 `>=`

`U_LT`
无符号数值比较 `<`

`U_LTEQ`
无符号数值比较 `<=`

`UMINUS`
取反 `-`

`BIT_NOT`
按位取反 `~`

`NOT`
逻辑非 `!`

`S_CAST`
有符号数值类型转换

`U_CAST`
无符号数值类型转换


