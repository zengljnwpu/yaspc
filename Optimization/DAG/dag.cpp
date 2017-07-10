#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <stdlib.h>

/*function ans data statement*/
#define MAXN 5				 /*符号或变量最大长度*/
/*结点类型*/
typedef struct node
{
	int iscons;				 /*0-- 无 1--整型 2--浮点*/
	int val_int;			 /*整型值*/
	double val_float;		 /*浮点值*/
	int idnum;				 /*变量的个数*/
	char id[MAXN][MAXN];	 /*变量0~valnum-1*/
	char op[MAXN];			 /*结点操作*/
	int left, right;	       	 /*左右节点*/
}DAGNODE;

#define MAXNN	20			``/*DAG最大结点数目*/
/*DAG*/
typedef struct mnode
{
	int num;				/*结点个数*/
	DAGNODE node[MAXNN];	/*结点内容1~NUM*/
}DAG;

/*四元式Quaternion*/
typedef struct snode
{
	int type;				/*类型0 1 2*/
	char op[MAXN];			/*操作*/
	char op1[MAXN];			/*操作数1*/
	char op2[MAXN];			/*操作数2*/
	char ans[MAXN];			/*结果*/
}QUA;

void init();/*初始化函数*/
bool getqua(QUA *qua);		/*获取一个四元式*/
int isnums(char *val);	/*检测字符串是否是数字串 0 标识符 1整型数串 2浮点数串*/
void makeleaf(DAGNODE *n, char val[]);/*构造叶子结点*/
void makenode(DAGNODE *n, char op[], int left, int right);/*构造中间结点*/
int getnode(DAG dag, char var[]);	 /*获取var[]所在结点号*/
int find1node(DAG dag, char op1[], char op[]);/*查找已有的表达式1*/
int  find2node(DAG dag, char op1[], char op2[], char op[]);/*查找已知表达式2*/
char *isconsnode(DAG dag, char id[]);/*是否是常数结点的id*/
void delnode(DAG *dag, int num);/*删除结点num*/
void delid(DAG *dag, int num);/*删除某节点的Id*/
void copynode(DAGNODE *to, DAGNODE from);/*复制结点值*/
void insertvar(DAG *dag, int noden, char var[]);  /*将值var附加在noden结点*/
int insertnode(DAG *dag, DAGNODE dagn);/*将结点插入DAG*/
char *calcons1(char op[], char op1[]);/*计算op op1的运算值*/
char *calcons2(char op[], char op1[], char op2[]);/*op1 op op2*/
void makeDAG();				/*构造DAG*/
void dispDAG(DAG dag);      /*输出DAG*/
char *getv(DAG dag, int dagn);
FILE *fp;	/*文件指针，指向代码文件*/
void dispcode();


int main()
{
	init();

	dispcode();

	init();
	makeDAG();
	return 0;
}


