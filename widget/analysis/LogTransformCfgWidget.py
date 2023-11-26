# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogTransformCfgWidget.py.py
# 定义一个LogTransformCfgWidget窗口类实现日志结果转换配置的功能

import sys

from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTableView import CommonTableView
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'LogTransformCfgWidget'

HEADERS = {
    KEY_ITEM_KEY: {KEY_TITLE: "字典key"}, KEY_FUNCTION: {KEY_TITLE: "执行函数"}
}


class LogTransformCfgWidget(ICommonWidget):
    def __init__(self, value=None, isEnable=True, maxWidth=None, toolTip=None, isDebug=False):
        super(LogTransformCfgWidget, self).__init__()
        self.__value = {}
        self.__isDebug = isDebug

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__keywordLineEdit = CommonLineEdit(label='日志关键字', toolTip='主要用于查找需要处理的日志行，可以配置多条，使用英文分号;间隔')
        hbox.addWidget(self.__keywordLineEdit, 1)
        self.__funcLineEdit = CommonLineEdit(label='日志处理函数',
                                             toolTip='执行指定的代码，将查找到的log行做为入参text，出参res（将处理结果转为字典格式的数据，以便进一步处理）')
        hbox.addWidget(self.__funcLineEdit, 3)
        vbox.addLayout(hbox)

        self.__transformFuncsTableView = CommonTableView(addBtnTxt="添加结果处理函数", headers=HEADERS, items=[],
                                                         addOrEditItemFunc=self.__addOrEditItemFunc)
        vbox.addWidget(self.__transformFuncsTableView, 1)

        vbox.addLayout(hbox)

        self.updateData(value)
        self.setEnabled(isEnable)
        if maxWidth:
            self.setMaximumWidth(maxWidth)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __addOrEditItemFunc(self, callback, default, items):
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑结果映射',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_ITEM_KEY,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: 'Key：',
                                           KEY_TOOL_TIP: '请输入log处理结果字典中对应的key',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_FUNCTION,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '需要执行的代码',
                                           KEY_TOOL_TIP: '从处理结果中取出对应的数据，做为输入参数 text，执行完输出结果到res中'
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __updateUi(self):
        self.__keywordLineEdit.updateData(DictUtil.get(self.__value, KEY_LOG_KEYWORD))
        self.__funcLineEdit.updateData(DictUtil.get(self.__value, KEY_FUNCTION))
        self.__transformFuncsTableView.updateData(DictUtil.get(self.__value, KEY_TRANSFORM_FUNCS))
        # self.adjustSize()
        pass

    def updateData(self, value):
        self.__value = value
        self.__updateUi()
        pass

    def getData(self):
        return {
            KEY_LOG_KEYWORD: self.__keywordLineEdit.getData(),
            KEY_FUNCTION: self.__funcLineEdit.getData(),
            KEY_TRANSFORM_FUNCS: self.__transformFuncsTableView.getData(),
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = LogTransformCfgWidget(
        toolTip='dddddd')
    e.show()
    LogUtil.d(TAG, e.getData())
    sys.exit(app.exec_())
