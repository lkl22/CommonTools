# -*- coding: utf-8 -*-
# python 3.x
# Filename: DecisionTreeCodeGenDialog.py
# 定义一个DecisionTreeCodeGenDialog类实现通过uml图生成模版代码的功能
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QApplication

from util.LogUtil import LogUtil
from util.OperaIni import OperaIni
from util.WidgetUtil import WidgetUtil
from widget.custom.CommonTextEdit import CommonTextEdit

TAG = 'DecisionTreeCodeGenDialog'


class DecisionTreeCodeGenDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        DecisionTreeCodeGenDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        DecisionTreeCodeGenDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.6)
        LogUtil.d(TAG, "Init Harmony Merge Res Dialog")
        self.setObjectName("DecisionTreeCodeGenDialog")
        self.resize(DecisionTreeCodeGenDialog.WINDOW_WIDTH, DecisionTreeCodeGenDialog.WINDOW_HEIGHT)
        # self.setFixedSize(DecisionTreeCodeGenDialog.WINDOW_WIDTH, DecisionTreeCodeGenDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 合并资源文件处理"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()

        dialogLayout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        self.__umlCodeTextEdit = CommonTextEdit(title='请输入UML代码：', isShowCopyFunc=False)
        dialogLayout.addWidget(self.__umlCodeTextEdit, 1)

        self.__genTsCodeBtn = WidgetUtil.createPushButton(self, text='生成TypeScript Code')
        dialogLayout.addWidget(self.__genTsCodeBtn)

        self.__genCodeTextEdit = CommonTextEdit(title='生成代码：')
        dialogLayout.addWidget(self.__genCodeTextEdit, 1)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DecisionTreeCodeGenDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())