void dispcode()
{
	static int i = 1;
	QUA q;
	while (getqua(&q))
	{
		if (q.type == 0)
			printf("(%d) %s%s%s\n", i++, q.ans, q.op, q.op1);
		else if (q.type == 1)
			printf("(%d) %s=%s%s\n", i++, q.ans, q.op, q.op1);
		else
			printf("(%d) %s=%s%s%s\n", i++, q.ans, q.op1, q.op, q.op2);
	}

}
/*初始化函数*/
void init()
{
	if ((fp = fopen("code.txt", "r")) == NULL)
	{
		printf("the code file is not existed."); exit(0);
	}
}
/*获取一个四元式*/
bool getqua(QUA *qua)
{
	int t;
	if (feof(fp)) { fclose(fp); return false; }
	fscanf(fp, "%d", &t);
	fscanf(fp, "%s", qua->ans);
	fscanf(fp, "%s", qua->op);
	fscanf(fp, "%s", qua->op1);

	if (fgetc(fp) == '\n' || feof(fp)) {
		strcpy(qua->op2, "");
		if (!strcmp(qua->op, "="))
			qua->type = 0;
		if (feof(fp)) { fclose(fp); return false; }
		return true;
	}
	fscanf(fp, "%s", qua->op);
	if (fgetc(fp) == '\n' || feof(fp)) {
		strcpy(qua->op2, qua->op);
		strcpy(qua->op, qua->op1);
		strcpy(qua->op1, qua->op2);
		strcpy(qua->op2, "");
		qua->type = 1;
		if (feof(fp)) { fclose(fp); return false; }
		return true;
	}
	fscanf(fp, "%s", qua->op2);
	qua->type = 2;
	return true;
}
int isnums(char *val)
{
	int i, flag;
	for (i = 0; val[i]; i++) {
		if (!isdigit(val[i])) {
			if (val[i] == '.')/*浮点*/
			{
				flag = 2; break;
			}
			flag = 0; break;
		}
		else {
			flag = 1; /*整型*/
		}
	}
	return flag;
}
/*构造叶子结点*/
void makeleaf(DAGNODE *n, char val[])
{

	switch (isnums(val))
	{
	case 0:
		n->iscons = 0;
		n->val_float = 0;
		n->val_int = 0;
		n->idnum = 1;
		strcpy(n->id[0], val);
		break;
	case 1:
		n->idnum = 0;
		n->iscons = 1;
		n->val_int = atoi(val);
		n->val_float = 0;
		break;
	case 2:
		n->idnum = 0;
		n->iscons = 2;
		n->val_int = 0;
		n->val_float = atof(val);
		break;
	}

	strcpy(n->op, "");
	n->left = n->right = 0;
}
/*构造中间结点*/
void makenode(DAGNODE *n, char op[], int left, int right)
{
	n->idnum = 0;
	n->iscons = 0;
	strcpy(n->op, op);
	n->left = left;
	n->right = right;
}
/*获取var[]所在结点号*/
int getnode(DAG dag, char var[])
{
	int i, j;
	if (dag.num == 0) return 0;
	for (i = 1; i <= dag.num; i++)
	{
		switch (isnums(var))
		{
		case 0:
			for (j = 0; j<dag.node[i].idnum; j++)
				if (!strcmp(dag.node[i].id[j], var))
					return i;
			break;
		case 1:
			if (dag.node[i].val_int == atoi(var))
				return i;
			break;
		case 2:
			if (dag.node[i].val_float == atof(var))
				return i;
			break;
		}
	}
	return 0;
}
/*是否是常数节点,常数*/
char *isconsnode(DAG dag, char id[])
{
	int i, j;
	char *temp;
	temp = (char *)malloc(MAXN * sizeof(char));
	if (isnums(id)) { strcpy(temp, id); return temp; }
	for (i = 1; i <= dag.num; i++)
	{
		if (dag.node[i].iscons>0)/*常数结点*/
		{
			for (j = 0; j<dag.node[i].idnum; j++)
				if (!strcmp(dag.node[i].id[j], id)) {
					switch (dag.node[i].iscons) {
					case 1:
						sprintf(temp, "%d", dag.node[i].val_int);
						break;
					case 2:
						sprintf(temp, "%g", dag.node[i].val_float);
						break;
					}
					return temp;
				}
		}
	}
	return NULL;
}
/*查找已定义的表达式1*/
int find1node(DAG dag, char op1[], char op[])
{
	int i;
	int op1n;
	op1n = getnode(dag, op1);
	for (i = 1; i <= dag.num; i++)
		if ((dag.node[i].left == op1n) && !strcmp(dag.node[i].op, op))
			return i;
	return 0;
}
/*查找已知表示式2*/
int find2node(DAG dag, char op1[], char op2[], char op[])
{
	int i;
	int op1n, op2n;
	op1n = getnode(dag, op1);
	op2n = getnode(dag, op2);
	for (i = 1; i <= dag.num; i++)
		if ((dag.node[i].left == op1n) && (dag.node[i].right == op2n) && !strcmp(dag.node[i].op, op))
			return i;
	return 0;
}
/*删除结点num*/
void delnode(DAG *dag, int num)
{
	int i, j;
	if (dag->num == 0) return;
	for (i = 1; i <= dag->num; i++)
		if (i == num) {
			for (j = i; j <= dag->num; j++)
				copynode(&(dag->node[j]), dag->node[j + 1]);
		}
	--(dag->num);
}
/*删除某结点的id*/
void delid(DAG *dag, int num)
{
	int i;
	if (dag->num == 0) return;
	for (i = 0; i<dag->node[num].idnum; i++)
		strcpy(dag->node[num].id[i], "");
	dag->node[num].idnum = 0;

}
/*赋值结点值*/
void copynode(DAGNODE*to, DAGNODE from)
{
	int i;
	to->idnum = from.idnum;
	for (i = 0; i<from.idnum; i++)
		strcpy(to->id[i], from.id[i]);
	to->iscons = from.iscons;
	to->val_int = from.val_int;
	to->val_float = from.val_float;
	strcpy(to->op, from.op);
	to->left = from.left;
	to->right = from.right;
}
/*将值var附加在noden结点*/
void insertvar(DAG *dag, int noden, char var[])
{
	(dag->node[noden].idnum)++;
	strcpy(dag->node[noden].id[dag->node[noden].idnum - 1], var);
}
/*将结点插入DAG*/
int insertnode(DAG *dag, DAGNODE dagn)
{
	dag->num = dag->num + 1;
	copynode(&(dag->node[dag->num]), dagn);
	return dag->num;
}

