# -*- coding: utf-8 -*-
# python 3.x
# Filename: UpdateExcelWidget.py
# 定义一个UpdateExcelWidget窗口类实现更新Excel内容相关功能
import sys

from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.WidgetUtil import *
from util.excel.ExcelOperator import ExcelOperator, KEY_HEADER_INDEX, KEY_SHEET_NAME, KEY_HEADERS, KEY_COL_TITLE, \
    KEY_SOURCE_KEY
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.CommonTableView import CommonTableView
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'UpdateExcelWidget'
KEY_UPDATE_COL_CFG = 'updateColCfg'
DST_COL_HEADERS = {KEY_COL_TITLE: {KEY_TITLE: "列Title"}, KEY_SOURCE_KEY: {KEY_TITLE: "数据源中对应的Key"},
                   KEY_DEFAULT: {KEY_TITLE: "默认值"}}


class UpdateExcelWidget(ICommonWidget):
    def __init__(self, label=None, data=None, toolTip=None, isDebug=False):
        super(UpdateExcelWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__isDebug = isDebug
        self.__data = None
        self.__headers = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(0, 0, 0, 0))
        box = WidgetUtil.createGroupBox(self, title=label)
        vLayout.addWidget(box)

        vbox = WidgetUtil.createVBoxLayout(box)
        self.__fpWidget = DragInputWidget(label='请选择Excel文件',
                                          fileParam={KEY_CAPTION: '选择Excel文件', KEY_FILTER: '*.xls;*.xlsx'},
                                          required=True)
        vbox.addWidget(self.__fpWidget)

        splitter = WidgetUtil.createSplitter(self)
        self.__sheetNameWidget = CommonLineEdit(label='表名')
        splitter.addWidget(self.__sheetNameWidget)
        self.__headerRowWidget = CommonSpinBox(label='Title行', minValue=1, maxValue=10, prefix='第 ', suffix=' 行')
        splitter.addWidget(self.__headerRowWidget)
        splitter.addWidget(WidgetUtil.createPushButton(self, text='Get',
                                                       toolTip='获取Title信息，展示在下方，可以选择需要提取出来的数据列',
                                                       onClicked=self.__getHeader))
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__primaryComboBox = CommonComboBox(label='选择主键',
                                                toolTip='从Title中选择一列数据作为从数据源中获取更新数据的key，无法下拉选择，请先点击Get按钮获取Title信息',
                                                required=True)
        hbox.addWidget(self.__primaryComboBox, 2)
        vbox.addLayout(hbox)

        self.__colCfgTableView = CommonTableView(addBtnTxt="添加表列信息", headers=DST_COL_HEADERS, items=[],
                                                 addOrEditItemFunc=self.__addOrEditDstCol,
                                                 toolTip='输出Excel中列信息，设置列Title，默认值，映射的源Excel内容')

        vbox.addWidget(self.__colCfgTableView)
        self.__updateContent(data)
        self.setAutoFillBackground(True)

        self.setToolTip(toolTip)
        # 调用Drops方法
        self.setAcceptDrops(True)
        pass

    def __getHeader(self):
        fp, sheetName, headerRow = self.__checkConfig()
        if not fp:
            return
        LogUtil.d(TAG, '__getHeader', fp, 'sheetName', sheetName, 'titleRow', headerRow)
        res = ExcelOperator.getExcelHeaderData(fp, sheetName, headerRow - 1)
        if type(res) == str:
            WidgetUtil.showErrorDialog(message=f"配置不正确。（{res}）")
            return
        LogUtil.d(TAG, '__getHeader', res)
        primaryKey = DictUtil.get(self.__data, KEY_PRIMARY, '')
        self.__data[KEY_HEADERS] = res
        self.__headers = res
        self.__primaryComboBox.updateData(default=primaryKey, groupList=['', *res])
        pass

    def __checkConfig(self):
        srcFp = self.__fpWidget.getData()
        if not srcFp:
            WidgetUtil.showErrorDialog(message="请选择Excel文件")
            return None, None, None
        if not FileUtil.existsFile(srcFp):
            WidgetUtil.showErrorDialog(message="选择的Excel文件已经不存在了，请重新选择")
            return None, None, None
        srcSheetName = self.__sheetNameWidget.getData()
        if not srcSheetName:
            WidgetUtil.showErrorDialog(message="请输入Excel文件里要处理的表名")
            return None, None, None
        srcHeaderRow = self.__headerRowWidget.getData()
        return srcFp, srcSheetName, srcHeaderRow

    def __updateContent(self, data):
        self.__data = data if data else {}
        headers = DictUtil.get(self.__data, KEY_HEADERS, [])
        self.__fpWidget.updateData(DictUtil.get(self.__data, KEY_FILE_PATH))
        self.__sheetNameWidget.updateData(DictUtil.get(self.__data, KEY_SHEET_NAME, 'Sheet1'))
        self.__headerRowWidget.updateData(DictUtil.get(self.__data, KEY_HEADER_INDEX, 1))
        self.__primaryComboBox.updateData(default=DictUtil.get(self.__data, KEY_PRIMARY),
                                          groupList=['', *headers])
        self.__colCfgTableView.updateData(items=DictUtil.get(self.__data, KEY_UPDATE_COL_CFG))
        pass

    def __addOrEditDstCol(self, callback, default=None, items=None, isAdd=False):
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑列配置信息',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_COL_TITLE,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '列名：',
                                           KEY_TOOL_TIP: '请输入列名',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_SOURCE_KEY,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '数据源中对应的Key',
                                           KEY_IS_OPTIONAL: True,
                                           KEY_TOOL_TIP: '数据源中对应的Key，从数据源中获取数据填充表格'
                                       }, {
                                           KEY_ITEM_KEY: KEY_DEFAULT,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '数据默认值',
                                           KEY_IS_OPTIONAL: True,
                                           KEY_TOOL_TIP: '数据默认值，数据源中通过key找不到时使用默认值填充'
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isAdd=isAdd,
                                       labelWidth=150,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def updateData(self, data):
        self.__updateContent(data)
        pass

    def getData(self):
        srcFp, srcSheetName, srcHeaderRow = self.__checkConfig()
        if not srcFp:
            return None
        primaryColName = self.__primaryComboBox.getData()
        if not primaryColName:
            WidgetUtil.showErrorDialog(message="请选择作为数据源中查找的key数据对应的列")
            return None
        self.__data = {
            KEY_FILE_PATH: self.__fpWidget.getData(),
            KEY_SHEET_NAME: self.__sheetNameWidget.getData(),
            KEY_HEADER_INDEX: self.__headerRowWidget.getData(),
            KEY_PRIMARY: self.__primaryComboBox.getData(),
            KEY_HEADERS: self.__headers if self.__headers else [],
            KEY_UPDATE_COL_CFG: self.__colCfgTableView.getData()
        }
        return self.__data

    def updateExcel(self, sourceData={}):
        fp = DictUtil.get(self.__data, KEY_FILE_PATH)
        sheetName = DictUtil.get(self.__data, KEY_SHEET_NAME)
        titleIndex = DictUtil.get(self.__data, KEY_HEADER_INDEX)
        primary = DictUtil.get(self.__data, KEY_PRIMARY)
        colCfgs = DictUtil.get(self.__data, KEY_UPDATE_COL_CFG)
        return ExcelOperator.updateExcel(fp=fp, sheetName=sheetName, titleIndex=titleIndex - 1, primaryTitle=primary,
                                         updateCols=colCfgs, data=sourceData)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = UpdateExcelWidget(label='源Excel相关配置', toolTip="test toolTip")
    e = UpdateExcelWidget(label='源Excel相关配置', data={
        KEY_FILE_PATH: 'D:/Projects/Python/CommonTools/widget/harmony/test/testData.xlsx'
    }, toolTip="test toolTip", isDebug=True)
    e.show()
    sys.exit(app.exec_())
