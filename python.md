
# python注意点

## Python变量的保护、私有等
 
Python 用下划线作为变量前缀和后缀指定特殊变量。
_xxx    不能用'from module import *'导入
__xxx__ 系统定义名字
__xxx   类中的私有变量名，只有内部可以访问，外部不能访问

## 常用内部函数
 __init__(self,...) 初始化对象（实例），在创建新对象时调用
 __del__(self) 析构函数，释放对象，在对象被删除之前调用，进行一些清理工作。
 __new__(cls,*args,**kwd) 实例的生成操作，__new__()在__init__()之前被调用
 __str__(self) 在使用print语句输出实例时被调用
 __getitem__(self,key) 获取序列的索引key对应的值，等价于seq[key]
 __len__(self) 在调用内联函数len()时被调用
 __cmp__(stc,dst) 比较两个对象src和dst
 __getattr__(s,name) 获取属性的值
 __setattr__(s,name,value) 设置属性的值
 __delattr__(s,name) 删除name属性
 __getattribute__() __getattribute__()功能与__getattr__()类似
 __gt__(self,other) 判断self对象是否大于other对象
 __lt__(slef,other) 判断self对象是否小于other对象
 __ge__(slef,other) 判断self对象是否大于或者等于other对象
 __le__(slef,other) 判断self对象是否小于或者等于other对象
 __eq__(slef,other) 判断self对象是否等于other对象
 __call__(self,*args) 把实例作为函数调用

## 静态方法、类方法：
 class MyClass:     
    val=100 #类变量；通过类名直接访问    
    def method(self): #实例方法：有self参数    
        print("instance method")     
    @staticmethod     
    def staticMethod(): #静态方法：没有参数    
        print("static method")    
        print MyClass.val   
    @classmethod     
    def classMethod(cls): #类方法：有cls参数    
        print("class method")    
        print cls.val  

## Return语句
return语句用于退出函数，向调用方返回一个表达式。
return在不带参数的情况下（或者没有写return语句），默认返回None。

None是一个特殊的值，它的数据类型是NoneType。NoneType是Python的特殊类型，它只有一个取值None。
它不支持任何运算也没有任何内建方法，和任何其他的数据类型比较是否相等时永远返回false，也可以将None赋值给任何变量

一般来说Return语句后面的语句不可执行，但在有例外处理时例外

## 装饰器
### 内置的装饰器
内置的装饰器有三个，分别是staticmethod、classmethod和property，作用分别是把类中定义的实例方法变成静态方法、类方法和类属性。由于模块里可以定义函数，所以静态方法和类方法的用处并不是太多，除非你想要完全的面向对象编程。而属性也不是不可或缺的，Java没有属性也一样活得很滋润。从我个人的Python经验来看，我没有使用过property，使用staticmethod和classmethod的频率也非常低。

### 使用语法糖@来装饰函数

import time  
import functools  
   
def timeit(func):  
    @functools.wraps(func)  
    def wrapper():  
        start = time.clock()  
        func()  
        end =time.clock()  
        print 'used:', end - start  
    return wrapper  
  
@timeit  
def foo():  
    print 'in foo()'  
   
foo()  
print foo.__name__ 

## 抽象方法及抽象类

抽象方法可以在类被实例化时触发它：使用python提供的abc模块。
import abc  
class Sheep(object):  
    __metaclass__ = abc.ABCMeta  
    @abc.abstractmethod  
    def get_size(self):  
        return  
      
class sheepson(Sheep):  
    def __init__(self):  
        print 'sheepson.__init__ is called!'  
      
s1=Sheep()   #报错，不能实例化抽象类  
s2=sheepson()#报错，不能实例化抽象类

