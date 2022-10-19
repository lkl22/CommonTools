# -*- coding: utf-8 -*-
# python 3.x
# Filename: StrUtil.py
# 定义一个StrUtil工具类实现字符串操作相关的功能
from util.LogUtil import *


class StrUtil:
    @staticmethod
    def capitalize(data: str):
        """
        将字符串的首字母大写，其余字母大小写不变
        :param data: data
        :return: value
        """
        if not data:
            return ""
        return data[0].upper() + data[1:]

    @staticmethod
    def decapitalize(data: str):
        """
        将字符串的首字母小写，其余字母大小写不变
        :param data: data
        :return: value
        """
        if not data:
            return ""
        return data[0].lower() + data[1:]


if __name__ == "__main__":
    LogUtil.d(StrUtil.capitalize("thank"))
    LogUtil.d(StrUtil.decapitalize("THANK"))

    LogUtil.d(StrUtil.capitalize("t"))
    LogUtil.d(StrUtil.decapitalize("T"))

    LogUtil.d(StrUtil.capitalize(""))
    LogUtil.d(StrUtil.decapitalize(""))
