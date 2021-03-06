# -*- coding: utf-8 -*-
# python 3.x
# Filename: ShellUtil.py
# 定义一个ShellUtil工具类实现shell指令相关的功能
import os
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
            LogUtil.d("执行指令：\n", cmd)
            p: subprocess.Popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)
            (stdout, stderr) = p.communicate(timeout=timeout)
            LogUtil.d("执行指令结果：\n", stdout)
            if stderr:
                LogUtil.e("执行指令发生错误：", stderr)
            return stdout, stderr
        except Exception as err:
            LogUtil.e("执行指令发生错误：", err)
            return '', '{}'.format(err)

    @staticmethod
    def cmdOutput(cmd, *args, **kwargs):
        """
        Run command use subprocess and get its content

        Returns:
            string of output

        Raises:
            EnvironmentError
        """
        cmds = [cmd]
        cmds.extend(args)
        cmdline = subprocess.list2cmdline(map(str, cmds))
        try:
            return subprocess.check_output(cmdline,
                                           stderr=subprocess.STDOUT,
                                           shell=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            if kwargs.get('raise_error', True):
                raise EnvironmentError(
                    "subprocess", cmdline,
                    e.output.decode('utf-8', errors='ignore'))

    @staticmethod
    def system(cmd):
        """
        执行指令
        :param cmd: 指令
        :return: True 执行成功
        """
        return os.system(cmd) == 0


if __name__ == "__main__":
    # ShellUtil.exec("ls -l ")
    # print(ShellUtil.cmdOutput('python', '-m', 'pip', 'install', '--upgrade', 'pip', '--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple/'))
    # print(ShellUtil.cmdOutput("ls", '-a'))
    print(ShellUtil.system('python1 -V'))
    # ShellUtil.system('python -m pip install --upgrade pip --index-url https://pypi.tuna.tsinghua.edu.cn/simple/')
    print(ShellUtil.system('pip install -U weditor --index-url https://pypi.tuna.tsinghua.edu.cn/simple/'))
    print('finished')
