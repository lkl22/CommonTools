# -*- coding: utf-8 -*-
# python 3.x
# Filename: WeditorUtil.py
# 定义一个WeditorUtil工具类实现Weditor安装相关的功能

from util.LogUtil import *
from util.FileUtil import *
from util.ShellUtil import *


class WeditorUtil:
    @staticmethod
    def open(retry=True):
        out, err = ShellUtil.exec('weditor')
        if err:
            if err.__contains__("command not found") or err.__contains__("不是内部或外部命令，也不是可运行的程序"):
                out, err = ShellUtil.exec('python --version')
                if err:
                    if not retry:
                        return err
                    LogUtil.e(err)
                    LogUtil.d('start install python')
                    installPackageFp = FileUtil.getProjectPath() + 'software/python-3.8.6-amd64.exe'
                    # installPackageFp = 'E:/PythonProjects/CommonTools/software/python-3.8.6-amd64.exe'
                    LogUtil.d('install package file path:' + installPackageFp)
                    if os.path.isfile(installPackageFp):
                        out, err = ShellUtil.exec(installPackageFp + ' /passive InstallAllUsers=1 PrependPath=1', timeout=None)
                        if not err:
                            WeditorUtil.open(False)
                    else:
                        info = "请到浏览器输入'https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe'下载python安装包并安装"
                        LogUtil.d(info)
                        return info
                else:
                    LogUtil.d('start install weditor')
                    out, err = ShellUtil.exec('python -m pip install --upgrade pip', timeout=None)
                    if not err:
                        out, err = ShellUtil.exec('pip install -U weditor --index-url https://pypi.tuna.tsinghua.edu.cn/simple/', timeout=None)
                        if not err or err.__contains__("WARNING: You are using pip version"):
                            out, err = ShellUtil.exec('weditor')
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
