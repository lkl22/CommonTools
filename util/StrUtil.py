# -*- coding: utf-8 -*-
# python 3.x
# Filename: StrUtil.py
# 定义一个StrUtil工具类实现字符串操作相关的功能

import re
import chardet
from util.LogUtil import *

TAG = 'StrUtil'


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

    @staticmethod
    def containsStr(srcStr: str, dataList: []):
        """
        判断字符串中是否包含指定列表中的数据
        :param srcStr: 源字符串
        :param dataList: 要判断的字符串列表
        :return: True 包含任意一个数据 False 一个都不包含
        """
        isContains = False
        for data in dataList:
            if data in srcStr:
                isContains = True
                break
        return isContains

    @staticmethod
    def decode(data):
        """
        将字节转为字符串
        :param data: 源字节串
        :return: 解码后到字符串
        """
        if not data:
            return ''
        try:
            return data.decode()
        except Exception as e:
            LogUtil.e(TAG, 'decode 错误信息：', e)
        try:
            return data.decode('gbk')
        except Exception as e:
            LogUtil.e(TAG, 'decode 错误信息：', e)
        return ''

    @staticmethod
    def detectEncoding(data):
        result = chardet.detect(data)
        # 编码格式
        encoding = result['encoding']
        # 可信度
        confidence = result['confidence']
        return encoding, confidence

    @staticmethod
    def camel2under(data: str):
        return re.sub(r'(?!^)([A-Z]+)', r'_\1', data).upper()

    @staticmethod
    def under2camel(data):
        return StrUtil.decapitalize(''.join([_.capitalize() for _ in data.split('_')]))


if __name__ == "__main__":
    # LogUtil.d(StrUtil.capitalize("thank"))
    # LogUtil.d(StrUtil.decapitalize("THANK"))
    #
    # LogUtil.d(StrUtil.capitalize("t"))
    # LogUtil.d(StrUtil.decapitalize("T"))
    #
    # LogUtil.d(StrUtil.capitalize(""))
    # LogUtil.d(StrUtil.decapitalize(""))

    LogUtil.d(StrUtil.camel2under("helloWordLi"))
    LogUtil.d(StrUtil.under2camel("HELLO_WORD_LI"))
