# 优化

优化整体的入口为 `do_optimization.py` 。
该程序可以直接运行，可以使用命令行参数，使用--help选项查看详细参数。
另一种方式是`import`该代码，调用其中的`main`函数或`do_optimization`函数。

## 中间表示的形式：
优化部分代码支持两种形式的IR：
* 四元式形式：参见`IR_IO/irParser.py`
* JSON形式：参见`IR.md`

## 关于Python版本：
优化部分代码兼容`Python2.7.x`和`Python3.4+`
在`Python 2.7.12` 和 `Python 3.5.2` 下测试通过

## 关于库的配置：
推荐增加`.pth`文件：
在`site-packages`添加一个路径文件，如`mypkpath.pth`，必须以`.pth`为后缀，写上你要加入的模块文件所在的目录名称就是了。
在此项目中使用`yaspc`文件夹所在的目录

1 windows
    `C:\Users\lzc\AppData\Local\Programs\Python\Python36\Lib\site-packages`

2 linux(ubuntu)
   `/usr/local/lib/python2.7/dist-packages`

3 linux(redhat)
   `/usr/lib/python2.7/site-packages`