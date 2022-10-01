# -*- coding: utf-8 -*-
# python 3.x
# Filename: DragInputWidget.py
# 定义一个DragInputWidget窗口类实现拖动文件输入的功能
import sys


from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QFrame
from util.WidgetUtil import *
from util.PlatformUtil import PlatformUtil


class DragInputWidget(QFrame):
    def __init__(self, text="", fileParam=None, dirParam=None, isReadOnly=True, holderText=None, textChanged=None):
        super(DragInputWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.fileParam = fileParam
        self.dirParam = dirParam

        hbox = WidgetUtil.createHBoxLayout(self)
        self.lineEdit = WidgetUtil.createLineEdit(self, text=text, holderText=holderText, isEnable=False,
                                                  textChanged=textChanged, isReadOnly=isReadOnly)
        self.setAutoFillBackground(True)
        hbox.addWidget(self.lineEdit)
        hbox.setContentsMargins(0, 0, 0, 0)
        # 调用Drops方法
        self.setAcceptDrops(True)
        pass

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
        text = evn.mimeData().text()
        self.lineEdit.setText(text.replace("file://" if PlatformUtil.isMac() else "file:///", ""))
        # 鼠标放开函数事件
        evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):
        LogUtil.d('dropEvent', '鼠标放开了')

    def dragMoveEvent(self, evn):
        # LogUtil.d('dragMoveEvent', '鼠标移动')
        pass

    def mouseDoubleClickEvent(self, ev: QMouseEvent):
        LogUtil.d('mouseDoubleClickEvent')
        if ev.button() == Qt.LeftButton:
            if self.fileParam:
                fp = WidgetUtil.getOpenFileName(*self.fileParam)
                self.mouseLeftBtnDoubleClick(fp)
                return
            if self.dirParam:
                fp = WidgetUtil.getExistingDirectory(*self.dirParam)
                self.mouseLeftBtnDoubleClick(fp)
                return
            # 默认选择一个文件，不限制文件类型
            fp = WidgetUtil.getOpenFileName()
            self.mouseLeftBtnDoubleClick(fp)
        pass

    def mouseLeftBtnDoubleClick(self, fp):
        if fp:
            self.lineEdit.setText(fp)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = DragInputWidget()
    e.show()
    sys.exit(app.exec_())
