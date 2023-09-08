# -*- coding: utf-8 -*-
# python 3.x
# Filename: ICommonWidget.py
# 定义一个ICommonWidget类实现通用组件接口类
from PyQt5.QtWidgets import QFrame
from abc import abstractmethod


class ICommonWidget(QFrame):
    @abstractmethod
    def getData(self):
        pass
