# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyOperator.py
# 定义一个HarmonyOperator工具类实现harmony cmd相关的功能

from util.phoneCmd.IPhoneOperator import IPhoneOperator


class HarmonyOperator(IPhoneOperator):
    @staticmethod
    def isDeviceConnect():
        """
        检查device是否连接成功
        :return: True 已经连接成功
        """
        pass

    @staticmethod
    def getDeviceId():
        """
        获取设备唯一标识
        :return: 设备唯一标识
        """
        pass

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        pass