/*计算op op1的运算值*/
char *calcons1(char op[], char op1[])
{
	char *temp;
	if (!strcmp(op, "!")) {
		temp = (char *)malloc(MAXN * sizeof(char));
		switch (isnums(op1)) {
		case 1:sprintf(temp, "%d", !atoi(op1)); break;
		}
	}
	return temp;
}
/*计算 op1 op op2 的值*/
char *calcons2(char op[], char op1[], char op2[])
{
	int ch = isnums(op1)>isnums(op2) ? isnums(op1) : isnums(op2);
	char *temp;
	temp = (char *)malloc(MAXN * sizeof(char));
	if (!strcmp(op, "+")) {
		switch (ch) {
		case 1:
			sprintf(temp, "%d", atoi(op1) + atoi(op2));
			break;
		case 2:
			sprintf(temp, "%g", atof(op1) + atof(op2));
			break;
		}
	}
	else if (!strcmp(op, "-")) {
		switch (ch) {
		case 1:
			sprintf(temp, "%d", atoi(op1) - atoi(op2));
			break;
		case 2:
			sprintf(temp, "%g", atof(op1) - atof(op2));
			break;
		}
	}
	else if (!strcmp(op, "*")) {
		switch (ch) {
		case 1:
			sprintf(temp, "%d", atoi(op1)*atoi(op2));
			break;
		case 2:
			sprintf(temp, "%g", atof(op1)*atof(op2));
			break;
		}
	}
	else if (!strcmp(op, "/")) {
		/*！除法结果为浮点*/
		sprintf(temp, "%g", atof(op1) / atof(op2));
	}
	return temp;
}
/*构造DAG*/
void makeDAG()
{
	DAG dag; dag.num = 0;/*DAG*/
	QUA qua;    	  /*四元式*/
	DAGNODE dagn;     /*DAG结点*/
	int op1n, op2n, opn, oopn;	 /*操作数1--B 2--C所在结点号*/

	char temp[MAXN];
	int newleft, newright;
	while (getqua(&qua)) {
		/*op1--B没有定义*/
		newleft = newright = 0;
		if (getnode(dag, qua.op1) == 0) {
			makeleaf(&dagn, qua.op1);
			insertnode(&dag, dagn);/*将结点插入DAG*/
			newleft = 1;
		}
		switch (qua.type) {
		case 0:/*(=,B, ,A)*/
			op1n = getnode(dag, qua.op1);
			if ((opn = getnode(dag, qua.ans)) != 0)/*ans--A已经定义*/
				delid(&dag, opn);
			insertvar(&dag, op1n, qua.ans);/*将ans--A附加在B的结点上*/
			break;
		case 1:/*(op,B, A)*/
			if (isconsnode(dag, qua.op1) != NULL) {	/*op1--B是常数 返回值为 1或者 2*/
				if (newleft == 1) {/*op1--B是新建结点*/
					delnode(&dag, getnode(dag, qua.op1));
				}
				sprintf(temp, "%s", calcons1(qua.op, isconsnode(dag, qua.op1)));
				if (getnode(dag, temp) == 0) {
					makeleaf(&dagn, temp);
					opn = insertnode(&dag, dagn);
				}
			}
			else {
				if ((opn = find1node(dag, qua.op1, qua.op)) == 0) {
					makenode(&dagn, qua.op, getnode(dag, qua.op1), 0);
					opn = insertnode(&dag, dagn);
				}
			}
			if ((oopn = getnode(dag, qua.ans)) != 0)/*ans--A已经定义*/
				delid(&dag, oopn);
			insertvar(&dag, opn, qua.ans);/*将ans--A附加在B的结点上*/
			break;
		case 2:/*(op,B,C,A)*/
			if (getnode(dag, qua.op2) == 0) {
				makeleaf(&dagn, qua.op2);
				insertnode(&dag, dagn);/*将结点插入DAG*/
				newright = 1;
			}
			if ((isconsnode(dag, qua.op1) != NULL) && (isconsnode(dag, qua.op2) != NULL)) /*op1 --A op2 --B 在结点中*/
			{
				sprintf(temp, "%s", calcons2(qua.op, isconsnode(dag, qua.op1), isconsnode(dag, qua.op2)));
				if (newleft == 1)
					delnode(&dag, getnode(dag, qua.op1));
				if (newright == 1)
					delnode(&dag, getnode(dag, qua.op2));
				if (getnode(dag, temp) == 0) {
					makeleaf(&dagn, temp);
					opn = insertnode(&dag, dagn);/**/
				}
			}
			else {/**/
				if ((opn = find2node(dag, qua.op1, qua.op2, qua.op)) == 0) {
					op1n = getnode(dag, qua.op1);
					op2n = getnode(dag, qua.op2);
					makenode(&dagn, qua.op, op1n, op2n);
					opn = insertnode(&dag, dagn);/**/
				}
			}
			/**/
			if ((oopn = getnode(dag, qua.ans)) != 0)/*ans--A已经定义*/
				delid(&dag, oopn);
			insertvar(&dag, opn, qua.ans);/*将ans--A附加在B的结点上*/ /**/
			break;
		}
	}
	printf("\nDAG优化:\n");
	dispDAG(dag);
}

