# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelUtil.py
# 定义一个ExcelUtil工具类实现Excel相关的功能

import xlrd
import xlwt
from xlrd import book, sheet
from xlutils.copy import copy
from xlwt import Workbook, Worksheet

from util.LogUtil import *


class ExcelUtil:
    @staticmethod
    def getBook(filePath='../config/androidRes.xls'):
        """
        获取
        :param filePath:
        :return:
        """
        bk = None
        try:
            bk = xlrd.open_workbook(filePath)
        except Exception as err:
            LogUtil.e('ExcelUtil getBook 错误信息：', err)
        return bk

    @staticmethod
    def getSheet(filePath='../config/androidRes.xls', i=0):
        """
        获取指定索引的sheet的内容
        :param filePath: 文件路径
        :param i: 索引
        :return: sheet的内容
        """
        st = None
        try:
            bk = xlrd.open_workbook(filePath)
            st = bk.sheets()[i]
        except Exception as err:
            LogUtil.e('ExcelUtil getSheet 错误信息：', err)
        return st

    @staticmethod
    def getLines(st: sheet):
        """
        获取excel行数
        :param st: sheet
        :return: 行数
        """
        lines = st.nrows
        return lines

    @staticmethod
    def getCell(st: sheet, row, col):
        """
        获取指定单元格内容
        :param st: sheet
        :param row: 行数
        :param col: 列数
        :return: 单元格内容
        """
        value = st.cell(row, col).value.strip()
        return value

    @staticmethod
    def copyBook(bk: book):
        """
        从读book复制一个写book
        :param bk: book
        :return: 写book
        """
        return copy(bk)

    @staticmethod
    def createBook():
        """
        创建Excel工作薄
        :return: Excel工作薄
        """
        return xlwt.Workbook()

    @staticmethod
    def addSheet(bk: Workbook, sheetname):
        """
        添加Excel工作表
        :param bk: Workbook
        :param sheetname: sheetname
        :return: Worksheet
        """
        return bk.add_sheet(sheetname, True)

    @staticmethod
    def writeSheet(st: Worksheet, row, col, value):
        """
        写入数据
        :param st: Worksheet
        :param row: 行数
        :param col: 列数
        :param value: 内容
        """
        st.write(row, col, value)

    @staticmethod
    def saveBook(bk: Workbook, fileName):
        """
        保存Excel工作薄
        :param bk: Workbook
        :param fileName: 文件名
        """
        bk.save(fileName)
