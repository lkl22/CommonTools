# -*- coding: utf-8 -*-
# python 3.x
# Filename: ReUtil.py
# 定义一个ReUtil工具类实现正则相关的功能
import re

from util.LogUtil import *

TAG = 'ReUtil'


class ReUtil:
    @staticmethod
    def isMatch(pattern, string, flags=0):
        """
        正则匹配查找字符串
        :param pattern: 正则表达式
        :param string: 需要匹配的str
        :param flags: 正则flags
        :return: True match
        """
        try:
            m = ReUtil.match(pattern, string, flags)
            if m:
                return True
            else:
                return False
        except Exception as err:
            LogUtil.e(TAG, 'isMatch 错误信息：', err)
            return False

    @staticmethod
    def match(pattern, string, flags=0):
        """
        正则匹配查找字符串
        :param string: 需要匹配的str
        :param pattern: 正则表达式
        :param flags: 正则flags
        :return: True match
        """
        try:
            return re.match(f"^{pattern}$", string, flags)
        except Exception as err:
            LogUtil.e(TAG, 'match 错误信息：', err)
            return None

    @staticmethod
    def isMatchMore(patternList=[], string=None, flags=0):
        """
        正则匹配查找字符串
        :param patternList: 正则表达式列表
        :param string: 需要匹配的str
        :param flags: 正则flags
        :return: True match one
        """
        for pattern in patternList:
            if ReUtil.isMatch(pattern=pattern, string=string, flags=flags):
                LogUtil.d("ReUtil -> matchMore: ", "%s is match %s" % (string, pattern))
                return True
        return False

    @staticmethod
    def isMatchColor(string):
        """
        校验颜色值
        :param string: 颜色格式的字符串
        :return: true 正确的颜色值
        """
        patternStr = '#{0,1}(([0-9a-fA-F]{3})|([0-9a-fA-F]{6})|([0-9a-fA-F]{8}))'
        return ReUtil.isMatch(pattern=patternStr, string=string)


if __name__ == "__main__":
    print(ReUtil.isMatch(pattern=".*xml", string="True.xml"))
    print(ReUtil.isMatch(pattern=".xml", string="True.xml"))
    print(ReUtil.isMatch(pattern="True.xml", string="True.xml77"))

    print(ReUtil.isMatchMore(patternList=["True.xml2", ".*xml"], string="True.xml"))

    print(ReUtil.isMatchColor('fff'))
    print(ReUtil.isMatchColor('ffffff'))
    print(ReUtil.isMatchColor('ffffffff'))
    print(ReUtil.isMatchColor('#fff'))
    print(ReUtil.isMatchColor('#ffFff9'))
    print(ReUtil.isMatchColor('#ffFfddff'))
    print(ReUtil.isMatchColor('#f'))
    print(ReUtil.isMatchColor('ffFgff'))
    print(ReUtil.isMatchColor('ffFfff2'))
