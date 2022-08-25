# 概览

![](doc/img/developTools.png)


图片压缩工具

![](doc/img/compressPic.png)

Android资源文件复制/移动工具：

![](doc/img/androidResTool.png)

Android color资源管理工具：

![](doc/img/androidColorResTool.png)

[Android 自动化测试预研：](doc/autoTest.md)

![](doc/img/autoTest/adbDialog.png)

[图片预览](doc/picturePreview.md)

![](doc/img/photoWall/picWall.png)

[算法学习](doc/algorithm.md)

![](doc/img/algorithm/AlgorithmVisualizerManager.png)

# 开发指南

## 环境配置
1、下载PyCharm

[https://www.jetbrains.com/pycharm/download/#section=windows](https://www.jetbrains.com/pycharm/download/#section=windows)

2、下载安装python3

[https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

3、pip安装需要的库

`pip install PyQt5 PyQt5-tools Pyinstaller xlrd xlutils uiautomator2 weditor numpy QScintilla tinify openpyxl --index-url https://pypi.tuna.tsinghua.edu.cn/simple/`

4、PyCharm配置

设置External Tools
![External Tools](doc/img/pycharm_external_tools.png)

* 设置Qt Designer

Name：Qt Designer

Programs：D:\Python\Python38\Lib\site-packages\pyqt5_tools\Qt\bin\designer.exe

Working directory：$ProjectFileDir$

* 配置PyUIC

Name：PyUIC

Programs：D:\Python\Python38\python.exe

Parameters：-m PyQt5.uic.pyuic  $FileName$ -o $FileNameWithoutExtension$.py

Working directory：$ProjectFileDir$

## 使用Qt Designer
1、点击 Tools -》External Tools -》Qt Designer 启动我们的Qt Designer

## Python项目的打包（Windows）
1、spec文件，见CommonTools.spec

2、pyinstaller -D CommonTools.spec

## 参考文献

[pycharm如何设置python版本、设置国内pip镜像、添加第三方类库](https://www.cnblogs.com/yjmyzz/p/pycharm-add-third-package-and-add-domestic-mirror.html)

[使用PYINSTALLER打包多文件和目录的PYTHON项目](https://www.cnblogs.com/shiyongge/p/10582552.html)

[Python 3.6.12 文档](https://docs.python.org/zh-cn/3.6/)

[awesome-adb](https://github.com/BlankLun/awesome-adb)

[uiautomator2](https://github.com/BlankLun/uiautomator2)

[python中的subprocess.Popen()使用](https://www.cnblogs.com/zhoug2020/p/5079407.html)

[https://tinypng.com/developers/reference/python](https://tinypng.com/developers/reference/python)

[https://www.iconfont.cn/](https://www.iconfont.cn/)

[使用Python 3从网上下载文件](https://blog.csdn.net/xfxf996/article/details/107784224)

[subprocess --- 子进程管理](https://docs.python.org/zh-cn/3.7/library/subprocess.html)
