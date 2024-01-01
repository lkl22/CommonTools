# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidOperator.py
# 定义一个AndroidOperator工具类实现android cmd相关的功能

from util.phoneCmd.IPhoneOperator import IPhoneOperator


class AndroidOperator(IPhoneOperator):
    @staticmethod
    def connectDevice():
        """
        连接设备
        @return IPhoneOperator 连接上了设备后对应的操作类，None 未连接
        """
        pass

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        pass
