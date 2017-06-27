

# IR 规范---基本结构

近似线性IR，非SSA，包含类型信息。打印格式是 JSON，便于各语言解析以及表示原有抽象语法树结构。



其结构如下：

- program_definition

- function_definition

- label

- variable

- value

- instruction

	- variable_definition

	- label_definition

	- load

	- store

	- cjump

	- jump

	- call

	- return

	- bin

	- uni



## program_definition

```JSON

{

	"object": "program_definition";

	"name": "lalala",

	"filename": "dsq.pas",

	"line_number": 1,

	"variablelist": [

		{

			"object": "instruction",

			"name": "variable_definition",

			...

		},

		...

	],

	"functionlist": [

		{

			"object": "function_definition",

			...

		},

		...

	],

	"labellist": [

		{

			"object": "label",

			"pos": 2

		},

		...

	],

	"body": [

		{

			"object": "instruction",

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

    "type": "int32",

	"parameterlist": [

		{

			"object": "entity",

			"type": int32,

			"name": "a"

		},

		...

	],

	"variablelist": [

		{

			"object": "instruction",

			"name": "variable_definition",

			...

		},

		...

	],

	"labellist": [

		{

			"object": "label",

			"pos": 2

		},

		...

	],

	"body": [

		{

			"object": "instruction",

			"pos": 2

		},

		...

	]

}

```



## label

```JSON

{

    "object": "label",

    "name": "ruaruarua"

	"pos": 2

}

```



## variable

```JSON

{

    "object": "variable",

    "type": "int8",

	"name": "a",

	"const": true,

	"is_private": false

}

```



## value

```JSON

{

    "type": "int8",

    "object": "value",

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



`bool`
布尔



## instruction

指令的打印格式为一个 JSON 对象，`type` 属性为 `instruction`，`name` 属性为此指令名称，每个操作数分别为一个属性，属性名即下文中的操作数名。
以二元操作“>”为例

```

{

	"object": "instruction",

	"name": "bin",

	"filename": "dsq.pas",

	"line_number": 1,

	"op": "S_GT",

	"left": {

    	"object": "variable",

		"type": "int8",

		"name": "a",

		"const": true,

		"is_private": false

	},

	"right": {

    	"type": "int8",

    	"object": "value",

		"value": 1

	},

	"value": {

    	"object": "variable",

		"type": "int8",

		"name": "%1",

		"const": false,

		"is_private": false

	}

}
```

`variable_definition variablename var_type const is_private initvalue value`

定义变量，`variablename` 为string, `var_type` 为type `const` 为bool `value`


`label_definition labelname`

定义标签，`labelname` 为string



`load address value`

取值，`address` 为entity, `value`为entity



`store address value`

取地址，`address` 为entity, `value`为entity



`cjump cond thenLabel elseLabel`

条件跳转，`cond` 为entity，`thenLabel` 和 `elseLabel` 均为label。



`jump label`

无条件跳转，`label` 为label



`call functionname parameterlist value`

调用表达式，`functionname` 为string，`parameterlist` 为entity的列表 `value` 为entity



`return ret`

返回，`ret` 为entity



`bin op left right value`

双目运算，`op` 为entity，`left` 和 `right` 均为entity, `value` 为entity



`uni op variable value`

单目运算，`op` 为entity，`variable` 为entity, `value` 为entity



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



`S_CAST`

有符号数值类型转换



`U_CAST`

无符号数值类型转换



`BIT_AND`

位逻辑与 `&`



`BIT_OR`

位逻辑或 `|`



`BIT_XOR`

位逻辑异或 `^`



`NOT`

逻辑非 `!`



