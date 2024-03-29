# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelOperator.py
# 定义一个ExcelOperator工具类实现Excel相关的功能
import os

from constant.WidgetConst import KEY_PRIMARY, KEY_DEFAULT
from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.LogUtil import *
from util.excel.Excel2003Operator import Excel2003Operator
from util.excel.Excel2007Operator import Excel2007Operator
from util.excel.IExcelOperator import IExcelOperator, KEY_VALUE, KEY_FORMAT, KEY_BG_COLOR

KEY_SHEET_NAME = 'sheetName'
# header数据
KEY_HEADERS = 'headers'
KEY_HEADER_INDEX = 'headerIndex'
# 需要选择的列header key列表
KEY_SELECT_COL_KEYS = 'selectColKeys'
KEY_FILTER_RULES = 'filterRules'

KEY_COL_TITLE = 'colTitle'
KEY_SOURCE_KEY = 'sourceKey'


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
    def getExcelHeaderData(fp, sheetName, headerRow):
        """
        获取Excel指定表格header数据
        :param fp: Excel文件路径
        :param sheetName: 表名
        :param headerRow: header所在的行
        :return: header数据
        """
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
            return 'File ext error.'
        bk = operator.getBook(fp)
        if not bk:
            return 'File is not book'
        sheet = operator.getSheetByName(bk, sheetName)
        if not sheet:
            return 'sheet name is error'
        rows = operator.getRows(sheet)
        cols = operator.getColumns(sheet)
        LogUtil.d(f"Excel {fp} sheetName: {sheetName}", 'rows: ', rows, 'cols: ', cols, 'indexOffset: ', indexOffset)
        res = []
        for col in range(indexOffset, cols + indexOffset):
            res.append(operator.getCell(sheet, indexOffset + headerRow, col))
        return res

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
        bk = operator.createBook()
        sheet = operator.addSheet(bk, sheetName)

        keyMap = {}
        for index, key in enumerate(keys):
            keyMap[key] = index + indexOffset
            operator.writeSheet(sheet, indexOffset, index + indexOffset, key)
        for row, rowItem in enumerate(data):
            for key, item in rowItem.items():
                if key in keyMap:
                    operator.writeSheet(sheet, row + indexOffset + 1, keyMap[key], DictUtil.get(item, KEY_VALUE, ''),
                                        DictUtil.get(item, KEY_FORMAT, None))
        operator.saveBook(bk, fp)
        return True

    @staticmethod
    def updateExcel(fp, sheetName, titleIndex, primaryTitle, updateCols: [], data: {}):
        if not updateCols or not data or not primaryTitle:
            LogUtil.e('updateExcel', 'no data need add to excel.')
            return False
        fileName, fileExt = os.path.splitext(fp)
        operator: IExcelOperator
        indexOffset = 0
        if fileExt == '.xls':
            operator = Excel2003Operator()
        elif fileExt == '.xlsx':
            operator = Excel2007Operator()
            # xlsx的下标从1开始
            indexOffset = 1
        else:
            LogUtil.e('updateExcel', 'not support file ext: ', fileExt)
            return False
        bk = operator.getBook(fp)
        if not bk:
            return False
        sheet = operator.getSheetByName(bk, sheetName)
        if not sheet:
            LogUtil.e('updateExcel', 'not support file ext: ', fileExt)
            return False
        rows = operator.getRows(sheet)
        cols = operator.getColumns(sheet)

        newBk = None
        newSheet = None
        if fileExt == '.xls':
            newBk = operator.createBook()
            newSheet = operator.addSheet(newBk, sheetName=sheetName)
            for row in range(rows):
                for col in range(cols):
                    operator.writeSheet(newSheet, row=row, col=col, value=operator.getCell(st=sheet, row=row, col=col))

        colKeyMap = {}
        primaryIndex = -1
        for col in range(indexOffset, cols + indexOffset):
            cellValue = operator.getCell(sheet, titleIndex + indexOffset, col)
            if primaryTitle == cellValue:
                primaryIndex = col
            colKeyMap[cellValue] = col
        if primaryIndex == -1:
            LogUtil.e('updateExcel', 'not find primary in title row.')
            return False
        newCol = cols + indexOffset
        for updateCol in updateCols:
            if updateCol[KEY_COL_TITLE] not in colKeyMap:
                operator.writeSheet(st=newSheet if newSheet else sheet, row=titleIndex + indexOffset, col=newCol,
                                    value=updateCol[KEY_COL_TITLE])
                colKeyMap[updateCol[KEY_COL_TITLE]] = newCol
                newCol += 1
        LogUtil.e('updateExcel', f'colKeyMap {colKeyMap}')
        for row in range(titleIndex + indexOffset + 1, rows + indexOffset):
            primaryValue = operator.getCell(sheet, row, primaryIndex)
            updateRowData = DictUtil.get(data, primaryValue)
            if not updateRowData:
                continue
            if type(updateRowData) == list:
                for updateCol in updateCols:
                    value = [DictUtil.get(item, updateCol[KEY_SOURCE_KEY], updateCol[KEY_DEFAULT]) for item in
                             updateRowData if updateCol[KEY_SOURCE_KEY] in item]
                    cellData = updateCol[KEY_DEFAULT] if len(value) == 0 else (value[0] if len(value) == 1 else value)
                    col = colKeyMap[updateCol[KEY_COL_TITLE]]
                    operator.writeSheet(st=newSheet if newSheet else sheet, row=row, col=col, value=f"{cellData}")
            elif type(updateRowData) == dict:
                for updateCol in updateCols:
                    value = DictUtil.get(updateRowData, updateCol[KEY_SOURCE_KEY], updateCol[KEY_DEFAULT])
                    col = colKeyMap[updateCol[KEY_COL_TITLE]]
                    operator.writeSheet(st=newSheet if newSheet else sheet, row=row, col=col, value=f"{value}")
        if newBk:
            FileUtil.removeFile(fileName + '_new.xls')
            operator.saveBook(newBk, fileName + '_new.xls')
        else:
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
        :param extendInfo: 扩展信息 KEY_FILTER_RULES 没有不过滤 KEY_PRIMARY 没有，行号作为kay KEY_SELECT_COL_KEYS 没有，获取所有列数据
        :return: 获取满足指定条件的数据
        """
        titleIndex = DictUtil.get(extendInfo, KEY_HEADER_INDEX, 0)
        colKeys = DictUtil.get(extendInfo, KEY_SELECT_COL_KEYS, None)
        primaryKey = DictUtil.get(extendInfo, KEY_PRIMARY, None)
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
    #                                       KEY_PRIMARY: 'key',
    #                                       KEY_FILTER_RULES: {'dark': ['', '#000000', '#43CDF9'],
    #                                                          'normal': ['#6633B5E5', '#1CA9F2']}}))
    #
    # LogUtil.d(
    #     ExcelOperator.getExcelData("/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx", '单选题',
    #                                {KEY_TITLE_INDEX: 0, KEY_COL_KEYS: ['题干', '答案', '选项A'],
    #                                 KEY_PRIMARY: '题干',
    #                                 KEY_FILTER_RULES: {'答案': ['A', 'C']}}))
    ExcelOperator.saveToExcel('./test.xls', '11', ['key', 'normal', 'dark'],
                              [{'key': {KEY_VALUE: 'key', KEY_FORMAT: {KEY_BG_COLOR: 4}},
                                'normal': {KEY_VALUE: 'normal'}, 'dark': {KEY_VALUE: 'dark'}},
                               {'key': {KEY_VALUE: 'sdd'}, 'normal': {KEY_VALUE: '#ffddffff'},
                                'dark': {KEY_VALUE: '#000dd000'}}, ])
