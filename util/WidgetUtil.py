# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetUtil.py
# 定义一个WidgetUtil工具类实现Widget相关的功能
from PyQt5 import QtCore, QtGui, QtWidgets


class WidgetUtil:
    @staticmethod
    def createGroupBox(parent: QtWidgets.QWidget):
        groupBox = QtWidgets.QGroupBox(parent)
        # QtWidgets.QSizePolicy
        return groupBox
