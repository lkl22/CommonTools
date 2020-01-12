# -*- coding: utf-8 -*-
# python 3.x
# Filename: DataTypeUtil.py
# 定义一个DataTypeUtil工具类实现数据内型相关的功能
class DataTypeUtil:
    @staticmethod
    def isDict(data):
        try:
            return type(data) == dict
        except SyntaxError as err:
            print("%s" % err)
            return False

    @staticmethod
    def isList(data):
        try:
            return type(data) == list
        except SyntaxError as err:
            print("%s" % err)
            return False

    @staticmethod
    def isInt(data):
        try:
            return type(data) == int
        except SyntaxError as err:
            print("%s" % err)
            return False

    @staticmethod
    def isBool(data):
        try:
            return type(data) == bool
        except SyntaxError as err:
            print("%s" % err)
            return False

    @staticmethod
    def isFloat(data):
        try:
            return type(data) == float
        except SyntaxError as err:
            print("%s" % err)
            return False

    @staticmethod
    def isStr(data):
        try:
            return type(data) == str
        except SyntaxError as err:
            print("%s" % err)
            return False


if __name__ == "__main__":
    print(DataTypeUtil.isInt(1))
    print(DataTypeUtil.isBool(False))
    print(DataTypeUtil.isFloat(1.0))
    print(DataTypeUtil.isStr('True'))
    print(DataTypeUtil.isList(['a', 'b']))
    print(DataTypeUtil.isDict({'a': 'b'}))

