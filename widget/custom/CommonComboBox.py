# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonComboBox.py
# 定义一个CommonComboBox窗口类实现通用下拉选择弹框的功能
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QListView

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.WidgetUtil import *

TAG = 'CommonComboBox'


class CommonComboBox(QFrame):
    def __init__(self, label: str, default=None, groupList: [{} or str] = [], toolTip=None):
        super(CommonComboBox, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        if type(groupList[0]) == str:
            self.__groupList = [{KEY_SHOW_TEXT: item} for item in groupList]
        else:
            self.__groupList = groupList
        self.__default = default if default else DictUtil.get(self.__groupList[0], KEY_DATA,
                                                              DictUtil.get(self.__groupList[0], KEY_SHOW_TEXT))

        hBox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text=label))
        self.__comboBox = WidgetUtil.createComboBox(self, activated=self.__activated)
        self.__comboBox.setView(QListView())
        self.setStyleSheet('QComboBox QAbstractItemView::item {padding-top:2px;padding-bottom:2px}')
        hBox.addWidget(self.__comboBox, 1)
        self.__updateComboBox()
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __updateComboBox(self):
        curIndex = 0
        for index, item in enumerate(self.__groupList):
            if KEY_SHOW_TEXT not in item:
                continue
            if KEY_COLOR in item:
                pixmap = QPixmap(180, 60)
                pixmap.fill(QColor(item[KEY_COLOR]))
                self.__comboBox.addItem(QIcon(pixmap), item[KEY_SHOW_TEXT])
            else:
                self.__comboBox.addItem(item[KEY_SHOW_TEXT])
            data = DictUtil.get(item, KEY_DATA, DictUtil.get(item, KEY_SHOW_TEXT))
            if self.__default == data:
                curIndex = index
        self.__comboBox.setCurrentIndex(curIndex)
        pass

    def __activated(self):
        curData = self.__groupList[self.__comboBox.currentIndex()]
        self.__default = DictUtil.get(curData, KEY_DATA, DictUtil.get(curData, KEY_SHOW_TEXT))
        LogUtil.d(TAG, '__activated', curData, self.__default)
        pass

    def getData(self):
        return self.__default


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = CommonComboBox()
    # e = CommonComboBox(fileParam=["file", "./", "*.py", "*.py"])
    # e = CommonComboBox(dirParam=["dir", "./"])
    e = CommonComboBox(label='选择颜色：', default='ss', groupList=[
        {KEY_COLOR: '#FF0000', KEY_SHOW_TEXT: 'red', KEY_DATA: 'ss'},
        {KEY_COLOR: '#00FF00', KEY_SHOW_TEXT: 'green'},
        {KEY_SHOW_TEXT: 'blue'}, {}
    ], toolTip='请选择需要的颜色')
    e.show()
    sys.exit(app.exec_())
