# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonDateTimeRangeEdit.py
# 定义一个CommonDateTimeRangeEdit窗口类实现通用时间范围选择控件的功能
import sys

from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonDateTimeRangeEdit'


class CommonDateTimeRangeEdit(ICommonWidget):
    def __init__(self, label: str, value=None, maxOffsetValue=300, labelMinSize: QSize = None, maxWidth=None,
                 toolTip=None):
        super(CommonDateTimeRangeEdit, self).__init__()
        self.__value = {}

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text=label, minSize=labelMinSize))
        self.__dateTimeEdit = WidgetUtil.createDateTimeEdit(self, displayFormat=DATETIME_FORMAT)
        hbox.addWidget(self.__dateTimeEdit, 2)
        self.__beforeSpinBox = WidgetUtil.createSpinBox(self, value=0, minValue=0, maxValue=maxOffsetValue, step=5,
                                                        prefix='before: ', suffix=' s')
        hbox.addWidget(self.__beforeSpinBox, 1)
        self.__afterSpinBox = WidgetUtil.createSpinBox(self, value=0, minValue=0, maxValue=maxOffsetValue, step=5,
                                                       prefix='after: ', suffix=' s')
        hbox.addWidget(self.__afterSpinBox, 1)

        self.updateData(value)
        if maxWidth:
            self.setMaximumWidth(maxWidth)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __updateUi(self):
        self.__dateTimeEdit.setDateTime(QDateTime.fromString(DictUtil.get(self.__value, KEY_DATETIME), DATETIME_FORMAT))
        self.__beforeSpinBox.setValue(DictUtil.get(self.__value, KEY_BEFORE, 0))
        self.__afterSpinBox.setValue(DictUtil.get(self.__value, KEY_AFTER, 0))
        self.adjustSize()
        pass

    def updateData(self, value):
        self.__value = value
        self.__updateUi()
        pass

    def getData(self):
        return {
            KEY_DATETIME: self.__dateTimeEdit.dateTime().toString(DATETIME_FORMAT),
            KEY_BEFORE: self.__beforeSpinBox.value(),
            KEY_AFTER: self.__afterSpinBox.value()
        }

    def getDateRange(self):
        curDatetime = self.__dateTimeEdit.dateTime()
        return curDatetime.addSecs(-self.__beforeSpinBox.value()), curDatetime.addSecs(self.__afterSpinBox.value())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonDateTimeRangeEdit(label='配置时间信息',
                                value={KEY_DATETIME: '2023-09-21 15:23:35', KEY_BEFORE: 12, KEY_AFTER: 23},
                                labelMinSize=QSize(80, 0),
                                toolTip='dddddd')
    e.show()
    LogUtil.d(TAG, e.getData(), e.getDateRange())
    sys.exit(app.exec_())
