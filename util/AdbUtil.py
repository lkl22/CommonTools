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

    @staticmethod
    def getVersionCode(packageName: str, defaultCode: int = -1):
        """
        获取指定包名apk的version code
        :param packageName: apk的包名
        :param defaultCode: 默认返回值
        :return: version code
        """
        return AdbUtil.getVersionInfo(packageName, "versionCode", defaultCode)

    @staticmethod
    def getVersionName(packageName: str, defaultName: str = ""):
        """
        获取指定包名apk的version name
        :param packageName: apk的包名
        :param defaultName: 默认返回值
        :return: version name
        """
        return AdbUtil.getVersionInfo(packageName, "versionName", defaultName)

    @staticmethod
    def getVersionInfo(packageName: str, key: str, defaultValue: any):
        """
        获取指定包名apk的version信息
        :param packageName: apk的包名
        :param key: version信息的查找关键字
        :param defaultValue: 查找失败的默认返回值
        :return: 指定查询的版本信息
        """
        if not AdbUtil.isInstalled(packageName):
            return defaultValue
        out, err = ShellUtil.exec("adb shell dumpsys package {} | {} {}".format(packageName, findCmd, key))
        if err or not out:
            return defaultValue
        if key in out:
            datas = out.strip().split(" ")
            for item in datas:
                if key in item:
                    return item.split("=")[1].strip()
        return defaultValue

    @staticmethod
    def getApkPath(packageName: str):
        """
        获取apk安装的path
        :param packageName: apk的包名
        :return: apk安装的path
        """
        if not AdbUtil.isInstalled(packageName):
            return ""
        out, err = ShellUtil.exec("adb shell pm path {}".format(packageName))
        if err or not out:
            return ""
        return out

    @staticmethod
    def getRunningActivities():
        """
        查看正在运行的activities
        :return: 正在运行的activities
        """
        out, err = ShellUtil.exec("adb shell dumpsys activity activities | {} Run".format(findCmd))
        if err or not out:
            return ""
        return out


if __name__ == "__main__":
    androidTestAssistTool = 'com.lkl.androidtestassisttool'
    androidTestAssistTool1 = 'com.lkl.androidtestassisttool1'
    # print(AdbUtil.getVersionCode(androidTestAssistTool))
    # print(AdbUtil.getVersionCode(androidTestAssistTool1))

    # print(AdbUtil.getVersionName(androidTestAssistTool))
    # print(AdbUtil.getVersionName(androidTestAssistTool1))

    # print(AdbUtil.getApkPath(androidTestAssistTool))
    # print(AdbUtil.getApkPath(androidTestAssistTool1))

    print(AdbUtil.getRunningActivities())
