# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelOperator.py
# 定义一个ExcelOperator工具类实现Excel相关的功能
import os

from util.LogUtil import *
from util.excel.IExcelOperator import IExcelOperator
from util.excel.Excel2003Operator import Excel2003Operator
from util.excel.Excel2007Operator import Excel2007Operator


class ExcelOperator:
    @staticmethod
    def getExcelData(fp, sheetName, colKeys=None, primaryKey=None, filterRules={}):
        _, fileExt = os.path.splitext(fp)
        operator: IExcelOperator
        if fileExt == '.xls':
            operator = Excel2003Operator()
        elif fileExt == '.xlsx':
            operator = Excel2007Operator()
        else:
            LogUtil.e('getExcelData', 'not support file ext: ', fileExt)
            return None
        bk = operator.getBook(fp)
        sheet = operator.getSheetByName(bk, sheetName)
        rows = operator.getRows(sheet)
        cols = operator.getColumns(sheet)
        LogUtil.d(f"Excel {fp} {sheetName}", 'rows: ', rows, 'cols: ', cols)
        pass


if __name__ == "__main__":
    LogUtil.d(ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/res/values/AndroidRes.xls", 'color'))

    # LogUtil.d(ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx", '考试信息'))
