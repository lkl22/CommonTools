# -*- coding: utf-8 -*-
# python 3.x
# Filename: IExcelOperator.py
# 定义一个IExcelOperator接口类定义Excel相关的接口

from abc import ABCMeta, abstractmethod

KEY_BG_COLOR = 'backgroundColor'
KEY_FORMAT = 'format'
KEY_VALUE = 'value'


class IExcelOperator(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def getBook(filePath):
        """
        获取工作簿
        :param filePath: 文件路径
        :return: 工作簿
        """
        pass

    @staticmethod
    @abstractmethod
    def getSheetByName(bk, sheetName='考试信息'):
        """
        获取指定索引的sheet的内容
        :param bk: Book
        :param sheetName: sheet表的名字
        :return: sheet的内容
        """
        pass

    @staticmethod
    @abstractmethod
    def getRows(st):
        """
        获取excel行数
        :param st: sheet
        :return: 行数
        """
        pass

    @staticmethod
    @abstractmethod
    def getColumns(st):
        """
        获取excel列数
        :param st: sheet
        :return: 列数
        """
        pass

    @staticmethod
    @abstractmethod
    def getCell(st, row, col):
        """
        获取指定单元格内容
        :param st: sheet
        :param row: 行数
        :param col: 列数
        :return: 单元格内容
        """
        pass

    @staticmethod
    @abstractmethod
    def createBook():
        """
        创建Excel工作薄
        :return: Excel工作薄
        """
        pass

    @staticmethod
    @abstractmethod
    def addSheet(bk, sheetName):
        """
        添加Excel工作表
        :param bk: Workbook
        :param sheetName: sheetName
        :return: Worksheet
        """
        pass

    @staticmethod
    @abstractmethod
    def writeSheet(st, row, col, value, cellFormat):
        """
        写入数据
        :param st: Worksheet
        :param row: 行数
        :param col: 列数
        :param value: 内容
        :param cellFormat: 单元格格式
        """
        pass

    @staticmethod
    @abstractmethod
    def saveBook(bk, fileName):
        """
        保存Excel工作薄
        :param bk: Workbook
        :param fileName: 文件名
        """
        pass

