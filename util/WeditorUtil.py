# -*- coding: utf-8 -*-
# python 3.x
# Filename: WeditorUtil.py
# 定义一个WeditorUtil工具类实现Weditor安装相关的功能

from util.LogUtil import *
from util.FileUtil import *
from util.ShellUtil import *
from util.WidgetUtil import WidgetUtil


class WeditorUtil:
    @staticmethod
    def open():
        out, err = ShellUtil.exec('weditor')
        if err:
            if err.__contains__("command not found") or err.__contains__("不是内部或外部命令，也不是可运行的程序"):
                out, err = ShellUtil.exec('python --version')
                if err or not out:
                    LogUtil.e(err)
                    LogUtil.d('start install python')
                    installPackageFp = FileUtil.getProjectPath() + '/software/python-3.8.6-amd64.exe'
                    # installPackageFp = 'E:/PythonProjects/CommonTools/software/python-3.8.6-amd64.exe'
                    LogUtil.d('install package file path:' + installPackageFp)
                    if os.path.isfile(installPackageFp):
                        res = ShellUtil.system(installPackageFp + ' /passive InstallAllUsers=1 PrependPath=1')
                        if res:
                            WidgetUtil.showInformationDialog(text='python安装完成，需要重启应用程序生效。')
                            os._exit(0)
                        else:
                            return 'python install failed.'
                    else:
                        info = "请到浏览器输入'https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe'下载python安装包并安装"
                        LogUtil.d(info)
                        return info
                else:
                    LogUtil.d('start install weditor')
                    res = ShellUtil.system('python -m pip install --upgrade pip --index-url https://pypi.tuna.tsinghua.edu.cn/simple/')
                    if res:
                        res = ShellUtil.system('pip install -U weditor --index-url https://pypi.tuna.tsinghua.edu.cn/simple/')
                        if res:
                            out, err = ShellUtil.exec('weditor')
                        else:
                            return 'install weditor failed. please exec "pip install -U weditor --index-url https://pypi.tuna.tsinghua.edu.cn/simple/"'
                    else:
                        return 'upgrade pip failed. please exec "python -m pip install --upgrade pip --index-url https://pypi.tuna.tsinghua.edu.cn/simple/"'
            if err.__contains__("Command 'weditor' timed out after 10 seconds"):
                out, err = ShellUtil.exec('weditor')
            if err and err.__contains__("is already running"):
                info = 'weditor已经打开，请打开浏览器输入"http://localhost:17310"访问'
                LogUtil.d(info)
                return info
            return err
        else:
            return 'open weditor success.'


if __name__ == "__main__":
    WeditorUtil.open()
    # out, err = ShellUtil.exec('wget https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe', timeout=None)
    pass
