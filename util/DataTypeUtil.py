# -*- coding: utf-8 -*-
# python 3.x
# Filename: DataTypeUtil.py
# 定义一个DataTypeUtil工具类实现数据内型相关的功能


class DataTypeUtil:
    INT = 1
    BOOL = 2
    FLOAT = 3
    STR = 4
    LIST = 5
    DICT = 6
    UNKNOWN = 7

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

    @staticmethod
    def type(data):
        if DataTypeUtil.isInt(data):
            return DataTypeUtil.INT
        elif DataTypeUtil.isBool(data):
            return DataTypeUtil.BOOL
        elif DataTypeUtil.isFloat(data):
            return DataTypeUtil.FLOAT
        elif DataTypeUtil.isStr(data):
            return DataTypeUtil.STR
        elif DataTypeUtil.isList(data):
            return DataTypeUtil.LIST
        elif DataTypeUtil.isDict(data):
            return DataTypeUtil.DICT
        else:
            return DataTypeUtil.UNKNOWN

    @staticmethod
    def parseByType(data, dataType):
        if dataType == DataTypeUtil.INT:
            return int(data)
        elif dataType == DataTypeUtil.FLOAT:
            return float(data)
        elif dataType == DataTypeUtil.BOOL:
            if "False" == data or "false" == data or "N" == data or "n" == data:
                return False
            else:
                return data
        elif dataType == DataTypeUtil.STR:
            return str(data)
        else:
            return None


# if __name__ == "__main__":
#     print(DataTypeUtil.isInt(1))
#     print(DataTypeUtil.isBool(False))
#     print(DataTypeUtil.isFloat(1.0))
#     print(DataTypeUtil.isStr('True'))
#     print(DataTypeUtil.isList(['a', 'b']))
#     print(DataTypeUtil.isDict({'a': 'b'}))
#     print(DataTypeUtil.parseByType("False", DataTypeUtil.BOOL))
#     print(DataTypeUtil.parseByType("12", DataTypeUtil.INT))
#     print(DataTypeUtil.parseByType("255.789", DataTypeUtil.FLOAT))
