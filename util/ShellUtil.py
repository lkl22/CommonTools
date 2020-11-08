# -*- coding: utf-8 -*-
# python 3.x
# Filename: ShellUtil.py
# 定义一个ShellUtil工具类实现shell指令相关的功能

import subprocess
from util.LogUtil import *


class ShellUtil:
    @staticmethod
    def exec(cmd: str, timeout=10):
        """
        执行shell指令
        :param timeout: timeout
        :param cmd: shell指令
        :return: 执行结果，错误信息
        """
        # 如果把universal_newlines 设置成True，则子进程的stdout和stderr被视为文本对象，并且不管是*nix的行结束符（'/n'
        # ），还是老mac格式的行结束符（'/r' ），还是windows 格式的行结束符（'/r/n' ）都将被视为 '/n' 。
        try:
            p: subprocess.Popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
            (stdout, stderr) = p.communicate(timeout=timeout)
            LogUtil.d("执行指令结果：\n", stdout)
            if stderr:
                LogUtil.e("执行指令发生错误：", stderr)
            return stdout, stderr
        except Exception as err:
            LogUtil.e("执行指令发生错误：", err)
            return '', '{}'.format(err)


if __name__ == "__main__":
    ShellUtil.exec("ls -l ")
