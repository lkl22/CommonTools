# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonComboBox.py
# 定义一个CommonComboBox窗口类实现通用下拉选择弹框的功能
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QListView

from constant.WidgetConst import *
from util.WidgetUtil import *

TAG = 'CommonComboBox'


class CommonComboBox(QFrame):
    def __init__(self, label: str, group=[], toolTip=None):
        super(CommonComboBox, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__group = group

        hBox = WidgetUtil.createHBoxLayout(self)
        hBox.addWidget(WidgetUtil.createLabel(self, text=label))
        self.comboBox = WidgetUtil.createComboBox(self, currentIndexChanged=self.__indexChanged)
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
        for item in self.__group:
            if KEY_DESC not in item:
                continue
            if KEY_COLOR in item:
                pixmap = QPixmap(180, 60)
                pixmap.fill(QColor(item[KEY_COLOR]))
                self.comboBox.addItem(QIcon(pixmap), item[KEY_DESC])
            else:
                self.comboBox.addItem(item[KEY_DESC])
        pass

    def __indexChanged(self):
        curData = self.__group[self.comboBox.currentIndex()]
        LogUtil.d(TAG, '__indexChanged', curData)
        pass

    def getData(self):
        return self.__group[self.comboBox.currentIndex()]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = CommonComboBox()
    # e = CommonComboBox(fileParam=["file", "./", "*.py", "*.py"])
    # e = CommonComboBox(dirParam=["dir", "./"])
    e = CommonComboBox(label='选择颜色：', group=[
        {KEY_COLOR: '#FF0000', KEY_DESC: 'red', 'dd': 'ss'},
        {KEY_COLOR: '#00FF00', KEY_DESC: 'green'},
        {KEY_DESC: 'green'}, {}
    ], toolTip='请选择需要的颜色')
    e.show()
    sys.exit(app.exec_())
