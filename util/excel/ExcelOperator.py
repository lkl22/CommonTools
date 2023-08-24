# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelOperator.py
# 定义一个ExcelOperator工具类实现Excel相关的功能
import os

from util.DictUtil import DictUtil
from util.LogUtil import *
from util.excel.IExcelOperator import IExcelOperator
from util.excel.Excel2003Operator import Excel2003Operator
from util.excel.Excel2007Operator import Excel2007Operator

KEY_TITLE_INDEX = 'titleIndex'
KEY_COL_KEYS = 'colKeys'
KEY_PRIMARY_KEY = 'primaryKey'
KEY_FILTER_RULES = 'filterRules'


class ExcelOperator:
    @staticmethod
    def getExcelData(fp, sheetName, extendInfo=None):
        _, fileExt = os.path.splitext(fp)
        operator: IExcelOperator
        indexOffset = 0
        if fileExt == '.xls':
            operator = Excel2003Operator()
        elif fileExt == '.xlsx':
            operator = Excel2007Operator()
            # xlsx的下标从1开始
            indexOffset = 1
        else:
            LogUtil.e('getExcelData', 'not support file ext: ', fileExt)
            return None
        bk = operator.getBook(fp)
        if not bk:
            return None
        sheet = operator.getSheetByName(bk, sheetName)
        if not sheet:
            return None
        rows = operator.getRows(sheet)
        cols = operator.getColumns(sheet)
        LogUtil.d(f"Excel {fp} sheetName: {sheetName}", 'rows: ', rows, 'cols: ', cols, 'indexOffset: ', indexOffset)
        if extendInfo:
            return ExcelOperator.__getFilterData(operator, sheet, rows, cols, indexOffset, extendInfo)
        else:
            return ExcelOperator.__getAllData(operator, sheet, rows, cols, indexOffset)
        pass

    @staticmethod
    def __getFilterData(operator, sheet, rows, cols, indexOffset, extendInfo):
        titleIndex = DictUtil.get(extendInfo, KEY_TITLE_INDEX, 0)
        colKeys = DictUtil.get(extendInfo, KEY_COL_KEYS, None)
        primaryKey = DictUtil.get(extendInfo, KEY_PRIMARY_KEY, None)
        filterRules = DictUtil.get(extendInfo, KEY_FILTER_RULES, [])
        LogUtil.i(f"__getFilterData titleIndex: {titleIndex} primaryKey: {primaryKey} filterRules: {filterRules}")
        colKeyMap = {}
        hasColKeys = True if colKeys else False
        for col in range(indexOffset, cols + indexOffset):
            colKey = operator.getCell(sheet, titleIndex + indexOffset, col)
            if hasColKeys:
                if colKey in colKeys:
                    colKeyMap[colKey] = col
            else:
                colKeyMap[colKey] = col
        LogUtil.i(f"__getFilterData colKeyMap: {colKeyMap}")
        pass

    @staticmethod
    def __getAllData(operator, sheet, rows, cols, indexOffset):
        res = []
        for row in range(indexOffset, rows + indexOffset):
            rowData = []
            for col in range(indexOffset, cols + indexOffset):
                rowData.append(operator.getCell(sheet, row, col))
            res.append(rowData)
        return res


if __name__ == "__main__":
    LogUtil.d(ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/res/values/AndroidRes.xls", 'color',
                                         {KEY_TITLE_INDEX: 0, KEY_COL_KEYS: ['key', 'dark']}))

    LogUtil.d(
        ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx", '考试信息'))
