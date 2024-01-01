# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidOperator.py
# 定义一个AndroidOperator工具类实现android cmd相关的功能
from util.AdbUtil import AdbUtil
from util.ShellUtil import ShellUtil
from util.phoneCmd.IPhoneOperator import IPhoneOperator


class AndroidOperator(IPhoneOperator):
    @staticmethod
    def isDeviceConnect():
        """
        检查device是否连接成功
        :return: True 已经连接成功
        """
        return AdbUtil.isDeviceConnect()

    @staticmethod
    def getDeviceId():
        """
        获取设备唯一标识
        :return: 设备唯一标识
        """
        # sn
        out, err = ShellUtil.exec("adb shell getprop ro.serialno")
        if out:
            return out
        # imei
        out, err = ShellUtil.exec('''adb shell "service call iphonesubinfo 1 | cut -c 52-66 | tr -d '.[:space:]'"''')
        if out:
            return out
        return None

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        pass
