# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonTextEdit.py
# 定义一个CommonTextEdit窗口类实现通用多行文本显示的功能
import sys

from PyQt5.QtCore import pyqtSignal

from util.ClipboardUtil import ClipboardUtil
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.ClickTextEdit import ClickTextEdit
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonTextEdit'


class CommonTextEdit(ICommonWidget):
    __standardOutputSignal = pyqtSignal(list)
    __hrefOutputSignal = pyqtSignal(str, str, int)

    def __init__(self, title: str = None, text: str = None, isReadOnly: bool = True, holderText: str = None,
                 toolTip=None, isShowCopyFunc=True, linkClicked=None):
        super(CommonTextEdit, self).__init__()
        self.linkClicked = linkClicked
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        if isShowCopyFunc or title:
            hbox = WidgetUtil.createHBoxLayout(spacing=10)
            if title:
                hbox.addWidget(WidgetUtil.createLabel(self, text=title))
            if isShowCopyFunc:
                hbox.addWidget(WidgetUtil.createPushButton(self, text='Copy', onClicked=self.__copyData))
            hbox.addItem(WidgetUtil.createHSpacerItem())
            vbox.addLayout(hbox)
        self.__textEdit = ClickTextEdit(self, isReadOnly=isReadOnly, linkClicked=self.linkClicked)
        self.__textEdit.setText(text if text else '')
        self.__textEdit.setPlaceholderText(holderText if holderText else '')
        vbox.addWidget(self.__textEdit, 1)

        self.__standardOutputSignal.connect(self.__standardOutput)
        self.__hrefOutputSignal.connect(self.__hrefOutput)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __standardOutput(self, message):
        if type(message) == list:
            data = []
            for item in message:
                if DictUtil.get(item, KEY_TYPE) != KEY_HYPERLINK:
                    if '<a style' in item[KEY_LOG]:
                        WidgetUtil.textEditAppendMessages(self.__textEdit, messages=data)
                        data = []
                        self.__textEdit.append(f'<span style="color: {item[KEY_COLOR]}">{item[KEY_LOG]}</span>')
                    else:
                        data.append(item)
                else:
                    WidgetUtil.textEditAppendMessages(self.__textEdit, messages=data)
                    data = []
                    self.__hrefOutput(DictUtil.get(item, KEY_SHOW_TEXT, ''), DictUtil.get(item, KEY_HYPERLINK_TXT, 'link'), DictUtil.get(item, KEY_WRAP_NUM, 0))
            if data:
                WidgetUtil.textEditAppendMessages(self.__textEdit, messages=data)
        else:
            WidgetUtil.textEditAppendMessage(self.__textEdit, *message)
        pass

    def __hrefOutput(self, showText, hrefContent, wrapNum=0):
        self.__textEdit.append(
            f'<span>{showText}<a style="color: red" href="{hrefContent}">{hrefContent}</a></span>{"".rjust(wrapNum, "&").replace("&", "<br/>")}')

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

    def hrefOutput(self, showText, hrefContent, wrapNum=0):
        self.__hrefOutputSignal.emit(showText, hrefContent, wrapNum)
        pass

    def getData(self):
        return self.__textEdit.toPlainText()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonTextEdit(title='',
                       text='ddd\ndddfffeef',
                       isReadOnly=False,
                       toolTip='dddddd',
                       isShowCopyFunc=False)
    e.show()
    sys.exit(app.exec_())
