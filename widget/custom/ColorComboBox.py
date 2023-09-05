# -*- coding: utf-8 -*-
# python 3.x
# Filename: ColorComboBox.py
# 定义一个ColorComboBox窗口类实现color颜色选择的功能
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QListView
from util.WidgetUtil import *

TAG = 'ColorComboBox'
KEY_COLOR = 'color'
KEY_TEXT = 'text'


class ColorComboBox(QFrame):
    def __init__(self, colorGroup=[], toolTip=None):
        super(ColorComboBox, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.colorGroup = colorGroup

        hBox = WidgetUtil.createHBoxLayout(self)
        hBox.addWidget(WidgetUtil.createLabel(self, text='选择颜色：'))
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
        for item in self.colorGroup:
            pixmap = QPixmap(180, 60)
            pixmap.fill(QColor(item[KEY_COLOR]))
            self.comboBox.addItem(QIcon(pixmap), item[KEY_TEXT])
        pass

    def __indexChanged(self):
        curData = self.colorGroup[self.comboBox.currentIndex()]
        LogUtil.d(TAG, '__indexChanged', curData)
        pass

    def getCurData(self):
        return self.colorGroup[self.comboBox.currentIndex()]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = ColorComboBox()
    # e = ColorComboBox(fileParam=["file", "./", "*.py", "*.py"])
    # e = ColorComboBox(dirParam=["dir", "./"])
    e = ColorComboBox(colorGroup=[{KEY_COLOR: '#FF0000', KEY_TEXT: 'red'}, {KEY_COLOR: '#00FF00', KEY_TEXT: 'green'}])
    e.show()
    sys.exit(app.exec_())
