# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetUtil.py
# 定义一个WidgetUtil工具类实现Widget相关的功能
from typing import Union

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QBrush, QStandardItemModel, QStandardItem, QColor, QKeySequence, QFont
from PyQt5.QtWidgets import QWidget, QMessageBox, QSizePolicy, QTreeWidget, QMenu, QTreeWidgetItem, QDialog, \
    QRadioButton, QTableView, QHeaderView, QColorDialog, QSpinBox, QTextEdit, QApplication, QDoubleSpinBox, QMenuBar, \
    QTabWidget, QCheckBox, QProgressBar, QComboBox, QDialogButtonBox, QLineEdit, QLayout, QWidgetItem, QSpacerItem, \
    QLayoutItem
from PyQt5.QtCore import QRect, QMargins, QSize, Qt, QDateTime, QObject
from constant.WidgetConst import *
from util.LogUtil import *
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
    screenRect = None

    @staticmethod
    def getScreenRect():
        # 获取显示器分辨率
        if not WidgetUtil.screenRect:
            WidgetUtil.screenRect = QApplication.desktop().screenGeometry()
            LogUtil.d(f"Screen width {WidgetUtil.screenRect.width()}\nScreen height {WidgetUtil.screenRect.height()}")
        return WidgetUtil.screenRect

    @staticmethod
    def getScreenHeight():
        return WidgetUtil.getScreenRect().height()

    @staticmethod
    def getScreenWidth():
        return WidgetUtil.getScreenRect().width()

    @staticmethod
    def getColor():
        """
        打开一个颜色选择弹框
        :return: 选择的颜色值
        """
        qColor: QColor = QColorDialog.getColor()
        if qColor.isValid():
            return qColor.name()
        return None

    @staticmethod
    def getOpenFileName(parent=None, caption='', directory='', filter='', initialFilter=''):
        """
        打开一个文件弹框选择一个指定的文件
        :param parent: 父窗口
        :param caption: 标题
        :param directory: directory
        :param filter: 过滤列表
        :param initialFilter: 默认的过滤条件
        :return: 文件路径
        """
        (filePath, _) = QtWidgets.QFileDialog.getOpenFileName(parent=parent, caption=caption, directory=directory,
                                                              filter=filter,
                                                              initialFilter=initialFilter)
        print("选择的文件： " + filePath)
        return filePath

    @staticmethod
    def getExistingDirectory(parent=None, caption='', directory=''):
        """
        打开一个文件夹弹框选择一个指定的文件夹
        :param parent: 父窗口
        :param caption: 标题
        :param directory: directory
        :return: 文件夹路径
        """
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(parent=parent, caption=caption, directory=directory)
        print("选择的目录： " + dirPath)
        return dirPath

    @staticmethod
    def showAboutDialog(parent=None, caption="About", text=""):
        """
        显示about提示弹框
        :param parent: 父widget
        :param caption: 标题
        :param text: 提示文本
        """
        QMessageBox.about(parent, caption, text)

    @staticmethod
    def showInformationDialog(parent=None, title="Information", text="",
                              buttons: Union[QMessageBox.StandardButtons, QMessageBox.StandardButton] = QMessageBox.Ok,
                              defaultButton: QMessageBox.StandardButton = QMessageBox.NoButton) -> QMessageBox.StandardButton:
        """
        显示Information提示弹框
        :param parent: 父widget
        :param title: 标题
        :param text: 提示文本
        :param buttons: buttons
        :param defaultButton: defaultButton
        """
        return QMessageBox.information(parent, title, text, buttons, defaultButton)

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
    def createHBoxLayout(parent: QWidget = None, objectName="HBoxLayout", margins: QMargins = None,
                         spacing: int = None, alignment: Union[Qt.Alignment, Qt.AlignmentFlag] = None):
        """
        创建一个水平布局容器
        :param parent: 父QWidget
        :param objectName: objectName
        :param margins: margin值
        :param spacing: spacing值
        :param alignment: 文本对其方式，默认左居中
        :return: QHBoxLayout
        """
        if parent:
            layout = QtWidgets.QHBoxLayout(parent)
        else:
            layout = QtWidgets.QHBoxLayout()
        layout.setObjectName(objectName)
        if margins:
            layout.setContentsMargins(margins)
        if spacing:
            layout.setSpacing(spacing)
        if alignment:
            layout.setAlignment(alignment)
        return layout

    @staticmethod
    def createVBoxLayout(parent: QWidget = None, objectName="VBoxLayout", margins: QMargins = None,
                         spacing: int = None, alignment: Union[Qt.Alignment, Qt.AlignmentFlag] = None):
        """
        创建一个垂直布局容器
        :param parent: 父QWidget
        :param objectName: objectName
        :param margins: margin值
        :param spacing: spacing值
        :param alignment: 文本对其方式，默认左居中
        :return: QVBoxLayout
        """
        if parent:
            layout = QtWidgets.QVBoxLayout(parent)
        else:
            layout = QtWidgets.QVBoxLayout()
        layout.setObjectName(objectName)
        if margins:
            layout.setContentsMargins(margins)
        if spacing:
            layout.setSpacing(spacing)
        if alignment:
            layout.setAlignment(alignment)
        return layout

    @staticmethod
    def createHSpacerItem(w: int = 1, h: int = 1):
        """
        创建一个水平垫片容器，用于占位空间
        :param w: 宽度
        :param h: 高度
        :return: QSpacerItem
        """
        return QtWidgets.QSpacerItem(w, h, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

    @staticmethod
    def createVSpacerItem(w: int = 1, h: int = 1):
        """
        创建一个垂直垫片容器，用于占位空间
        :param w: 宽度
        :param h: 高度
        :return: QSpacerItem
        """
        return QtWidgets.QSpacerItem(w, h, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

    @staticmethod
    def createVBoxWidget(parent: QWidget, margins: QMargins = None, geometry: QRect = None,
                         sizePolicy: QSizePolicy = None):
        """
        创建一个Widget使用垂直布局容器
        :param parent: 父QWidget
        :param margins: VBoxLayout margin值
        :param geometry: QWidget geometry
        :param sizePolicy: 缩放策略
        :return: QVBoxLayout
        """
        layoutWidget = QtWidgets.QWidget(parent)
        layoutWidget.setObjectName("layoutWidget")
        if geometry:
            layoutWidget.setGeometry(geometry)
        layout = WidgetUtil.createVBoxLayout(margins=margins)
        layoutWidget.setLayout(layout)
        if sizePolicy:
            layoutWidget.setSizePolicy(sizePolicy)
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
    def createWidget(parent: QWidget = None, objectName='Widget', toolTip=None, geometry: QRect = None,
                     minSize: QSize = None, margins: QMargins = None, isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个QWidget对象
        :param parent: 父QWidget
        :param objectName: objectName
        :param toolTip: toolTip
        :param geometry: 位置尺寸
        :param minSize: 最小size
        :param margins: margin值
        :param isEnable: Enabled
        :param sizePolicy: 缩放策略
        :return: QWidget
        """
        widget = QWidget()
        if parent:
            widget.setParent(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, margins=margins,
                       isEnable=isEnable, sizePolicy=sizePolicy)
        return widget

    @staticmethod
    def createSpinBox(parent: QWidget = None, objectName="SpinBox", value=None, minValue=None, maxValue=None, step=None,
                      prefix=None, suffix=None, intBase=None, toolTip=None, geometry: QRect = None,
                      minSize: QSize = None, isEnable=True, sizePolicy: QSizePolicy = None, valueChanged=None):
        """
        创建一个计数器控件 - 用于整数的显示和输入，一般显示十进制数，也可以显示二进制、十六进制的数，而且可以在显示框中增加前缀或后缀。
        :param parent: 父QWidget
        :param objectName: objectName
        :param value: 当前值
        :param minValue: 最小值
        :param maxValue: 最大值
        :param step: 步长
        :param prefix: 前缀
        :param suffix: 后缀
        :param intBase: 显示整数使用的进制，例如 2 就表示二进制
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param isEnable: isEnable
        :param sizePolicy: 缩放策略
        :param valueChanged: 数值改变监听函数
        :return: QSpinBox
        """
        widget = QSpinBox()
        if parent:
            widget.setParent(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, isEnable=isEnable,
                       sizePolicy=sizePolicy)
        if value:
            widget.setValue(value)
        if minValue:
            widget.setMinimum(minValue)
        if maxValue:
            widget.setMaximum(maxValue)
        if step:
            widget.setSingleStep(step)
        if prefix:
            widget.setPrefix(prefix)
        if suffix:
            widget.setSuffix(suffix)
        if intBase:
            widget.setDisplayIntegerBase(intBase)
        if valueChanged:
            widget.valueChanged.connect(valueChanged)
        return widget

    @staticmethod
    def createDoubleSpinBox(parent: QWidget = None, objectName="SpinBox", value=None, minValue=None, maxValue=None,
                            step=None, prefix=None, suffix=None, decimals=2, toolTip=None, geometry: QRect = None,
                            minSize: QSize = None, isEnable=True, sizePolicy: QSizePolicy = None, valueChanged=None):
        """
        创建一个计数器控件 - 用于整数的显示和输入，一般显示十进制数，也可以显示二进制、十六进制的数，而且可以在显示框中增加前缀或后缀。
        :param parent: 父QWidget
        :param objectName: objectName
        :param value: 当前值
        :param minValue: 最小值
        :param maxValue: 最大值
        :param step: 步长
        :param prefix: 前缀
        :param suffix: 后缀
        :param decimals: 显示数值的小数位数，例如 2 就显示两位小数
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param isEnable: isEnable
        :param sizePolicy: 缩放策略
        :param valueChanged: 数值改变监听函数
        :return: QDoubleSpinBox
        """
        widget = QDoubleSpinBox()
        if parent:
            widget.setParent(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, isEnable=isEnable,
                       sizePolicy=sizePolicy)
        if value:
            widget.setValue(value)
        if minValue:
            widget.setMinimum(minValue)
        if maxValue:
            widget.setMaximum(maxValue)
        if step:
            widget.setSingleStep(step)
        if prefix:
            widget.setPrefix(prefix)
        if suffix:
            widget.setSuffix(suffix)
        if decimals:
            widget.setDecimals(decimals)
        if valueChanged:
            widget.valueChanged.connect(valueChanged)
        return widget

    @staticmethod
    def createLabel(parent: QWidget, objectName="Label", text="", toolTip=None,
                    alignment=Qt.AlignVCenter | Qt.AlignLeft,
                    geometry: QRect = None, minSize: QSize = None, sizePolicy: QSizePolicy = None):
        """
        创建一个Label标签
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param alignment: 文本对其方式，默认左居中
        :param geometry: geometry
        :param minSize: minSize
        :param sizePolicy: 缩放策略
        :return: QLabel
        """
        widget = QtWidgets.QLabel(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, sizePolicy=sizePolicy)
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
    def createButtonGroup(buttonClicked=None, exclusive=True):
        """
        创建一个QButtonGroup，给RadioButton分组
        :param buttonClicked: 群组中按钮点击回调
        :param exclusive: False 独立，True 同一个父widget为一组，选中一个会取消其他按钮的选中状态
        :return: QButtonGroup
        """
        widget = QtWidgets.QButtonGroup()
        if buttonClicked:
            widget.buttonClicked.connect(buttonClicked)
        widget.setExclusive(exclusive)
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
        :param autoExclusive: autoExclusive False 独立，True 同一个父widget为一组
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
    def createCheckBox(parent: QWidget, objectName="RadioButton", text="RadioButton", toolTip=None, isEnable=True,
                       autoExclusive=False, isChecked=False, geometry: QRect = None, sizePolicy: QSizePolicy = None,
                       stateChanged=None, clicked=None):
        """
        创建一个复选框
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param isEnable: enable
        :param autoExclusive: autoExclusive False 独立，True 同一个父widget为一组
        :param isChecked: isChecked 默认是否选中，true选中
        :param geometry: geometry
        :param sizePolicy: 缩放策略
        :param stateChanged: toggled checked状态切换回调，不管是用户点击还是代码设置选中状态
        :param clicked: 用户点击时触发
        :return: 复选框
        """
        widget = QCheckBox(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        widget.setText(_translate(contextName, text))
        widget.setAutoExclusive(autoExclusive)
        widget.setChecked(isChecked)
        font = QFont()
        font.setBold(isChecked)
        widget.setFont(font)
        if stateChanged:
            widget.stateChanged.connect(lambda: (
                stateChanged(),
                font.setBold(widget.isChecked()),
                widget.setFont(font)
            ))
        if clicked:
            widget.clicked.connect(lambda: (
                clicked(),
                font.setBold(widget.isChecked()),
                widget.setFont(font)
            ))
        return widget

    @staticmethod
    def createComboBox(parent: QWidget, objectName="QComboBox", toolTip=None, isEnable=True, isEditable=False,
                       geometry: QRect = None, sizePolicy: QSizePolicy = None, currentIndexChanged=None,
                       activated=None):
        """
        创建一个下拉选择框
        :param parent: 父QWidget
        :param objectName: objectName
        :param toolTip: toolTip
        :param isEnable: enable
        :param isEditable: editable
        :param geometry: geometry
        :param sizePolicy: 缩放策略
        :param currentIndexChanged: 改变当前索引触发，包括代码里设置索引
        :param activated: 用户选中下拉列表某一项触发，编辑和代码改变索引时不会触发
        :return: 下拉选择框
        """
        widget = QComboBox(parent)
        widget.setEditable(isEditable)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        if currentIndexChanged:
            widget.currentIndexChanged[int].connect(currentIndexChanged)
        if activated:
            widget.activated[int].connect(activated)
        return widget

    @staticmethod
    def createPushButton(parent: QWidget, objectName="PushButton", text="PushButton", toolTip=None,
                         fixedSize: QSize = None, geometry: QRect = None, minSize: QSize = None, isEnable=True,
                         styleSheet: str = None, iconSize: QSize = None, icon: QIcon = None,
                         sizePolicy: QSizePolicy = None, onClicked=None):
        """
        创建一个Button
        :param parent: 父QWidget
        :param objectName: objectName
        :param text: text
        :param toolTip: toolTip
        :param fixedSize: 固定大小
        :param geometry: geometry
        :param minSize: minSize
        :param isEnable: isEnable
        :param styleSheet: 样式表 设置按钮样式
        :param iconSize: 图标大小
        :param icon: 图标
        :param sizePolicy: 缩放策略
        :param onClicked: clicked回调函数
        :return: QPushButton
        """
        widget = QtWidgets.QPushButton(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, isEnable=isEnable,
                       sizePolicy=sizePolicy)
        widget.setText(_translate(contextName, text))
        if fixedSize:
            widget.setFixedSize(fixedSize)
        if styleSheet:
            widget.setStyleSheet(styleSheet)
        if iconSize:
            widget.setIconSize(iconSize)
        if icon:
            widget.setIcon(icon)
        if onClicked:
            widget.clicked.connect(onClicked)
        return widget

    @staticmethod
    def createLineEdit(parent: QWidget, objectName="LineEdit", text="", holderText="", toolTip=None,
                       geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None, textChanged=None,
                       isReadOnly=False, echoMode: QLineEdit.EchoMode = None, editingFinished=None):
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
        :param isReadOnly: 是否只读不能编辑
        :param echoMode: 显示模式
        :param editingFinished: 编辑结束
        :return: QLineEdit
        """
        widget = QtWidgets.QLineEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        if holderText:
            widget.setPlaceholderText(_translate(contextName, holderText))
            if not toolTip:
                widget.setToolTip(_translate(contextName, holderText))
        if text:
            widget.setText(_translate(contextName, text))
        if textChanged:
            widget.textChanged.connect(textChanged)
        if echoMode:
            widget.setEchoMode(echoMode)
        if editingFinished:
            widget.editingFinished.connect(editingFinished)
        widget.setReadOnly(isReadOnly)
        return widget

    @staticmethod
    def createTextEdit(parent: QWidget, objectName="TextEdit", text="", holderText="", toolTip=None,
                       geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None, isReadOnly=False):
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
        :param isReadOnly: 是否只读不能编辑
        :return: 多行文本输入框
        """
        widget = QtWidgets.QTextEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        widget.setReadOnly(isReadOnly)
        if holderText:
            widget.setPlaceholderText(_translate(contextName, holderText))
        if text:
            widget.setText(_translate(contextName, text))
        return widget

    @staticmethod
    def createDateTimeEdit(parent: QWidget, objectName="DateTimeEdit",
                           dateTime: QDateTime = QDateTime.currentDateTime(), minDateTime=None, maxDateTime=None,
                           displayFormat: str = "yyyy-MM-dd HH:mm:ss", toolTip=None, onDateTimeChanged=None,
                           geometry: QRect = None, isEnable=True, sizePolicy: QSizePolicy = None):
        """
        创建一个日期格式输入框
        :param parent: 父QWidget
        :param objectName: objectName
        :param dateTime: 显示的时间
        :param minDateTime: 日期最小值
        :param maxDateTime: 日期最大值
        :param displayFormat: 日期显示格式
        :param toolTip: toolTip
        :param onDateTimeChanged: 日期时间改变时触发槽函数
        :param geometry: geometry
        :param isEnable: enable
        :param sizePolicy: 缩放策略
        :return: 多行文本输入框
        """
        widget = QtWidgets.QDateTimeEdit(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, isEnable=isEnable, sizePolicy=sizePolicy)
        widget.setDateTime(dateTime)
        widget.setDisplayFormat(displayFormat)
        # 设置日期最大值与最小值
        if minDateTime:
            widget.setMinimumDateTime(minDateTime)
        if maxDateTime:
            widget.setMaximumDateTime(maxDateTime)
        # 设置日历控件允许弹出
        widget.setCalendarPopup(True)
        # 当日期时间改变时触发槽函数
        if onDateTimeChanged:
            widget.dateTimeChanged.connect(onDateTimeChanged)
        return widget

    @staticmethod
    def textEditAppendMessage(textEdit: QTextEdit, text: str, color='#00f'):
        """
        向QTextEdit控件添加文字（指定颜色，默认蓝色）
        :param textEdit: QTextEdit控件
        :param text: 文本
        :param color: 颜色值
        :return: None
        """
        textFormat = f'<div style="color: {color}">{WidgetUtil.specialCharTransform(text)}</div>'
        textEdit.append(textFormat)
        # 触发实时显示数据
        QApplication.instance().processEvents()
        pass

    @staticmethod
    def textEditAppendMessages(textEdit: QTextEdit, messages: list[dict]):
        """
        批量向QTextEdit控件添加文字（指定颜色）
        :param textEdit: QTextEdit控件
        :param messages: 需要输出的信息列表(log, color)
        :return: None
        """
        textFormat = ""
        for msg in messages:
            textFormat += f'<div style="color: {msg[KEY_COLOR]}">{WidgetUtil.specialCharTransform(msg[KEY_LOG])}</div>'
        textEdit.append(textFormat)
        # 触发实时显示数据
        QApplication.instance().processEvents()
        pass

    @staticmethod
    def specialCharTransform(text: str):
        if '</a>' in text or '</span>' in text:
            return text
        return text.replace("\r\n", "<br/>").replace("\n", "<br/>").replace(" ", "&nbsp;")

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
    def createAction(parent: Union[QMenu, QMenuBar, QWidget], icon: QIcon = None, text="添加", func=None,
                     shortcut: Union[QKeySequence, QKeySequence.StandardKey, str, int] = None,
                     statusTip: str = None):
        """
        创建一个菜单action
        :param parent: QMenu、QMenuBar
        :param icon: 图标
        :param text: 显示文本
        :param func: 触发回调函数
        :param shortcut: 快捷键
        :param statusTip: 状态栏信息文本
        :return: QAction
        """
        action = QtWidgets.QAction(parent)
        if icon:
            action.setIcon(icon)
        if text:
            action.setText(text)
        if func:
            action.triggered.connect(func)
        if shortcut:
            action.setShortcut(shortcut)
        if statusTip:
            action.setStatusTip(statusTip)
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
        widget.addAction(WidgetUtil.createAction(parent=widget, text=action1, func=func1))
        if action2:
            widget.addAction(WidgetUtil.createAction(parent=widget, text=action2, func=func2))
        if action3:
            widget.addAction(WidgetUtil.createAction(parent=widget, text=action3, func=func3))
        return widget

    @staticmethod
    def createTableView(parent: QWidget, objectName="TreeWidget", toolTip=None, geometry: QRect = None,
                        minSize: QSize = None, isEnable=True, sizePolicy: QSizePolicy = None, clicked=None,
                        doubleClicked=None, isResizeToContents=False):
        """
        创建一个QTableView
        :param parent: 父QWidget
        :param objectName: objectName
        :param toolTip: toolTip
        :param geometry: geometry
        :param minSize: minSize
        :param isEnable: isEnable
        :param sizePolicy: 缩放策略
        :param clicked: 单击回调函数
        :param doubleClicked: 双击回调函数
        :param isResizeToContents: 是否根据列内容来定列宽
        :return: QTableView
        """
        widget = QTableView(parent)
        widgetSetAttrs(widget, objectName, toolTip=toolTip, geometry=geometry, minSize=minSize, isEnable=isEnable,
                       sizePolicy=sizePolicy)

        # 水平方向标签拓展剩下的窗口部分，填满表格
        widget.horizontalHeader().setStretchLastSection(True)
        if isResizeToContents:
            # 根据列内容来定列宽
            widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        else:
            # 水平方向，表格大小拓展到适当的尺寸 所有列都扩展自适应宽度，填充充满整个屏幕宽度
            widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        if clicked:
            widget.clicked.connect(clicked)
        if doubleClicked:
            widget.doubleClicked.connect(doubleClicked)
        return widget

    @staticmethod
    def tableViewSetColumnWidth(tableView: QTableView, column: int = 0, width: int = 80):
        """
        设置tableView某行宽度为固定宽度，在设置数据后调用
        :param tableView: QTableView
        :param column: 列index
        :param width: 宽度值
        """
        # 对第column列单独设置固定宽度
        tableView.horizontalHeader().setSectionResizeMode(column, QHeaderView.Fixed)
        # 设置固定宽度
        tableView.setColumnWidth(column, width)

    @staticmethod
    def addTableViewData(tableView: QTableView, data=[{}], ignoreCol=[], headerLabels: [] = None, itemChanged=None):
        """
        TableView设置数据
        :param tableView: QTableView
        :param data: 数据源
        :param ignoreCol: 需要忽略的数据列列表
        :param headerLabels: 列表头部标题
        :param itemChanged: 单元格内容变化监听函数
        """
        if data:
            rows = len(data)
            cols = len(data[0])
            # 忽略的列数
            ignoreColCount = 0
            for key in data[0]:
                if key in ignoreCol:
                    ignoreColCount = ignoreColCount + 1
            cols = cols - ignoreColCount
            # 设置数据层次结构，rows行cols列
            model = QStandardItemModel(rows, cols)
            if not headerLabels:
                headerLabels = []
                for key in data[0]:
                    if not (key in ignoreCol):
                        headerLabels.append(key)
            # 设置水平方向头标签文本内容
            model.setHorizontalHeaderLabels(headerLabels)

            for row in range(rows):
                column = 0
                for key, value in data[row].items():
                    if not (key in ignoreCol):
                        item = QStandardItem(str(value))
                        item.setToolTip(str(value))
                        # 设置每个位置的文本值
                        model.setItem(row, column, item)
                        column = column + 1
            if itemChanged:
                model.itemChanged.connect(itemChanged)
            # 实例化表格视图，设置模型为自定义的模型
            tableView.setModel(model)
        else:
            model = tableView.model()
            if model:
                model.removeRows(0, model.rowCount())
            if headerLabels:
                model = QStandardItemModel(0, len(headerLabels))
                # 设置水平方向头标签文本内容
                model.setHorizontalHeaderLabels(headerLabels)
                tableView.setModel(model)
            LogUtil.e("data is empty")

    @staticmethod
    def createTabWidget(parent: QWidget = None):
        """
        创建一个选项卡 QTabWidget
        :param parent: 父QWidget
        :return: QTabWidget
        """
        widget = QTabWidget(parent)
        return widget

    @staticmethod
    def createProgressBar(parent: QWidget = None, value: int = 0, minValue: int = 0, maxValue: int = 100,
                          orientation: Qt.Orientation = Qt.Horizontal, format: str = None,
                          alignment: Qt.Alignment = Qt.AlignHCenter, textVisible: bool = True,
                          textDirection: QProgressBar.Direction = None, invertedAppearance: bool = False,
                          sizePolicy: QSizePolicy = None, valueChanged=None):
        """
        创建一个进度条 QProgressBar
        :param parent: 父QWidget
        :param value: 设置当前值——显示进度
        :param minValue: 最小值
        :param maxValue: 最大值
        :param orientation: 进度条方向 Qt.Horizontal | Qt.Vertical
        :param format: %p 百分比 %v 当前值 %m 总值 eg: 当前人数/总人数%p% 当前人数%v/总人数%m
        :param alignment: 设置标识在进度条的位置
        :param textVisible: 文本标签 Visible
        :param textDirection: 文本方向 仅仅对垂直进度条有效 Visible QProgressBar.TopToBottom | QProgressBar.BottomToTop
        :param invertedAppearance: True 倒立外观
        :param sizePolicy: 缩放策略
        :param valueChanged: 数值改变监听函数
        :return: QProgressBar
        """
        widget = QProgressBar(parent)
        widget.setOrientation(orientation)
        if value:
            widget.setValue(value)
        if minValue:
            widget.setMinimum(minValue)
        if maxValue:
            widget.setMaximum(maxValue)
        # 格式设置
        if format:
            widget.setFormat(format)
        if alignment:
            widget.setAlignment(alignment)
        # 文本操作+方向
        widget.setTextVisible(textVisible)
        if textDirection:
            widget.setTextDirection(textDirection)
        widget.setInvertedAppearance(invertedAppearance)
        if sizePolicy:
            widget.setSizePolicy(sizePolicy)
        if valueChanged:
            widget.valueChanged.connect(valueChanged)
        return widget

    @staticmethod
    def createDialogButtonBox(standardButton: Union[
        QDialogButtonBox.StandardButtons, QDialogButtonBox.StandardButton] = QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                              orientation: Qt.Orientation = QtCore.Qt.Horizontal, parent: QWidget = None,
                              objectName="QDialogButtonBox", isCenter=False, acceptedFunc=None, rejectedFunc=None,
                              clickedFunc=None):
        btnBox = QDialogButtonBox(standardButton, orientation, parent)
        btnBox.setObjectName(objectName)
        btnBox.setCenterButtons(isCenter)
        if acceptedFunc:
            btnBox.accepted.connect(acceptedFunc)
        if rejectedFunc:
            btnBox.rejected.connect(rejectedFunc)
        if clickedFunc:
            btnBox.clicked.connect(clickedFunc)
        return btnBox
        pass

    @staticmethod
    def removeAllChild(parent: QLayout):
        """
        移除控件下所有的子组件
        :param parent: 父控件
        """
        if not isinstance(parent, QWidgetItem) and not isinstance(parent, QSpacerItem):
            while len(parent.children()) > 0:
                child = parent.children()[0]
                WidgetUtil.removeChild(parent, child)

    @staticmethod
    def removeChild(parent: QLayout, child: QObject):
        """
        移除父控件下指定的子组件
        :param parent: 父组件
        :param child: 子组件
        """
        if isinstance(child, QWidget):
            child.deleteLater()
            parent.removeWidget(child)
        elif isinstance(child, QLayoutItem):
            WidgetUtil.removeAllChild(child)
            parent.removeItem(child)

    @classmethod
    def translate(cls, context=contextName, text=""):
        return _translate(context, text)
