# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetUtil.py
# 定义一个WidgetUtil工具类实现Widget相关的功能
from PyQt5 import QtCore, QtGui, QtWidgets


class WidgetUtil:
    @staticmethod
    def getExistingDirectory():
        """
        打开一个文件夹弹框选择一个指定的文件夹
        :return: 文件夹路径
        """
        dirPath = QtWidgets.QFileDialog.getExistingDirectory()
        print("选择的目录： " + dirPath)
        return dirPath

    @staticmethod
    def showErrorDialog(parent=None, title="Error", message=""):
        """
        显示错误提示弹框
        :param parent: 父widget
        :param title: 标题
        :param message: 提示文本
        :return: 点击的button
        """
        return QtWidgets.QMessageBox.warning(parent, title, message)

    @staticmethod
    def createGroupBox(parent: QtWidgets.QWidget):
        groupBox = QtWidgets.QGroupBox(parent)
        # QtWidgets.QSizePolicy
        return groupBox
