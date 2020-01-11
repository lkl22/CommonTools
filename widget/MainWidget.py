# -*- coding: utf-8 -*-
# python 3.x
# Filename: MainWidget.py
# 定义一个MainWidget类实现MainWindow主窗口的功能
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from util.WidgetUtil import *
from util.DateUtil import *
from constant.WidgetConst import *


class MainWidget(QMainWindow):
    def __init__(self):
        # 调用父类的构函
        QMainWindow.__init__(self)
        self.setObjectName("MainWidget")
        self.resize(1180, 620)

        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setGeometry(QRect(10, 10, 1160, 600))
        self.layoutWidget.setObjectName("layoutWidget")

        self.vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))

        self.layoutWidget.setLayout(self.vLayout)
        self.commonGroupBox = self.createCommonGroupBox(self.layoutWidget)

        self.vLayout.addWidget(self.commonGroupBox)

        self.setWindowTitle(WidgetUtil.translate("MainWidget", "开发工具"))
        QtCore.QMetaObject.connectSlotsByName(self)
        pass

    def createCommonGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="常用工具")
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, const.HEIGHT_OFFSET, 1000, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间转化工具：")
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, const.HEIGHT_OFFSET * 2, 1000, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间戳转化时间：")
        sizePolicy = WidgetUtil.createSizePolicy()
        self.timestampLineEdit1 = WidgetUtil.createLineEdit(splitter, text=str(DateUtil.nowTimestamp()), holderText="1578623033", sizePolicy=sizePolicy)
        self.timeChangeBtn1 = WidgetUtil.createPushButton(splitter, text="转化", onClicked=self.timestamp2Time)
        self.timeLineEdit1 = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, const.HEIGHT_OFFSET * 3, 1000, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间转化时间戳：")
        self.timeLineEdit2 = WidgetUtil.createLineEdit(splitter, text=str(DateUtil.nowTime()), holderText="2020-01-11 10:28:28", sizePolicy=sizePolicy)
        self.timeChangeBtn2 = WidgetUtil.createPushButton(splitter, text="转化", onClicked=self.time2Timestamp)
        self.timestampLineEdit2 = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        return box

    def timestamp2Time(self):
        timestampStr = self.timestampLineEdit1.text().strip()
        timestamp = DateUtil.timestampStr2Seconds(timestampStr)
        if timestamp is None:
            WidgetUtil.showErrorDialog(message="请输入正确格式的时间戳")
            return
        time = DateUtil.timestamp2Time(timestamp[0])
        if timestamp[1] > 0:
            time = "%s.%3d" % (time, timestamp[1])
        self.timeLineEdit1.setText(time)
        pass

    def time2Timestamp(self):
        timeStr = self.timeLineEdit2.text().strip()
        timestamp = DateUtil.time2Timestamp(timeStr)
        if timestamp:
            self.timestampLineEdit2.setText(str(timestamp))
        else:
            WidgetUtil.showErrorDialog(message="请输入正确格式的时间(YYYY-MM-dd HH:mm:ss)")
        pass
