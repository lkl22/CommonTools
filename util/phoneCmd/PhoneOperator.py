# -*- coding: utf-8 -*-
# python 3.x
# Filename: PhoneOperator.py
# 定义一个PhoneOperator接口类定义phone cmd相关的接口
from util.phoneCmd.AndroidOperator import AndroidOperator
from util.phoneCmd.HarmonyOperator import HarmonyOperator

TAG = 'PhoneOperator'


class PhoneOperator:
    @staticmethod
    def __connectDevice():
        """
        连接设备
        @return PhoneOperator 连接上了设备后对应的操作类，None 未连接
        """
        if AndroidOperator.isDeviceConnect():
            return AndroidOperator
        if HarmonyOperator.isDeviceConnect():
            return HarmonyOperator
        return None

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        operator = PhoneOperator.__connectDevice()
        if not operator:
            return '未连接手机或者指令连接手机失败'
        operator.clearPhoneLog()
        return None

    @staticmethod
    def captureRealTimeLogs(pathPre: str):
        """
        实时抓取手机日志到指定文件
        @param pathPre 文件路径前缀
        """
        operator = PhoneOperator.__connectDevice()
        if not operator:
            return '未连接手机或者指令连接手机失败'
        operator.restartServer()
        operator.captureRealTimeLogs(pathPre)
        return None

    @staticmethod
    def restartServer():
        """
        重启服务
        """
        operator = PhoneOperator.__connectDevice()
        if not operator:
            return '未连接手机或者指令连接手机失败'
        operator.restartServer()
        return None


if __name__ == "__main__":
    print(PhoneOperator.clearPhoneLog())
