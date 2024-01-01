# -*- coding: utf-8 -*-
# python 3.x
# Filename: PhoneOperator.py
# 定义一个PhoneOperator接口类定义phone cmd相关的接口

from abc import ABCMeta, abstractmethod


class PhoneOperator:
    @staticmethod
    def connectDevice():
        """
        连接设备
        @return PhoneOperator 连接上了设备后对应的操作类，None 未连接
        """
        pass

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        pass
