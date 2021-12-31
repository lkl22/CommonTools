# -*- coding: utf-8 -*-
# python 3.x
# Filename: AdbUtil.py
# 定义一个AdbUtil工具类实现adb指令操作相关的功能
import base64

from util.PlatformUtil import PlatformUtil
from util.ShellUtil import ShellUtil

if PlatformUtil.isMac():
    findCmd = "grep"
else:
    findCmd = "findstr"

ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME = 'com.lkl.androidtestassisttool'

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
    def uninstallApk(packageName: str):
        """
        卸载指定包名的apk
        :param packageName: apk包名
        :return: 输出结果
        """
        out, err = ShellUtil.exec("adb uninstall {}".format(packageName))
        return out

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

    @staticmethod
    def clearApkData(packageName: str):
        """
        清除apk的数据
        :param packageName: apk的包名
        :return: 正在运行的activities
        """
        out, err = ShellUtil.exec("adb shell pm clear {}".format(packageName))
        return out

    @staticmethod
    def startActivity(packageName: str, activityName: str = None):
        """
        启动app/指定activity
        :param packageName: apk的包名
        :param activityName: 要启动的activity
        :return: 执行结果
        """
        if activityName:
            out, err = ShellUtil.exec("adb shell am start -n {}/{}".format(packageName, activityName))
        else:
            out, err = ShellUtil.exec(
                "adb shell monkey -p {} -c android.intent.category.LAUNCHER 1".format(packageName))
        return out

    @staticmethod
    def startAdbServer():
        """
        启动 adb server 命令
        :return: 执行结果
        """
        out, err = ShellUtil.exec("adb start-server")
        return out

    @staticmethod
    def killAdbServer():
        """
        停止 adb server 命令
        :return: 执行结果
        """
        out, err = ShellUtil.exec("adb kill-server")
        return out

    @staticmethod
    def inputText(text: str):
        """
        向输入框输入文本
        :return: 执行结果
        """
        out, err = ShellUtil.exec('adb shell input text {}'.format(text))
        return out

    @staticmethod
    def getCurKeyboardId():
        """
        获取当前使用的软键盘的ID
        :return: 当前使用的软键盘的ID
        """
        out, err = ShellUtil.exec('adb shell settings get secure default_input_method')
        if out:
            return out
        out, err = ShellUtil.exec('adb shell ime list -s')
        if err or not out:
            return None
        items = out.split("\n")
        for item in items:
            if ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME not in item:
                return item.strip()
        return None

    @staticmethod
    def inputBase64Text(text):
        charsBase64 = str(base64.b64encode(text.encode('utf-8')))[1:]
        curKeyboardId = AdbUtil.getCurKeyboardId()
        ShellUtil.exec("adb shell ime set com.lkl.androidtestassisttool/.adbkeyboard.AdbIME")
        ShellUtil.exec("adb shell am broadcast -a ADB_INPUT_B64 --es msg %s" % charsBase64)
        ShellUtil.exec("adb shell ime set {}".format(curKeyboardId))
        return True


if __name__ == "__main__":
    androidTestAssistTool = 'com.lkl.androidtestassisttool'
    androidTestAssistTool1 = 'com.lkl.androidtestassisttool1'
    # print(AdbUtil.getVersionCode(androidTestAssistTool))
    # print(AdbUtil.getVersionCode(androidTestAssistTool1))

    # print(AdbUtil.getVersionName(androidTestAssistTool))
    # print(AdbUtil.getVersionName(androidTestAssistTool1))

    # print(AdbUtil.getApkPath(androidTestAssistTool))
    # print(AdbUtil.getApkPath(androidTestAssistTool1))

    # print(AdbUtil.getRunningActivities())

    # print(AdbUtil.clearApkData(androidTestAssistTool))

    # print(AdbUtil.uninstallApk(androidTestAssistTool))
    # print(AdbUtil.uninstallApk(androidTestAssistTool1))

    # print(AdbUtil.startActivity(androidTestAssistTool, ""))
    # print(AdbUtil.startActivity(androidTestAssistTool, ".MainActivity"))
    # print(AdbUtil.startActivity(androidTestAssistTool1))

    print(AdbUtil.getCurKeyboardId())
    print(AdbUtil.inputBase64Text("hello && 你好！"))
