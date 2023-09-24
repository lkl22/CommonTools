# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonDateTimeFormatEdit.py
# 定义一个CommonDateTimeFormatEdit窗口类实现通用时间格式编辑控件的功能
import sys

from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonDateTimeFormatEdit'


class CommonDateTimeFormatEdit(ICommonWidget):
    def __init__(self, label: str, value=None, labelMinSize: QSize = None, maxWidth=None, toolTip=None):
        super(CommonDateTimeFormatEdit, self).__init__()
        self.__value = {}

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text=label, minSize=labelMinSize))
        self.__formatLineEdit = CommonLineEdit(label='日期格式', toolTip='请输入文本里日期文本的日期格式（例如：yyyyMMdd_HHmmss.SSS）')
        hbox.addWidget(self.__formatLineEdit, 2)
        self.__startIndexSpinBox = CommonSpinBox(label='起始位置', value=0, minValue=0, step=1,
                                                 toolTip='日期在文本中的起始位置，从下标0开始')
        hbox.addWidget(self.__startIndexSpinBox, 1)

        self.updateData(value)
        if maxWidth:
            self.setMaximumWidth(maxWidth)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __updateUi(self):
        self.__formatLineEdit.updateData(DictUtil.get(self.__value, KEY_DATETIME_FORMAT))
        self.__startIndexSpinBox.updateData(DictUtil.get(self.__value, KEY_START_INDEX, 0))
        self.adjustSize()
        pass

    def updateData(self, value):
        self.__value = value
        self.__updateUi()
        pass

    def getData(self):
        return {
            KEY_DATETIME_FORMAT: self.__formatLineEdit.getData(),
            KEY_START_INDEX: self.__startIndexSpinBox.getData()
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonDateTimeFormatEdit(label='日期格式',
                                 value={KEY_DATETIME_FORMAT: 'YYYY-MM-dd HH:mm:ss.SSS', KEY_START_INDEX: 3},
                                 labelMinSize=QSize(60, 0),
                                 toolTip='dddddd')
    e.show()
    LogUtil.d(TAG, e.getData())
    sys.exit(app.exec_())
