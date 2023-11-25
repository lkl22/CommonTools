# -*- coding: utf-8 -*-
# python 3.x
# Filename: SpliceLogParamsWidget.py
# 定义一个SpliceLogParamsWidget窗口类实现日志拼接参数设置控件的功能

import sys

from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonDateTimeFormatEdit'


class SpliceLogParamsWidget(ICommonWidget):
    def __init__(self, value=None, isEnable=True, maxWidth=None, toolTip=None):
        super(SpliceLogParamsWidget, self).__init__()
        self.__value = {}

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__startLogLineEdit = CommonLineEdit(label='起始日志关键字')
        hbox.addWidget(self.__startLogLineEdit, 1)
        self.__endLogLineEdit = CommonLineEdit(label='结束日志关键字')
        hbox.addWidget(self.__endLogLineEdit, 1)
        self.__splitReLineEdit = CommonLineEdit(label='拆分正则表达式')
        hbox.addWidget(self.__splitReLineEdit, 1)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__funcLineEdit = CommonLineEdit(label='日志处理函数', toolTip='执行指定的代码，入参text，出参res')
        hbox.addWidget(self.__funcLineEdit, 3)
        self.__enableUmlCheckBox = WidgetUtil.createCheckBox(self, text="plantuml日志转图片", toolTip="对执行结果执行uml转换功能生成图片")
        hbox.addWidget(self.__enableUmlCheckBox, 1)
        vbox.addLayout(hbox)

        self.updateData(value)
        self.setEnabled(isEnable)
        if maxWidth:
            self.setMaximumWidth(maxWidth)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __updateUi(self):
        self.__startLogLineEdit.updateData(DictUtil.get(self.__value, KEY_START_LOG_KEYWORD))
        self.__endLogLineEdit.updateData(DictUtil.get(self.__value, KEY_END_LOG_KEYWORD))
        self.__splitReLineEdit.updateData(DictUtil.get(self.__value, KEY_SPLIT_RE))
        self.__funcLineEdit.updateData(DictUtil.get(self.__value, KEY_FUNCTION))
        self.__enableUmlCheckBox.setChecked(DictUtil.get(self.__value, KEY_ENABLE_UML_TRANSFORM, False))
        # self.adjustSize()
        pass

    def updateData(self, value):
        self.__value = value
        self.__updateUi()
        pass

    def getData(self):
        return {
            KEY_START_LOG_KEYWORD: self.__startLogLineEdit.getData(),
            KEY_END_LOG_KEYWORD: self.__endLogLineEdit.getData(),
            KEY_SPLIT_RE: self.__splitReLineEdit.getData(),
            KEY_FUNCTION: self.__funcLineEdit.getData(),
            KEY_ENABLE_UML_TRANSFORM: self.__enableUmlCheckBox.isChecked()
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = SpliceLogParamsWidget(
        toolTip='dddddd')
    e.show()
    LogUtil.d(TAG, e.getData())
    sys.exit(app.exec_())
