# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonLineEdit.py
# 定义一个CommonLineEdit窗口类实现通用文本编辑的功能
import sys
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonLineEdit'


class CommonLineEdit(ICommonWidget):
    def __init__(self, label: str, text: str = None, labelMinSize: QSize = None, holderText: str = None, maxWidth=None,
                 toolTip=None):
        super(CommonLineEdit, self).__init__()
        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text=label, minSize=labelMinSize))
        self.__lineEdit = WidgetUtil.createLineEdit(self, text=text, holderText=holderText)
        hbox.addWidget(self.__lineEdit, 1)

        if maxWidth:
            self.setMaximumWidth(maxWidth)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def updateData(self, text):
        self.__lineEdit.setText(text)
        pass

    def getData(self):
        return self.__lineEdit.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonLineEdit(label='name',
                       text='ddd',
                       labelMinSize=QSize(120, 0),
                       toolTip='dddddd')
    e.show()
    sys.exit(app.exec_())
