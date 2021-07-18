# -*- coding: utf-8 -*-
# python 3.x
# Filename: ReUtil.py
# 定义一个ReUtil工具类实现正则相关的功能
import re
from util.LogUtil import *


class ReUtil:
    @staticmethod
    def match(string, patternStr):
        """
        正则匹配查找字符串
        :param string: 需要匹配的str
        :param patternStr: 正则表达式
        :return: True match
        """
        try:
            pattern = re.compile("^%s$" % patternStr)
            m = pattern.match(string)
            if m:
                return True
            else:
                return False
        except Exception as err:
            LogUtil.e('match 错误信息：', err)
            return False

    @staticmethod
    def matchMore(string, patternList=[]):
        """
        正则匹配查找字符串
        :param string: 需要匹配的str
        :param patternList: 正则表达式列表
        :return: True match one
        """
        for patternStr in patternList:
            if ReUtil.match(string, patternStr):
                LogUtil.d("ReUtil -> matchMore: ", "%s is match %s" % (string, patternStr))
                return True
        return False

    @staticmethod
    def matchColor(string):
        """
        校验颜色值
        :param string: 颜色格式的字符串
        :return: true 正确的颜色值
        """
        patternStr = '#{0,1}(([0-9a-fA-F]{3})|([0-9a-fA-F]{6})|([0-9a-fA-F]{8}))'
        return ReUtil.match(string, patternStr)

# if __name__ == "__main__":
#     print(ReUtil.match("True.xml", ".*xml"))
#     print(ReUtil.match("True.xml", ".xml"))
#     print(ReUtil.match("True.xml77", "True.xml"))
#
#     print(ReUtil.matchMore("True.xml", ["True.xml2", ".*xml"]))

#     print(ReUtil.matchColor('fff'))
#     print(ReUtil.matchColor('ffffff'))
#     print(ReUtil.matchColor('ffffffff'))
#     print(ReUtil.matchColor('#fff'))
#     print(ReUtil.matchColor('#ffFff9'))
#     print(ReUtil.matchColor('#ffFfddff'))
#     print(ReUtil.matchColor('#f'))
#     print(ReUtil.matchColor('ffFgff'))
#     print(ReUtil.matchColor('ffFfff2'))

