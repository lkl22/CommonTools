# -*- coding: utf-8 -*-
# python 3.x
# Filename: ClickLabel.py
# 定义一个ClickLabel窗口类实现可点击的Label控件
import sys

from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QLabel
from util.WidgetUtil import *

TAG = "ClickableLabel"


class ClickableLabel(QLabel):
    def __init__(self, parent: QWidget = None, text=None, toolTip=None, leftDoubleClicked=None):
        super(ClickableLabel, self).__init__(parent)
        self.leftDoubleClicked = leftDoubleClicked
        if text:
            self.setText(text)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def mouseDoubleClickEvent(self, ev: QMouseEvent) -> None:
        LogUtil.d(TAG, f'mouseDoubleClickEvent: {ev.button()}')
        if self.leftDoubleClicked and ev.button() == Qt.LeftButton:
            self.leftDoubleClicked()
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ClickableLabel(text="可点击Label", toolTip="可点击Label", leftDoubleClicked=lambda: print("leftDoubleClicked"))
    e.show()
    sys.exit(app.exec_())
