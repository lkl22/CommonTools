# -*- coding: utf-8 -*-
# python 3.x
# Filename: DragInputWidget.py
# 定义一个DragInputWidget窗口类实现拖动文件输入的功能
import os
import sys
from PyQt5.QtWidgets import QStyle

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from util.PlatformUtil import PlatformUtil
from widget.custom.ICommonWidget import ICommonWidget


class DragInputWidget(ICommonWidget):
    def __init__(self, label=None, text=None, fileParam=None, dirParam=None, isReadOnly=True, holderText=None,
                 labelMinSize: QSize = None, toolTip=None, textChanged=None):
        super(DragInputWidget, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.fileParam = fileParam
        self.dirParam = dirParam

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        if label:
            hbox.addWidget(WidgetUtil.createLabel(self, text=label, minSize=labelMinSize))
        self.lineEdit = WidgetUtil.createLineEdit(self, text=text, holderText=holderText, toolTip=toolTip,
                                                  textChanged=textChanged, isReadOnly=isReadOnly)
        if dirParam:
            self.lineEdit.addAction(
                WidgetUtil.createAction(self, icon=QIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon)),
                                        text="打开目录", func=self.__openDir), QLineEdit.TrailingPosition)
        if fileParam:
            self.lineEdit.addAction(
                WidgetUtil.createAction(self, icon=QIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon)),
                                        text="打开文件", func=self.__openFile), QLineEdit.TrailingPosition)

        hbox.addWidget(self.lineEdit)
        self.setAutoFillBackground(True)

        self.setToolTip(toolTip)
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

    def __openFile(self):
        directoryParam = {KEY_DIRECTORY: self.__getParentDir()}
        fileParam = DictUtil.join([self.fileParam, directoryParam])
        fp = WidgetUtil.getOpenFileName(self, **fileParam)
        self.__updateContent(fp)

    def __openDir(self):
        directoryParam = {KEY_DIRECTORY: self.__getParentDir()}
        dirParam = DictUtil.join([self.dirParam, directoryParam])
        fp = WidgetUtil.getExistingDirectory(self, **dirParam)
        self.__updateContent(fp)

    def __getParentDir(self):
        filePath = self.lineEdit.text().strip()
        if filePath:
            fp, _ = os.path.split(filePath)
            return fp
        return ''

    def __updateContent(self, fp):
        if self.lineEdit and fp:
            self.lineEdit.setText(fp)
        pass

    def getData(self):
        return self.lineEdit.text().strip()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = DragInputWidget(label='名字', isReadOnly=False)
    # e = DragInputWidget(fileParam=["file", "./", "*.py", "*.py"])
    # e = DragInputWidget(dirParam=["dir", "./"])
    e = DragInputWidget(label='请选择需要的文件',
                        fileParam={KEY_CAPTION: "file", KEY_DIRECTORY: "./", KEY_FILTER: "*.py",
                                   KEY_INITIAL_FILTER: "*.py"},
                        dirParam={KEY_CAPTION: "dir", KEY_DIRECTORY: "./"},
                        isReadOnly=False, toolTip="test toolTip")
    e.show()
    sys.exit(app.exec_())
