# -*- coding: utf-8 -*-
# python 3.x
# Filename: SwapTextWidget.py
# 定义一个SwapTextWidget窗口类实现内容交换控件
import sys

from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'SwapTextWidget'
KEY_LEFT_TXT = 'leftTxt'
KEY_RIGHT_TXT = 'rightTxt'


class SwapTextWidget(ICommonWidget):
    def __init__(self, label=None, data=None, labelMinSize: QSize = None, toolTip=None, textChanged=None,
                 required=False):
        super(SwapTextWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__textChanged = textChanged

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hbox.addWidget(
            WidgetUtil.createLabel(self, text=label if label else '', minSize=labelMinSize, required=required))
        self.__leftLineEdit = WidgetUtil.createLineEdit(self, editingFinished=self.__lineEditChanged)
        hbox.addWidget(self.__leftLineEdit)

        btn = WidgetUtil.createPushButton(self, text="", fixedSize=QSize(40, 30),
                                          styleSheet="background-color: white",
                                          iconSize=QSize(40, 30),
                                          icon=QIcon(FileUtil.getIconFp('androidRes/swap.png')),
                                          onClicked=self.__swapLineEdit)
        hbox.addWidget(btn)

        self.__rightLineEdit = WidgetUtil.createLineEdit(self, editingFinished=self.__lineEditChanged)
        hbox.addWidget(self.__rightLineEdit)

        self.__updateContent(data)
        self.setAutoFillBackground(True)

        self.setToolTip(toolTip)
        # 调用Drops方法
        self.setAcceptDrops(True)
        pass

    def __swapLineEdit(self):
        LogUtil.i(TAG, '__swapLineEdit')
        leftTxt = self.__leftLineEdit.text().strip()
        rightTxt = self.__rightLineEdit.text().strip()
        self.__leftLineEdit.setText(rightTxt)
        self.__rightLineEdit.setText(leftTxt)
        self.__lineEditChanged()
        pass

    def __lineEditChanged(self):
        LogUtil.i(TAG, '__lineEditChanged')
        if self.__textChanged:
            self.__textChanged(self.getData())

    def __updateContent(self, data):
        self.__leftLineEdit.setText(DictUtil.get(data, KEY_LEFT_TXT, ''))
        self.__rightLineEdit.setText(DictUtil.get(data, KEY_RIGHT_TXT, ''))
        pass

    def updateData(self, data):
        self.__updateContent(data)
        pass

    def getData(self):
        return {
            KEY_LEFT_TXT: self.__leftLineEdit.text().strip(),
            KEY_RIGHT_TXT: self.__rightLineEdit.text().strip()
        }


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = SwapTextWidget(toolTip="test toolTip", required=True)
    # e = SwapTextWidget(label='请选择需要的文件', toolTip="test toolTip", required=True)
    e.show()
    sys.exit(app.exec_())
