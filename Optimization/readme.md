# 优化

优化整体的入口为 do_optimization.py
该程序可以直接运行，可以使用命令行参数，使用--help选项查看详细参数
也可以import该代码，调用其中的main函数或do_optimization函数


## 关于库的配置：
推荐增加.pth文件：
在site-packages添加一个路径文件，如mypkpath.pth，必须以.pth为后缀，写上你要加入的模块文件所在的目录名称就是了。
在此项目中使用yaspc文件夹所在的目录

1 windows
    C:\Users\lzc\AppData\Local\Programs\Python\Python36\Lib\site-packages

2 linux(ubuntu)
   /usr/local/lib/python2.7/dist-packages
3 linux(redhat)
   /usr/lib/python2.7/site-packages