/*输出DAG*/
void dispDAG(DAG dag)
{
	int i, j;
	int count = 0;

	for (i = 1; i <= dag.num; i++)
	{
		if (dag.node[i].iscons>0 && dag.node[i].idnum == 1) {
			switch (dag.node[i].iscons) {
			case 1:printf("(%d) %s=%d\n", ++count, dag.node[i].id[0], dag.node[i].val_int); break;
			case 2:printf("(%d) %s=%g\n", ++count, dag.node[i].id[0], dag.node[i].val_float); break;
			}
		}
		else if (dag.node[i].idnum >= 1 && dag.node[i].left != 0 && dag.node[i].right != 0) {
			printf("(%d) %s=%s%s%s\n", ++count, dag.node[i].id[0], getv(dag, dag.node[i].left), dag.node[i].op, getv(dag, dag.node[i].right));
			if (dag.node[i].idnum>1)
				for (j = 1; j<dag.node[i].idnum; j++)
				{
					printf("(%d) %s=%s\n", ++count, dag.node[i].id[j], dag.node[i].id[j - 1]);
				}
		}
	}
}

char *getv(DAG dag, int dagn)
{

	char *temp;
	temp = (char *)malloc(MAXN * sizeof(char));
	if (dag.node[dagn].iscons == 0) {
		strcpy(temp, dag.node[dagn].id[0]);
	}
	else if (dag.node[dagn].iscons == 1) {
		sprintf(temp, "%d", dag.node[dagn].val_int);
	}
	else if (dag.node[dagn].iscons == 2) {
		sprintf(temp, "%g", dag.node[dagn].val_float);
	}
	else {
		strcpy(temp, "");
	}
	return temp;
}

