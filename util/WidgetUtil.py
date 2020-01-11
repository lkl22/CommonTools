# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetUtil.py
# 定义一个WidgetUtil工具类实现Widget相关的功能
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox, QSizePolicy
from PyQt5.QtCore import QRect, QMargins, QSize, Qt

_translate = QtCore.QCoreApplication.translate
contextName = "CommonTools"


def widgetSetAttrs(widget: QWidget, objectName, toolTip=None, geometry: QRect = None, minSize: QSize = None,
                   margins: QMargins = None, isEnable=True, sizePolicy: QSizePolicy = None):
    """
    给Widget设置属性
    :param widget: QWidget
    :param objectName: objectName
    :param toolTip: toolTip
    :param geometry: 位置尺寸
    :param minSize: 最小size
    :param margins: margin值
    :param isEnable: Enabled
    :param sizePolicy: 缩放策略
    """
    widget.setObjectName(objectName)
    widget.setEnabled(isEnable)
    if toolTip:
        widget.setToolTip(_translate(contextName, toolTip))
    if geometry:
        widget.setGeometry(geometry)
    if minSize:
        widget.setMinimumSize(minSize)
    if margins:
        widget.setContentsMargins(margins)
    if sizePolicy:
        widget.setSizePolicy(sizePolicy)
    pass


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
        return QMessageBox.warning(parent, title, message)

    @staticmethod
    def showQuestionDialog(parent=None, title="Message", message="", acceptFunc=None):
        """
        显示一个确认弹框
        :param parent: 父widget
        :param title: 标题
        :param message: 提示文本
        :param acceptFunc: 点击确认按钮处理函数
        :return:
        """
        box = QMessageBox.question(parent, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if box == QMessageBox.Yes:
            print("yes")
            if acceptFunc:
                acceptFunc()
        else:
            print("No")

    @staticmethod
    def createSizePolicy(hPolicy=QSizePolicy.Expanding, vPolicy=QSizePolicy.Expanding, hStretch=1, vStretch=1):
        """
        创建QSizePolicy
        :param hPolicy: 水平缩放策略
        :param vPolicy: 垂直缩放策略
        :param hStretch: 水平缩放因子
        :param vStretch: 垂直缩放因子
        :return: QSizePolicy
        """
        sizePolicy = QSizePolicy()
        # 水平和垂直方向的大小策略
        sizePolicy.setHorizontalPolicy(hPolicy)
        sizePolicy.setVerticalPolicy(vPolicy)
        # 缩放因子
        sizePolicy.setHorizontalStretch(hStretch)
        sizePolicy.setVerticalStretch(vStretch)
        return sizePolicy

    @staticmethod
    def createHBoxLayout(objectName="HBoxLayout", margins: QMargins = None):
        """
        创建一个水平布局容器
        :param objectName: objectName
        :param margins: margin值
        :return: QHBoxLayout
        """
        layout = QtWidgets.QHBoxLayout()
        layout.setObjectName(objectName)
        if margins:
            layout.setContentsMargins(margins)
        return layout

    @staticmethod
    def createVBoxLayout(objectName="VBoxLayout", margins: QMargins = None):
        """
        创建一个垂直布局容器
        :param objectName: objectName
        :param margins: margin值
        :return: QVBoxLayout
        """
        layout = QtWidgets.QVBoxLayout()
        layout.setObjectName(objectName)
        if margins:
            layout.setContentsMargins(margins)
        return layout

    @staticmethod
    def createSplitter(parent: QWidget = None, isVertical=False, objectName="Splitter", toolTip=None, geometry: QRect = None):
        """
        创建一个动态的布局管理器
        :param parent: 父QWidget
        :param isVertical: True 垂直方向
        :param objectName: objectName
        :param toolTip: toolTip
        :param geometry: geometry
        :return: QSplitter
        """
        widget = QtWidgets.QSplitter()
        if parent:
            widget.setParent(parent)
        if isVertical:
            widget.setOrientation(Qt.Vertical)
        else:
            widget.setOrientation(Qt.Horizontal)
        widgetSetAttrs(widget, objectName, toolTip, geometry)
        return widget

    @staticmethod
    def createLabel(parent: QWidget, objectName="Label", text="", alignment=Qt.AlignVCenter | Qt.AlignLeft, geometry: QRect = None, minSize: QSize = None, sizePolicy: QSizePolicy = None):
        """
        创建一个Label标签
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param alignment: 文本对其方式，默认左居中
        :param geometry: geometry
        :param minSize: minSize
        :param sizePolicy: 缩放策略
        :return: QLabel
        """
        widget = QtWidgets.QLabel(parent)
        widgetSetAttrs(widget, objectName, geometry=geometry, minSize=minSize, sizePolicy=sizePolicy)
        widget.setAlignment(alignment)
        widget.setText(_translate(contextName, text))
        return widget

    @staticmethod
    def createGroupBox(parent: QWidget, objectName="GroupBox", title="GroupBox", toolTip=None, geometry: QRect = None,
                       minSize: QSize = None, margins: QMargins = None, sizePolicy: QSizePolicy = None):
        """
        创建一个GroupBox
        :param parent: 父QWidget
        :param objectName: objectName
        :param title: title
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param margins: margins
        :param sizePolicy: 缩放策略
        :return: QGroupBox
        """
        widget = QtWidgets.QGroupBox(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, margins=margins, sizePolicy=sizePolicy)
        widget.setTitle(_translate(contextName, title))
        if margins:
            widget.setContentsMargins(margins)
        return widget

    @staticmethod
    def createPushButton(parent: QWidget, objectName="PushButton", text="PushButton", toolTip=None, geometry: QRect = None,
                         sizePolicy: QSizePolicy = None, onClicked=None):
        """
        创建一个Button
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param geometry: geometry
        :param sizePolicy: 缩放策略
        :param onClicked: clicked回调函数
        :return: QPushButton
        """
        widget = QtWidgets.QPushButton(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, sizePolicy=sizePolicy)
        widget.setText(_translate(contextName, text))
        if onClicked:
            widget.clicked.connect(onClicked)
        return widget

    @staticmethod
    def createLineEdit(parent: QWidget, objectName="LineEdit", text="", holderText="", toolTip=None, geometry: QRect = None,
                       isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个输入文本框
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param holderText: holderText
        :param toolTip: toolTip
        :param geometry: geometry
        :param isEnable: enable
        :param sizePolicy: 缩放策略
        :return: QLineEdit
        """
        widget = QtWidgets.QLineEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        if holderText:
            widget.setPlaceholderText(_translate(contextName, holderText))
        if text:
            widget.setText(_translate(contextName, text))
        return widget

    @classmethod
    def translate(cls, context=contextName, text=""):
        return _translate(context, text)
