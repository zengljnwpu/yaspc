
# IR 规范---基本结构
近似线性IR，非SSA，包含类型信息。打印格式是 JSON，便于各语言解析以及表示原有抽象语法树结构。

其结构如下：
- program_definition
- function_definition
- label
- entity
	- variable
	- value
- instruction
	- variable_definition
	- label_definition
	- bin
	- uni
	- load
	- store
	- addr
	- cjump
	- jump
	- return
	- call

## program_definition
```JSON
{
	"object": "program_definition";
	"name": "lalala",
	"functionlist": [
		{
			"object": "function_definition",
			...
		},
		...
	]
}
```

## fuction_definition
```JSON
{
    "object": "function_definition",
    "filename": "test.cl",
    "line_number": 2,
    "name": "main",
    "type": "int32(int32,int8**)",
	"parameterlist": [
		{
			"object": "var",
			"type": int32,
			"name": "a"
		},
		...
	],
	"labellist": [
		{
			"object": "label",
			"pos": 2
		},
		...
	]
	"body": [
		{
			"object": "label",
			"pos": 2
		},
		...
	]
}
```
注：`is_private` 属性表示此函数是否为 `static`，变量声明同。

## label
```JSON
{
    "object": "label",
    "name": "ruaruarua"
	"pos": 2
}
```

## entity

### variable
```JSON
{
    "object": "entity",
    "type": "int8",
    "name": "variable",
	"variable": "a"
}
```
### const
```JSON
{
    "object": "entity",
    "type": "int8",
    "name": "const",
	"variable": "a"
}
```

### value
```JSON
{
    "object": "entity",
    "type": "int8",
    "name": "value",
	"value": 1
}
```

### type

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



## instruction

指令的打印格式为一个 JSON 对象，`type` 属性为 `instruction`，`name` 属性为此指令名称，每个操作数分别为一个属性，属性名即下文中的操作数名。

`cjump cond thenLabel elseLabel`
条件跳转，`cond` 为entity，`thenLabel` 和 `elseLabel` 均为label。

`jump label`
无条件跳转，`label` 为label

`label_definition labelname`
定义标签，`labelname` 为string

`variable_definition variablename var_type`
定义变量，`variablename` 为string, `var_type` 为type

`const_definition constname var_type`
定义变量，`constname` 为string, `var_type` 为type

`return ret`
返回，`ret` 为entity

	`call functionname parameterlist`
	调用表达式，`functionname` 为string，`parameterlist` 为entity的列表

`addr variable value`
取地址，`variable` 为entity, `value`为entity

`load address value`
取值，`address` 为entity, `value`为entity

`store address value`
取地址，`address` 为entity, `value`为entity

`uni op variable value`
单目运算，`op` 为entity，`variable` 为entity, `value` 为entity

`bin op left right value`
双目运算，`op` 为entity，`left` 和 `right` 均为entity, `value` 为entity

#### 运算符

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

# IR 规范---高级结构翻译(样例)

## if-else
####example
```
if a>2 then a=2 else a=1;
```
####cond calculation
```
{
	"object": "instruction",
	"name": "variable_definition",
	"variablename": "%cond1",
	"var_type": int32
}, 
{
	"object": "instruction",
	"name": "bin",
	"op": "S_GT",
	"left": {
		"object": "entity",
		"type": "int32",
		"name": "variable",
		"variable": "a"
	},
	"right": {
		"object": "entity",
		"type": "int32",
		"name": "value",
		"value": 1
	},
	"value": {
		"object": "entity",
		"type": "int32",
		"name": "variable",
		"variable": "%cond1"
	}
},
```
####cjump
```
{
	"object": "instruction",
	"name": "cjump",
	"cond": {
		"object": "entity",
		"type": "int32",
		"name": "variable",
		"variable": "%cond1"
	},
	"thenlabel": "ifthenlabel1",
	"elselabel": "ifelselabel1"
},
```
####ifthenlabel definition
```
{
	"object": "instruction",
	"name": "label_definition",
	"labelname": "ifthenlabel1"
},
```
####then block
```
{
	"object": "instruction",
	"name": "variable_definition",
	"variablename": "%ap1",
	"var_type": int32*
},
{
	"object": "instruction",
	"name": "addr",
	"variable": {
		"object": "entity",
		"type": "int32",
		"name": "variable",
		"variable": "a"
	},
	“value”: {
		"object": "entity",
		"type": "int32*",
		"name": "variable",
		"variable": "%ap1"
	},
}
{
	"object": "instruction",
	"name": "store",
	"address": {
		"object": "entity",
		"type": "int32*",
		"name": "variable",
		"variable": "%ap1"
	},
	"value": {
		"object": "entity",
		"type": "int32",
		"name": "value",
		"value": 2
	}
}
```
####jump to end
```
{
	"object": "instruction",
	"name": "jump",
	"label": "ifendlabel1"
}
```
####ifelselabel definition
```
{
	"object": "instruction",
	"name": "label_definition",
	"labelname": "ifelselabel1"
}
```
####else block
```
{
	"object": "instruction",
	"name": "variable_definition",
	"variablename": "%ap2",
	"var_type": int32*
},
{
	"object": "instruction",
	"name": "addr",
	"variable": {
		"object": "entity",
		"type": "int32",
		"name": "variable",
		"variable": "a"
	},
	“value”: {
		"object": "entity",
		"type": "int32*",
		"name": "variable",
		"variable": "%ap2"
	},
}
{
	"object": "instruction",
	"name": "store",
	"address": {
		"object": "entity",
		"type": "int32*",
		"name": "variable",
		"variable": "%ap2"
	},
	"value": {
		"object": "entity",
		"type": "int32",
		"name": "value",
		"value": 1
	}
}
```
####endlabel definition
```
{
	"object": "instruction",
	"name": "label_definition",
	"labelname": "ifendlabel1"
}
```

## for
```JSON
{
        "object": "variable_definition",
        ...
}, 
```

## switch
```JSON
{
        "object": "variable_definition",
        ...
}, 
```
## array
```JSON
{
        "object": "variable_definition",
        ...
}, 
```

## structure
```JSON
{
        "object": "variable_definition",
        ...
}, 
```
#question
	指针
	call
	assign	addr	load	store	allocate
