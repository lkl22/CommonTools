# -*- coding: utf-8 -*-
# python 3.x
# Filename: AdbUtil.py
# 定义一个AdbUtil工具类实现adb指令操作相关的功能
from util.PlatformUtil import PlatformUtil
from util.ShellUtil import ShellUtil

if PlatformUtil.isMac():
    findCmd = "grep"
else:
    findCmd = "findstr"


class AdbUtil:
    @staticmethod
    def isInstalled(packageName: str):
        """
        判断指定包名的apk是否已经安装
        :param packageName: apk包名
        :return: True 已经安装
        """
        out, err = ShellUtil.exec("adb shell pm list packages | {} {}".format(findCmd, packageName))
        if err or not out:
            return False
        if packageName in out:
            return True
        return False


if __name__ == "__main__":
    androidTestAssistTool = 'com.lkl.androidtestassisttool'
    print(AdbUtil.isInstalled(androidTestAssistTool))
