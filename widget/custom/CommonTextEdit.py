# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonTextEdit.py
# 定义一个CommonTextEdit窗口类实现通用多行文本显示的功能
import sys

from PyQt5.QtCore import pyqtSignal

from util.ClipboardUtil import ClipboardUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonTextEdit'


class CommonTextEdit(ICommonWidget):
    __standardOutputSignal = pyqtSignal(list)

    def __init__(self, text: str = None, isReadOnly: bool = True, holderText: str = None, toolTip=None):
        super(CommonTextEdit, self).__init__()
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(self, text='Copy', onClicked=self.__copyData))
        hbox.addItem(WidgetUtil.createHSpacerItem())
        vbox.addLayout(hbox)
        self.__textEdit = WidgetUtil.createTextEdit(self, text=text, isReadOnly=isReadOnly, holderText=holderText)
        vbox.addWidget(self.__textEdit, 1)
        self.__standardOutputSignal.connect(self.__standardOutput)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __standardOutput(self, message):
        if type(message) == list:
            WidgetUtil.textEditAppendMessages(self.__textEdit, messages=message)
        else:
            WidgetUtil.textEditAppendMessage(self.__textEdit, *message)
        pass

    def __copyData(self):
        ClipboardUtil.copyToClipboard(self.getData())

    def clear(self):
        self.__textEdit.clear()
        pass

    def standardOutput(self, message: list[dict]):
        self.__standardOutputSignal.emit(message)
        pass

    def standardOutputOne(self, log, color):
        self.__standardOutputSignal.emit([{KEY_LOG: log, KEY_COLOR: color}])
        pass

    def getData(self):
        return self.__textEdit.toPlainText()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonTextEdit(text='ddd\ndddfffeef',
                       isReadOnly=False,
                       toolTip='dddddd')
    e.show()
    sys.exit(app.exec_())
