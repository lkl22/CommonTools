# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonSpinBox.py
# 定义一个CommonSpinBox窗口类实现通用计数器控件的功能
import sys
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonSpinBox'


class CommonSpinBox(ICommonWidget):
    def __init__(self, label: str, value=None, minValue=None, maxValue=None, step=None, prefix=None, suffix=None,
                 intBase=None, labelMinSize: QSize = None, toolTip=None):
        super(CommonSpinBox, self).__init__()
        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text=label, minSize=labelMinSize))
        self.__spinBox = WidgetUtil.createSpinBox(self, value=value, minValue=minValue, maxValue=maxValue, step=step,
                                                  prefix=prefix, suffix=suffix, intBase=intBase)
        hbox.addWidget(self.__spinBox, 1)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def updateData(self, value):
        self.__spinBox.setValue(value)
        pass

    def getData(self):
        return self.__spinBox.value()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonSpinBox(label='name',
                      value=55,
                      labelMinSize=QSize(120, 0),
                      toolTip='dddddd')
    e.show()
    sys.exit(app.exec_())
