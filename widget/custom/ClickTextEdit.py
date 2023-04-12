# -*- coding: utf-8 -*-
# python 3.x
# Filename: ClickTextEdit.py
# 定义一个ClickTextEdit窗口类实现可点击的QTextEdit控件
import sys

from PyQt5.QtGui import QMouseEvent
from util.WidgetUtil import *

TAG = "ClickTextEdit"


class ClickTextEdit(QTextEdit):
    def __init__(self, parent: QWidget = None, isReadOnly=False, toolTip=None, linkClicked=None):
        super(ClickTextEdit, self).__init__(parent)
        self.linkClicked = linkClicked
        self.link = None
        self.setReadOnly(isReadOnly)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def mousePressEvent(self, ev: QMouseEvent):
        self.link = self.anchorAt(ev.pos())
        pass

    def mouseReleaseEvent(self, ev: QMouseEvent):
        if self.link:
            LogUtil.i(TAG, f"Clicked on {self.link}")
            if self.linkClicked:
                self.linkClicked(self.link)
            self.link = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ClickTextEdit(isReadOnly=True, toolTip="可点击Label", linkClicked=lambda it: print("linkClicked", it))
    messages = ["Somethingsomething", "Hello", "What is up", "Big bo"]
    for msg in messages:
        e.append(
            f'<span>{msg}<a style="color: pink" href="{msg}">[Add]</a></span>'
        )
    e.show()
    sys.exit(app.exec_())
