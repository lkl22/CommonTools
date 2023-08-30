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
    def saveToExcel(fp, sheetName, keys: [], data: [{}]):
        if not keys or not data:
            LogUtil.e('saveToExcel', 'no data add to excel')
            return False
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
            LogUtil.e('saveToExcel', 'not support file ext: ', fileExt)
            return None
        keyMap = {}
        for index, key in enumerate(keys):
            keyMap[key] = index + indexOffset
        bk = operator.createBook()
        sheet = operator.addSheet(bk, sheetName)
        for row, rowItem in enumerate(data):
            for key, item in rowItem.items():
                operator.writeSheet(sheet, row + indexOffset, keyMap[key], item['value'])
        operator.saveBook(bk, fp)
        return True

    @staticmethod
    def __getFilterData(operator, sheet, rows, cols, indexOffset, extendInfo):
        """
        根据filter规则过滤需要的数据
        :param operator: Excel操作类
        :param sheet: sheet表数据
        :param rows: 行数
        :param cols: 列数
        :param indexOffset: index偏移
        :param extendInfo: 扩展信息
        :return: 获取满足指定条件的数据
        """
        titleIndex = DictUtil.get(extendInfo, KEY_TITLE_INDEX, 0)
        colKeys = DictUtil.get(extendInfo, KEY_COL_KEYS, None)
        primaryKey = DictUtil.get(extendInfo, KEY_PRIMARY_KEY, None)
        filterRules = DictUtil.get(extendInfo, KEY_FILTER_RULES, [])
        LogUtil.i(f"__getFilterData titleIndex: {titleIndex} primaryKey: {primaryKey} filterRules: {filterRules}")
        colKeyMap = {}
        primaryIndex = -1
        hasColKeys = True if colKeys else False
        for col in range(indexOffset, cols + indexOffset):
            colKey = operator.getCell(sheet, titleIndex + indexOffset, col)
            if primaryKey and primaryKey == colKey:
                primaryIndex = col
            if hasColKeys:
                if colKey in colKeys:
                    colKeyMap[colKey] = col
            else:
                colKeyMap[colKey] = col
        LogUtil.i(f"__getFilterData primaryIndex: {primaryIndex} colKeyMap: {colKeyMap}")
        result = {}
        for row in range(titleIndex + indexOffset + 1, rows + indexOffset):
            primaryValue = operator.getCell(sheet, row, primaryIndex) if primaryIndex > -1 else row
            rowData = {}
            ignoreRow = False
            for key, col in colKeyMap.items():
                value = operator.getCell(sheet, row, col)
                if key in filterRules.keys():
                    if value not in filterRules[key]:
                        ignoreRow = True
                        break
                rowData[key] = value
            if not ignoreRow:
                result[primaryValue] = rowData
        return result

    @staticmethod
    def __getAllData(operator, sheet, rows, cols, indexOffset):
        """
        获取所有数据
        :param operator: Excel操作类
        :param sheet: sheet表数据
        :param rows: 行数
        :param cols: 列数
        :param indexOffset: index偏移
        :return: 表格里所有数据
        """
        res = []
        for row in range(indexOffset, rows + indexOffset):
            rowData = []
            for col in range(indexOffset, cols + indexOffset):
                rowData.append(operator.getCell(sheet, row, col))
            res.append(rowData)
        return res


if __name__ == "__main__":
    # LogUtil.d(ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/res/values/AndroidRes.xls", 'color',
    #                                      {KEY_TITLE_INDEX: 0, KEY_COL_KEYS: ['key', 'normal', 'dark'],
    #                                       KEY_PRIMARY_KEY: 'key',
    #                                       KEY_FILTER_RULES: {'dark': ['', '#000000', '#43CDF9'],
    #                                                          'normal': ['#6633B5E5', '#1CA9F2']}}))
    #
    # LogUtil.d(
    #     ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx", '单选题',
    #                                {KEY_TITLE_INDEX: 0, KEY_COL_KEYS: ['题干', '答案', '选项A'],
    #                                 KEY_PRIMARY_KEY: '题干',
    #                                 KEY_FILTER_RULES: {'答案': ['A', 'C']}}))
    ExcelOperator.saveToExcel('./test.xlsx', '11', ['key', 'normal', 'dark'],
                              [{'key': {'value': 'key'}, 'normal': {'value': 'normal'}, 'dark': {'value': 'dark'}},
                               {'key': {'value': 'sdd'}, 'normal': {'value': '#ffddffff'}, 'dark': {'value': '#000dd000'}}, ])
