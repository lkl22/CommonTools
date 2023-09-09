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
    def __init__(self, label: str, default=None, group: [{}] = [], toolTip=None):
        super(CommonComboBox, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__group = group
        self.__default = default if default else DictUtil.get(group[0], KEY_DATA, DictUtil.get(group[0], KEY_SHOW_TEXT))

        hBox = WidgetUtil.createHBoxLayout(self)
        hBox.addWidget(WidgetUtil.createLabel(self, text=label))
        self.comboBox = WidgetUtil.createComboBox(self, activated=self.__activated)
        self.comboBox.setView(QListView())
        self.setStyleSheet('QComboBox QAbstractItemView::item {padding-top:2px;padding-bottom:2px}')
        hBox.addWidget(self.comboBox, 1)
        self.__updateComboBox()
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)

        hBox.setContentsMargins(0, 0, 0, 0)
        pass

    def __updateComboBox(self):
        curIndex = 0
        for index, item in enumerate(self.__group):
            if KEY_SHOW_TEXT not in item:
                continue
            if KEY_COLOR in item:
                pixmap = QPixmap(180, 60)
                pixmap.fill(QColor(item[KEY_COLOR]))
                self.comboBox.addItem(QIcon(pixmap), item[KEY_SHOW_TEXT])
            else:
                self.comboBox.addItem(item[KEY_SHOW_TEXT])
            data = DictUtil.get(item, KEY_DATA, DictUtil.get(item, KEY_SHOW_TEXT))
            if self.__default == data:
                curIndex = index
        self.comboBox.setCurrentIndex(curIndex)
        pass

    def __activated(self):
        curData = self.__group[self.comboBox.currentIndex()]
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
    e = CommonComboBox(label='选择颜色：', default='ss', group=[
        {KEY_COLOR: '#FF0000', KEY_SHOW_TEXT: 'red', KEY_DATA: 'ss'},
        {KEY_COLOR: '#00FF00', KEY_SHOW_TEXT: 'green'},
        {KEY_SHOW_TEXT: 'blue'}, {}
    ], toolTip='请选择需要的颜色')
    e.show()
    sys.exit(app.exec_())
