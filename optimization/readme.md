# 优化

 优化整体的入口为 `program_optimizer.py` 。
 使用方法请参考test目录下代码。

## 中间表示的形式：
优化部分代码支持两种形式的IR：
* JSON形式：参见`IR.md`
* 四元式形式：参见`IR_TAC.md`

## 关于Python版本：
优化部分代码兼容`Python2.7.x`和`Python3.4+`。
在`Python 2.7.12` 和 `Python 3.5.2` 下测试通过。

## 关于库的配置：
### 方法一： 使用sys.path.append
可参考`Optimizaition/test/testBasicBlock.py`.
在所有需要直接运行的代码中加入下面内容：
``` python
    # 将yaspc所在路径加入path，确保import能正常运行
    import sys
    sys.path.append('yaspc-cli.py所在目录')
```
### 方法二：增加`.pth`文件
新建一个以`.pth`为后缀的文件，如`mypkpath.pth`。文件里写上你要加入的模块所在的目录名称。
在此项目中使用`yaspc-cli.py`所在的目录。
例如`yaspc-cli.py`在目录`/home/username/Desktop/Compiler/yaspc/`下，则`mypkpath.pth`的内容为`/home/username/Desktop/Compiler/yaspc`。

将此文件放在Python的`site-packages`文件夹下，`site-packages`文件夹的位置可由系统类型和Python版本确定：

1 windows
    `C:\Users\lzc\AppData\Local\Programs\Python\Python36\Lib\site-packages`

2 linux(ubuntu)
   `/usr/local/lib/python2.7/dist-packages`

3 linux(redhat)
   `/usr/lib/python2.7/site-packages`
