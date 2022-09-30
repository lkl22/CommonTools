# -*- coding: utf-8 -*-
# python 3.x
# Filename: EmittingStream.py
# 定义一个EmittingStream类实现控制台显示的功能
from PyQt5 import QtCore


class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)  # 定义一个发送str的信号

    def write(self, text):
        self.textWritten.emit(str(text))
