# -*- coding: utf-8 -*-
# python 3.x
# Filename: ChoiceButton.py
# 定义一个ChoiceButton窗口类实现单选，多选的功能（文本支持滑动）
import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QFrame
from util.WidgetUtil import *


class ChoiceButton(QFrame):
    class Mode(int):
        ...

    Radio = ...  # type: 'ChoiceButton.Mode'
    CheckBox = ...  # type: 'ChoiceButton.Mode'

    Radio = 0
    CheckBox = 1

    toggled = pyqtSignal(int)

    def __init__(self, option: str, text="", id=-1, onToggled=None):
        super(ChoiceButton, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.mode = ChoiceButton.Radio
        self.id = id

        hbox = WidgetUtil.createHBoxLayout(self)
        self.radioBtn = WidgetUtil.createRadioButton(self, text="")
        self.radioBtn.clicked.connect(lambda: self.toggled.emit(self.id))
        hbox.addWidget(self.radioBtn)

        self.checkBox = WidgetUtil.createCheckBox(self, text="")
        self.checkBox.clicked.connect(lambda: self.toggled.emit(self.id))
        hbox.addWidget(self.checkBox)

        self.optionLabel = WidgetUtil.createLabel(self, text=option)
        hbox.addWidget(self.optionLabel)
        self.descLabel = WidgetUtil.createLabel(self, text=text)
        hbox.addWidget(self.descLabel, 1)

        self.setMode(ChoiceButton.Radio)
        self.setAutoFillBackground(True)
        if onToggled:
            self.toggled.connect(onToggled)

        hbox.setContentsMargins(0, 10, 0, 10)
        pass

    def setMode(self, mode: Mode):
        self.radioBtn.setVisible(mode == ChoiceButton.Radio)
        self.checkBox.setVisible(mode == ChoiceButton.CheckBox)
        self.mode = mode
        pass

    def getMode(self):
        return self.mode

    def mousePressEvent(self, ev: QMouseEvent):
        LogUtil.d('mousePressEvent')
        if ev.button() == Qt.LeftButton:
            if self.mode == ChoiceButton.Radio:
                self.radioBtn.setChecked(True)
            else:
                self.checkBox.setChecked(not self.checkBox.isChecked())
            self.toggled.emit(self.id)
        pass

    def isChecked(self):
        if self.mode == ChoiceButton.Radio:
            return self.radioBtn.isChecked()
        else:
            return self.checkBox.isChecked()

    def getButton(self, mode: Mode = None):
        if not mode:
            mode = self.mode
        if mode == ChoiceButton.Radio:
            return self.radioBtn
        else:
            return self.checkBox

    def setText(self, option: str = None, text: str = None):
        if option:
            self.optionLabel.setText(option)
        if text:
            self.descLabel.setText(text)
        self.adjustSize()

    def setChecked(self, isChecked: bool):
        self.radioBtn.setChecked(isChecked)
        self.checkBox.setChecked(isChecked)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ChoiceButton(
        option="A.",
        text="ddddd\nddd\n\n\nnn\n\ndd\n\ndfg\n\n\nn\\\n\nggggggfdddddddddddddggggggfdddddddddddddggggggfdddddddddddddggggggfdddddddddddddggggggfdddddddddddddggggggfddddddddddddd")
    e.show()
    sys.exit(app.exec_())
