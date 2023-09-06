# -*- coding: utf-8 -*-
# python 3.x
# Filename: DragInputWidget.py
# 定义一个DragInputWidget窗口类实现拖动文件输入的功能
import os
import sys
from PyQt5.QtWidgets import QFrame, QStyle
from util.WidgetUtil import *
from util.PlatformUtil import PlatformUtil


class DragInputWidget(QFrame):
    def __init__(self, label=None, text=None, fileParam=None, dirParam=None, isReadOnly=True, holderText=None,
                 toolTip=None, textChanged=None):
        super(DragInputWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.fileParam = fileParam
        self.dirParam = dirParam

        hbox = WidgetUtil.createHBoxLayout(self)
        if label:
            hbox.addWidget(WidgetUtil.createLabel(self, text=label))
        self.lineEdit = WidgetUtil.createLineEdit(self, text=text, holderText=holderText, toolTip=toolTip,
                                                  textChanged=textChanged, isReadOnly=isReadOnly)
        if dirParam:
            self.lineEdit.addAction(
                WidgetUtil.createAction(self, icon=QIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon)),
                                        text="打开目录", func=self.openDir), QLineEdit.TrailingPosition)
        if fileParam:
            self.lineEdit.addAction(
                WidgetUtil.createAction(self, icon=QIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon)),
                                        text="打开文件", func=self.openFile), QLineEdit.TrailingPosition)

        hbox.addWidget(self.lineEdit)
        self.setAutoFillBackground(True)

        self.setToolTip(toolTip)

        hbox.setContentsMargins(0, 0, 0, 0)
        # 调用Drops方法
        self.setAcceptDrops(True)
        pass

    def setFileParam(self, fileParam):
        self.fileParam = fileParam

    def setDirParam(self, dirParam):
        self.dirParam = dirParam

    # 鼠标拖入事件
    def dragEnterEvent(self, evn):
        text = evn.mimeData().text()
        text = text.replace("file://" if PlatformUtil.isMac() else "file:///", "")
        if self.fileParam and not os.path.isfile(text):
            WidgetUtil.showErrorDialog(message="请拖动一个文件到此")
            return
        if self.dirParam and not os.path.isdir(text):
            WidgetUtil.showErrorDialog(message="请拖动一个文件夹到此")
            return

        self.lineEdit.setText(text)
        # 鼠标放开函数事件
        evn.accept()

    # 鼠标放开执行
    def dropEvent(self, evn):
        LogUtil.d('dropEvent', '鼠标放开了')

    def dragMoveEvent(self, evn):
        # LogUtil.d('dragMoveEvent', '鼠标移动')
        pass

    def openFile(self):
        if self.fileParam:
            fp = WidgetUtil.getOpenFileName(self, *self.fileParam)
        else:
            fp = WidgetUtil.getOpenFileName()
        self.updateContent(fp)

    def openDir(self):
        if self.dirParam:
            fp = WidgetUtil.getExistingDirectory(self, *self.dirParam)
        else:
            fp = WidgetUtil.getExistingDirectory(self)
        self.updateContent(fp)

    def updateContent(self, fp):
        if self.lineEdit and fp:
            self.lineEdit.setText(fp)
        pass

    def text(self):
        return self.lineEdit.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = DragInputWidget(label='名字', isReadOnly=False)
    # e = DragInputWidget(fileParam=["file", "./", "*.py", "*.py"])
    # e = DragInputWidget(dirParam=["dir", "./"])
    # e = DragInputWidget(label='请选择需要的文件', fileParam=["file", "./", "*.py", "*.py"], dirParam=["dir", "./"], isReadOnly=False,
    #                     toolTip="test toolTip")
    e.show()
    sys.exit(app.exec_())
