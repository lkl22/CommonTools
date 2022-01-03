# -*- coding: utf-8 -*-
# python 3.x
# Filename: AdbUtil.py
# 定义一个AdbUtil工具类实现adb指令操作相关的功能
import base64
from xml.dom.minidom import Element

from util.DateUtil import DateUtil, LogUtil
from util.DomXmlUtil import DomXmlUtil
from util.FileUtil import FileUtil
from util.PlatformUtil import PlatformUtil
from util.ShellUtil import ShellUtil

if PlatformUtil.isMac():
    findCmd = "grep"
else:
    findCmd = "findstr"

ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME = 'com.lkl.androidtestassisttool'
ANDROID_TEST_ASSIST_TOOL_OPERATION_RECEIVER_NAME = '.receiver.OperationReceiver'
ANDROID_TEST_ASSIST_TOOL_OPERATION_RECEIVER_ACTION = 'OperationReceiver'


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
    def startActivity(packageName: str, activityName: str = None, extraParams: str = ""):
        """
        启动app/指定activity
        :param packageName: apk的包名
        :param activityName: 要启动的activity
        :param extraParams: 传给activity的参数
        :return: 执行结果
        """
        if activityName:
            out, err = ShellUtil.exec("adb shell am start -n {}/{} {}".format(packageName, activityName, extraParams))
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
        """
        向手机输入框输入中文、特殊字符等
        :param text: 要输入等文本
        :return: 执行完
        """
        charsBase64 = str(base64.b64encode(text.encode('utf-8')))[1:]
        curKeyboardId = AdbUtil.getCurKeyboardId()
        ShellUtil.exec("adb shell ime set {}/.adbkeyboard.AdbIME".format(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME))
        ShellUtil.exec("adb shell am broadcast -a ADB_INPUT_B64 --es msg %s" % charsBase64)
        ShellUtil.exec("adb shell ime set {}".format(curKeyboardId))
        return True

    @staticmethod
    def sendOperationRequest(*intentExtras):
        """
        向手机测试apk发送操作指令
        :param intentExtras: 传递的参数
        :return: 操作结果
        """
        extraParams = []
        for extra in intentExtras:
            extraParams += extra
        out, err = ShellUtil.exec("adb shell am broadcast -a {} -n {}/{} {}"
                                  .format(ANDROID_TEST_ASSIST_TOOL_OPERATION_RECEIVER_ACTION,
                                          ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME,
                                          ANDROID_TEST_ASSIST_TOOL_OPERATION_RECEIVER_NAME,
                                          " ".join(extraParams)))
        if err or not out:
            return ""
        items = out.strip().split(" ")
        for item in items:
            if "data=" in item:
                return item.split("=")[1].replace("\"", "").strip()
        return ""

    @staticmethod
    def putStringExtra(key: str, value: str = None):
        """
        传递 string 类型的参数
        :param key: key值
        :param value: value值
        :return: 组装好的列表数据
        """
        if value:
            return ["--es", key, value]
        else:
            return ["--esn", key]

    @staticmethod
    def putBooleanExtra(key: str, value: bool = False):
        """
        传递 boolean 类型的参数
        :param key: key值
        :param value: value值
        :return: 组装好的列表数据
        """
        if value:
            return ["--ez", key, 'true']
        else:
            return ["--ez", key, 'false']

    @staticmethod
    def putIntExtra(key: str, value: int):
        """
        传递 int 类型的参数
        :param key: key值
        :param value: value值
        :return: 组装好的列表数据
        """
        return ["--ei", key, str(value)]

    @staticmethod
    def putLongExtra(key: str, value: int):
        """
        传递 long 类型的参数
        :param key: key值
        :param value: value值
        :return: 组装好的列表数据
        """
        return ["--el", key, str(value)]

    @staticmethod
    def putFloatExtra(key: str, value: float):
        """
        传递 float 类型的参数
        :param key: key值
        :param value: value值
        :return: 组装好的列表数据
        """
        return ["--ef", key, str(value)]

    @staticmethod
    def pullFile(src: str, dst: str = ''):
        """
        复制设备里的文件到电脑
        :param src: 设备里的文件路径
        :param dst: 电脑上的目录
        :return: 操作结果
        """
        return ShellUtil.exec("adb pull {} {}".format(src, dst))

    @staticmethod
    def pushFile(src: str, dst: str):
        """
        复制电脑里的文件到设备
        :param src: 电脑上的文件路径
        :param dst: 设备里的目录
        :return: 操作结果
        """
        return ShellUtil.exec("adb push {} {}".format(src, dst))

    @staticmethod
    def forceStopApp(packageName):
        """
        强制停止应用
        :param packageName: 应用包名
        :return: 执行结果
        """
        return ShellUtil.exec("adb shell am force-stop {}".format(packageName))

    @staticmethod
    def findUiElementCenter(text: str):
        """
        查找指定文本的界面元素的中心位置
        :param text: 要查找的文字
        :return: 元素中心点
        """
        phoneTempDumpFile = '/data/local/tmp/uidump.xml'
        tempDumpFile = 'uidump.xml'
        ShellUtil.exec("adb shell uiautomator dump {} && adb pull {} {}"
                       .format(phoneTempDumpFile, phoneTempDumpFile, tempDumpFile))
        srcXml = DomXmlUtil.readXml(tempDumpFile)
        elements: [Element] = DomXmlUtil.findElements(srcXml, 'node', 'text', text, isBlurMatch=True)
        for element in elements:
            bounds = element.getAttribute("bounds").replace("[", ",").replace("]", "")[1:].split(",")
            x = int(bounds[2]) / 2 + int(bounds[0]) / 2
            y = int(bounds[3]) / 2 + int(bounds[1]) / 2
            LogUtil.e("find element bounds {}".format(bounds))
            return x, y
        FileUtil.removeFile(tempDumpFile)
        return None, None

    @staticmethod
    def click(x: float, y: float):
        """
        点击屏幕
        :param x: x坐标
        :param y: y坐标
        """
        ShellUtil.exec("adb shell input tap {} {}".format(x, y))


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
    print(AdbUtil.startActivity(androidTestAssistTool, ".MainActivity", " ".join(AdbUtil.putIntExtra('cacheSize', 60))))
    # print(AdbUtil.startActivity(androidTestAssistTool1))

    # print(AdbUtil.getCurKeyboardId())
    # print(AdbUtil.inputBase64Text("hello && 你好！"))
    # print(AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", "startMuxer"),
    #                                    AdbUtil.putLongExtra('timestamp', DateUtil.nowTimestamp(True)),
    #                                    AdbUtil.putIntExtra('totalTime', 60)))

    # print(AdbUtil.pullFile('/sdcard/backup.xml'))
    # print(AdbUtil.pushFile('/Users/likunlun/PycharmProjects/CommonTools/util/backup.xml', '/sdcard/backup1.xml'))

    # print(AdbUtil.findUiElementCenter("允许|立即开始|Allow|Start now"))
    # print(AdbUtil.click(786.0, 1800.0))
