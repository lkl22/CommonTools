# -*- coding: utf-8 -*-
# python 3.x
# Filename: ReadExcelWidget.py
# 定义一个ReadExcelWidget窗口类实现读取Excel内容相关功能
import sys

from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.JsonUtil import JsonUtil
from util.WidgetUtil import *
from util.excel.ExcelOperator import ExcelOperator, KEY_HEADER_INDEX, KEY_SELECT_COL_KEYS, KEY_FILTER_RULES, \
    KEY_SHEET_NAME, KEY_HEADERS
from widget.custom.CommonCheckBoxs import CommonCheckBoxs
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'ReadExcelWidget'


class ReadExcelWidget(ICommonWidget):
    def __init__(self, label=None, data=None, toolTip=None):
        super(ReadExcelWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__data = None
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

        self.__selectHeaderCheckBoxs = CommonCheckBoxs(label='选择需要提取数据的Title')
        vbox.addWidget(self.__selectHeaderCheckBoxs)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__primaryComboBox = CommonComboBox(label='选择主键')
        hbox.addWidget(self.__primaryComboBox, 2)

        self.__filterRulesEdit = CommonLineEdit(label='过滤规则',
                                                toolTip='输入Excel过滤规则。格式如下：{"title1": [value1, value2, value3], "title2": [value1, value2, value3]}')
        hbox.addWidget(self.__filterRulesEdit, 9)
        vbox.addLayout(hbox)

        self.__updateContent(data)
        self.setAutoFillBackground(True)

        self.setToolTip(toolTip)
        # 调用Drops方法
        self.setAcceptDrops(True)
        pass

    def __getHeader(self):
        fp, sheetName, headerRow = self.__checkSrcConfig()
        if not fp:
            return
        LogUtil.d(TAG, '__getHeader', fp, 'sheetName', sheetName, 'titleRow', headerRow)
        res = ExcelOperator.getExcelHeaderData(fp, sheetName, headerRow - 1)
        if type(res) == str:
            WidgetUtil.showErrorDialog(message=f"配置不正确。（{res}）")
            return
        LogUtil.d(TAG, '__getHeader', res)
        srcSelectHeader = DictUtil.get(self.__data, KEY_SELECT_COL_KEYS, [])
        primaryKey = DictUtil.get(self.__data, KEY_PRIMARY, '')
        self.__data[KEY_HEADERS] = res
        self.__selectHeaderCheckBoxs.updateData(groupList=res, defaultValue=srcSelectHeader)
        self.__primaryComboBox.updateData(default=primaryKey, groupList=['', *res])
        pass

    def __checkSrcConfig(self):
        srcFp = self.__fpWidget.getData()
        if not srcFp:
            WidgetUtil.showErrorDialog(message="请选择源Excel文件")
            return None, None, None
        srcSheetName = self.__sheetNameWidget.getData()
        if not srcSheetName:
            WidgetUtil.showErrorDialog(message="请输入源Excel文件里要处理的表名")
            return None, None, None
        srcHeaderRow = self.__headerRowWidget.getData()
        return srcFp, srcSheetName, srcHeaderRow

    def __updateContent(self, data):
        self.__data = data if data else {}
        headers = DictUtil.get(self.__data, KEY_HEADERS, [])
        self.__fpWidget.updateData(DictUtil.get(self.__data, KEY_FILE_PATH))
        self.__sheetNameWidget.updateData(DictUtil.get(self.__data, KEY_SHEET_NAME, 'Sheet1'))
        self.__headerRowWidget.updateData(DictUtil.get(self.__data, KEY_HEADER_INDEX, 1))
        self.__selectHeaderCheckBoxs.updateData(groupList=headers,
                                                defaultValue=DictUtil.get(self.__data, KEY_SELECT_COL_KEYS, []))
        self.__primaryComboBox.updateData(default=DictUtil.get(self.__data, KEY_PRIMARY),
                                          groupList=['', *headers])
        self.__filterRulesEdit.updateData(
            JsonUtil.encode(DictUtil.get(self.__data, KEY_FILTER_RULES, {}), ensureAscii=False, indent=0))
        pass

    def updateData(self, data):
        self.__updateContent(data)
        pass

    def getData(self):
        srcFp, srcSheetName, srcHeaderRow = self.__checkSrcConfig()
        if not srcFp:
            return None
        if not FileUtil.existsFile(srcFp):
            WidgetUtil.showErrorDialog(message="选择的Excel文件已经不存在了，请重新选择")
            return None
        self.__data = {
            KEY_FILE_PATH: self.__fpWidget.getData(),
            KEY_SHEET_NAME: self.__sheetNameWidget.getData(),
            KEY_HEADER_INDEX: self.__headerRowWidget.getData(),
            KEY_HEADERS: self.__selectHeaderCheckBoxs.getGroupData(),
            KEY_SELECT_COL_KEYS: self.__selectHeaderCheckBoxs.getData(),
            KEY_PRIMARY: self.__primaryComboBox.getData(),
            KEY_FILTER_RULES: JsonUtil.decode(self.__filterRulesEdit.getData())
        }
        return self.__data

    def getExcelData(self):
        self.getData()
        srcDatas = ExcelOperator.getExcelData(self.__data[KEY_FILE_PATH], self.__data[KEY_SHEET_NAME], {
            KEY_PRIMARY: self.__data[KEY_PRIMARY],
            KEY_HEADER_INDEX: self.__data[KEY_HEADER_INDEX] - 1,
            KEY_SELECT_COL_KEYS: self.__data[KEY_SELECT_COL_KEYS],
            KEY_FILTER_RULES: self.__data[KEY_FILTER_RULES],
        })
        LogUtil.i(TAG, 'getExcelData', srcDatas)
        return srcDatas


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = ReadExcelWidget(label='源Excel相关配置', toolTip="test toolTip")
    e = ReadExcelWidget(label='源Excel相关配置', data={
        KEY_FILE_PATH: 'D:/Projects/Python/CommonTools/widget/harmony/test/testData.xlsx'
    }, toolTip="test toolTip")
    e.show()
    sys.exit(app.exec_())
