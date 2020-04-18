# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetUtil.py
# 定义一个WidgetUtil工具类实现Widget相关的功能
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QBrush, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget, QMessageBox, QSizePolicy, QTreeWidget, QMenu, QTreeWidgetItem, QDialog, \
    QRadioButton, QTableView, QHeaderView
from PyQt5.QtCore import QRect, QMargins, QSize, Qt

from util import LogUtil
from util.DataTypeUtil import *

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
    def getOpenFileName(caption='', directory='', filter='', initialFilter=''):
        """
        打开一个文件弹框选择一个指定的文件
        :param caption: 标题
        :param directory: directory
        :param filter: 过滤列表
        :param initialFilter: 默认的过滤条件
        :return: 文件路径
        """
        (filePath, _) = QtWidgets.QFileDialog.getOpenFileName(caption=caption, directory=directory, filter=filter, initialFilter=initialFilter)
        print("选择的文件： " + filePath)
        return filePath

    @staticmethod
    def getExistingDirectory(caption='', directory=''):
        """
        打开一个文件夹弹框选择一个指定的文件夹
        :param caption: 标题
        :param directory: directory
        :return: 文件夹路径
        """
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(caption=caption, directory=directory)
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
    def createSplitter(parent: QWidget = None, isVertical=False, objectName="Splitter", toolTip=None,
                       geometry: QRect = None, minSize: QSize = None, sizePolicy: QSizePolicy = None):
        """
        创建一个动态的布局管理器
        :param parent: 父QWidget
        :param isVertical: True 垂直方向
        :param objectName: objectName
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param sizePolicy: 缩放策略
        :return: QSplitter
        """
        widget = QtWidgets.QSplitter()
        if parent:
            widget.setParent(parent)
        if isVertical:
            widget.setOrientation(Qt.Vertical)
        else:
            widget.setOrientation(Qt.Horizontal)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, sizePolicy=sizePolicy)
        return widget

    @staticmethod
    def createLabel(parent: QWidget, objectName="Label", text="", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                    geometry: QRect = None, minSize: QSize = None, sizePolicy: QSizePolicy = None):
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
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, margins=margins,
                       sizePolicy=sizePolicy)
        widget.setTitle(_translate(contextName, title))
        if margins:
            widget.setContentsMargins(margins)
        return widget

    @staticmethod
    def createButtonGroup(onToggled=None):
        """
        创建一个QButtonGroup，给RadioButton分组
        :param onToggled: toggled checked状态切换回调
        :return: QButtonGroup
        """
        widget = QtWidgets.QButtonGroup()
        if onToggled:
            widget.buttonClicked.connect(onToggled)
        return widget

    @staticmethod
    def createRadioButton(parent: QWidget, objectName="RadioButton", text="RadioButton", toolTip=None, isEnable=True,
                          autoExclusive=True, isChecked=False, geometry: QRect = None, sizePolicy: QSizePolicy = None,
                          onToggled=None):
        """
        创建一个单选按钮
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param isEnable: enable
        :param autoExclusive: autoExclusive False 独立到，True 同一个父widget到为一组
        :param isChecked: isChecked 默认是否选中，true选中
        :param geometry: geometry
        :param sizePolicy: 缩放策略
        :param onToggled: toggled checked状态切换回调
        :return: 单选按钮
        """
        widget = QRadioButton(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        widget.setText(_translate(contextName, text))
        widget.setAutoExclusive(autoExclusive)
        widget.setChecked(isChecked)
        if onToggled:
            widget.toggled.connect(onToggled)
        return widget

    @staticmethod
    def createPushButton(parent: QWidget, objectName="PushButton", text="PushButton", toolTip=None,
                         geometry: QRect = None, minSize: QSize = None,
                         sizePolicy: QSizePolicy = None, onClicked=None):
        """
        创建一个Button
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param sizePolicy: 缩放策略
        :param onClicked: clicked回调函数
        :return: QPushButton
        """
        widget = QtWidgets.QPushButton(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, sizePolicy=sizePolicy)
        widget.setText(_translate(contextName, text))
        if onClicked:
            widget.clicked.connect(onClicked)
        return widget

    @staticmethod
    def createLineEdit(parent: QWidget, objectName="LineEdit", text="", holderText="", toolTip=None,
                       geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None, textChanged=None):
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
        :param textChanged: 输入内容变化监听函数
        :return: QLineEdit
        """
        widget = QtWidgets.QLineEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        if holderText:
            widget.setPlaceholderText(_translate(contextName, holderText))
        if text:
            widget.setText(_translate(contextName, text))
        if textChanged:
            widget.textChanged.connect(textChanged)
        return widget

    @staticmethod
    def createTextEdit(parent: QWidget, objectName="TextEdit", text="", holderText="", toolTip=None,
                       geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个多行文本输入框
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param holderText: holderText
        :param toolTip: toolTip
        :param geometry: geometry
        :param isEnable: enable
        :param sizePolicy: 缩放策略
        :return: 多行文本输入框
        """
        widget = QtWidgets.QTextEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        if holderText:
            widget.setPlaceholderText(_translate(contextName, holderText))
        if text:
            widget.setText(_translate(contextName, text))
        return widget

    @staticmethod
    def createTreeWidget(parent: QWidget, objectName="TreeWidget", toolTip=None, headerLabels=['格式化数据'],
                         geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个树形结构的展示控件
        :param parent: 父QWidget
        :param objectName: objectName
        :param toolTip: toolTip
        :param headerLabels: headerLabels
        :param geometry: geometry
        :param isEnable: enable
        :param sizePolicy: 缩放策略
        :return: 树形结构的展示控件
        """
        widget = QTreeWidget(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        # 设置树形控件头部的标题
        widget.setHeaderLabels(headerLabels)
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        return widget

    @staticmethod
    def createTreeWidgetItem(key="", value=None, keyBg: QBrush = None, valueBg: QBrush = None, keyIconPath=None,
                             isLeafNode=False, disable=False):
        """
        创建一个树形结构的展示控件item元素
        :param key: key
        :param value: value
        :param keyBg: keyBg
        :param valueBg: valueBg
        :param keyIconPath: keyIconPath
        :param isLeafNode: 是否末端节点
        :param disable: disable
        :return: 树形结构的展示控件item元素
        """
        widget = QTreeWidgetItem()
        widget.setText(0, str(key))
        widget.setDisabled(disable)
        widget.setData(0, Qt.UserRole, isLeafNode)
        widget.setData(1, Qt.UserRole, DataTypeUtil.type(key))
        if value is not None:
            widget.setText(1, str(value))
        if keyIconPath:
            widget.setIcon(0, QIcon(keyIconPath))
        if keyBg:
            widget.setBackground(0, keyBg)
        if valueBg:
            widget.setBackground(1, valueBg)
        return widget

    @staticmethod
    def setTreeWidgetJsonData(treeWidget: QTreeWidget, data={}, isExpand=True):
        """
        给TreeWidget设置数据
        :param treeWidget: TreeWidget
        :param data: json数据
        :param isExpand: isExpand是否全部展开
        """
        treeWidget.clear()
        root = None
        if DataTypeUtil.isDict(data):
            root = WidgetUtil.createTreeWidgetItem("{}")
        elif DataTypeUtil.isList(data):
            root = WidgetUtil.createTreeWidgetItem("[]")
        else:
            print("data is not json data")
            return
        items = WidgetUtil.createTreeWidgetItems(data)
        root.addChildren(items)
        treeWidget.addTopLevelItem(root)
        if isExpand:
            treeWidget.expandAll()
        pass

    @staticmethod
    def createTreeWidgetItems(data={}):
        """
        根据data创建TreeWidgetItems
        :param data: json数据
        :return: TreeWidgetItems
        """
        L = []
        if DataTypeUtil.isDict(data):
            for key, value in data.items():
                parent = WidgetUtil.createTreeWidgetItem(key)
                if DataTypeUtil.isList(value) or DataTypeUtil.isDict(value):
                    childList = WidgetUtil.createTreeWidgetItems(value)
                    if childList:
                        parent.addChildren(childList)
                else:
                    child = WidgetUtil.createTreeWidgetItem(value, isLeafNode=True)
                    parent.addChild(child)
                L.append(parent)
        elif DataTypeUtil.isList(data):
            for item in data:
                if DataTypeUtil.isList(item) or DataTypeUtil.isDict(item):
                    parent = None
                    if DataTypeUtil.isList(item):
                        parent = WidgetUtil.createTreeWidgetItem("[]")
                    else:
                        parent = WidgetUtil.createTreeWidgetItem("{}")
                    childList = WidgetUtil.createTreeWidgetItems(item)
                    if parent:
                        for child in childList:
                            parent.addChild(child)
                    else:
                        parent = childList
                    L.append(parent)
                else:
                    item = WidgetUtil.createTreeWidgetItem(item, isLeafNode=True)
                    L.append(item)
        else:
            LogUtil.e("err data is not dict or list")
        return L

    @staticmethod
    def getTreeWidgetJsonData(treeWidget: QTreeWidget):
        """
        从TreeWidget解析出json数据
        :param treeWidget: treeWidget
        :return: json数据
        """
        if treeWidget.topLevelItemCount() > 0:
            root: QTreeWidgetItem = treeWidget.topLevelItem(0)
            jsonData = WidgetUtil.getTreeWidgetItemJsonData(root)
            print(jsonData)
        return None
        pass

    @staticmethod
    def getTreeWidgetItemJsonData(treeWidgetItem: QTreeWidgetItem):
        """
        从TreeWidgetItem解析出json数据
        :param treeWidgetItem: treeWidgetItem
        :return: json数据
        """
        text = treeWidgetItem.text(0)
        if text == "[]":
            jsonData = []
            for i in range(0, treeWidgetItem.childCount()):
                res = WidgetUtil.getTreeWidgetItemJsonData(treeWidgetItem.child(i))
                jsonData.append(res)
            print(jsonData)
            return jsonData
        elif text == "{}":
            jsonData = {}
            for i in range(0, treeWidgetItem.childCount()):
                child = treeWidgetItem.child(i)
                res = WidgetUtil.getTreeWidgetItemJsonData(child)
                print("root key: " + child.text(0) + " value: " + str(res))
                jsonData = {**jsonData, **res}
            print(jsonData)
            return jsonData
        elif treeWidgetItem.data(0, Qt.UserRole):
            # 末端节点
            dataType = treeWidgetItem.data(1, Qt.UserRole)
            print(DataTypeUtil.parseByType(text, dataType))
            res = DataTypeUtil.parseByType(text, dataType)
            print("末端节点 -> %s dataType -> %d parse res -> %s" % (text, dataType, str(res)))
            return res
        else:
            jsonData = {}
            list = []
            for i in range(0, treeWidgetItem.childCount()):
                child = treeWidgetItem.child(i)
                res = WidgetUtil.getTreeWidgetItemJsonData(child)
                list.append(res)
            if len(list) == 1:
                jsonData[text] = list[0]
            else:
                jsonData[text] = list
            print(jsonData)
            return jsonData

    @staticmethod
    def createAction(parent: QMenu, text="添加", func=None):
        """
        创建一个菜单action
        :param parent: QMenu
        :param text: 显示文本
        :param func: 触发回调函数
        :return: QAction
        """
        action = QtWidgets.QAction(text, parent)
        if func:
            action.triggered.connect(func)
        return action

    @staticmethod
    def createMenu(action1="添加", func1=None, action2=None, func2=None, action3=None, func3=None):
        """
        创建一个菜单
        :param action1: action1
        :param func1: 回调函数1
        :param action2: action2
        :param func2: 回调函数2
        :param action3: action3
        :param func3: 回调函数3
        :return: QMenu
        """
        widget = QMenu()
        widget.addAction(WidgetUtil.createAction(widget, action1, func1))
        if action2:
            widget.addAction(WidgetUtil.createAction(widget, action2, func2))
        if action3:
            widget.addAction(WidgetUtil.createAction(widget, action3, func3))
        return widget

    @staticmethod
    def createTableView(parent: QWidget, objectName="TreeWidget", toolTip=None, geometry: QRect = None, minSize: QSize = None,
                        isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个QTableView
        :param parent: 父QWidget
        :param objectName: objectName
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param isEnable: isEnable
        :param sizePolicy: 缩放策略
        :return: QTableView
        """
        widget = QTableView(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, isEnable=isEnable, sizePolicy=sizePolicy)

        # 水平方向标签拓展剩下的窗口部分，填满表格
        widget.horizontalHeader().setStretchLastSection(True)
        # 水平方向，表格大小拓展到适当的尺寸
        widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return widget

    @staticmethod
    def addTableViewData(tableView: QTableView, data=[{}]):
        """
        TableView设置数据
        :param tableView: QTableView
        :param data: 数据源
        """
        if data:
            rows = len(data)
            cols = len(data[0])
            # 设置数据层次结构，rows行cols列
            model = QStandardItemModel(rows, cols)
            headerLabels = []
            for key in data[0]:
                headerLabels.append(key)
            # 设置水平方向头标签文本内容
            model.setHorizontalHeaderLabels(headerLabels)

            for row in range(rows):
                column = 0
                for value in data[row].values():
                    item = QStandardItem(value)
                    # 设置每个位置的文本值
                    model.setItem(row, column, item)
                    column = column + 1

            # 实例化表格视图，设置模型为自定义的模型
            tableView.setModel(model)
        else:
            LogUtil.e("data is empty")

    @classmethod
    def translate(cls, context=contextName, text=""):
        return _translate(context, text)
