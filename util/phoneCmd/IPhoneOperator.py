# -*- coding: utf-8 -*-
# python 3.x
# Filename: IPhoneOperator.py
# 定义一个IPhoneOperator接口类定义phone cmd相关的接口

from abc import ABCMeta, abstractmethod


class IPhoneOperator(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def isDeviceConnect():
        """
        检查device是否连接成功
        :return: True 已经连接成功
        """
        pass

    @staticmethod
    @abstractmethod
    def getDeviceId():
        """
        获取设备唯一标识
        :return: 设备唯一标识
        """
        pass

    @staticmethod
    @abstractmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        pass
