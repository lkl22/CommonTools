# -*- coding: utf-8 -*-
# python 3.x
# Filename: MainWidget.py
# 定义一个MainWidget类实现MainWindow主窗口的功能
from PyQt5.QtWidgets import QMainWindow
from util.WidgetUtil import *
from util.DateUtil import *
from util.FileUtil import *
from constant.WidgetConst import *


class MainWidget(QMainWindow):
    WINDOW_WIDTH = 880
    WINDOW_HEIGHT = 500

    windowList = []

    def __init__(self):
        # 调用父类的构函
        QMainWindow.__init__(self)
        self.setObjectName("MainWidget")
        self.resize(MainWidget.WINDOW_WIDTH, MainWidget.WINDOW_HEIGHT)

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, MainWidget.WINDOW_WIDTH - const.PADDING * 2,
                                       MainWidget.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        commonGroupBox = self.createCommonGroupBox(layoutWidget)
        otherGroupBox = self.createOtherUtilGroupBox(layoutWidget)

        vLayout.addWidget(commonGroupBox)
        vLayout.addWidget(otherGroupBox)

        self.setWindowTitle(WidgetUtil.translate("MainWidget", "开发测试辅助工具"))
        QtCore.QMetaObject.connectSlotsByName(self)
        pass

    def createCommonGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="常用工具")
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = MainWidget.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间转化工具：")
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING,  yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间戳转化时间：")
        sizePolicy = WidgetUtil.createSizePolicy(hStretch=2)
        sizePolicy1 = WidgetUtil.createSizePolicy(hStretch=3)
        self.timestampLineEdit1 = WidgetUtil.createLineEdit(splitter, text=str(DateUtil.nowTimestamp()),
                                                            holderText="1578623033", sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="转化", onClicked=self.timestamp2Time)
        self.timeLineEdit1 = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += int(const.HEIGHT_OFFSET * 1.2)
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间转化时间戳：")
        self.timeLineEdit2 = WidgetUtil.createLineEdit(splitter, text=str(DateUtil.nowTime()),
                                                       holderText="2020-01-11 10:28:28", sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="转化", onClicked=self.time2Timestamp)
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
            time = "%s.%03d" % (time, timestamp[1])
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

    def createOtherUtilGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="其他工具")
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = MainWidget.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="Android测试辅助工具", onClicked=self.jumpAndroidAssistTestDialog)
        WidgetUtil.createPushButton(splitter, text="文件操作工具", onClicked=self.jumpFileOperationDialog)
        WidgetUtil.createPushButton(splitter, text="Android资源移动工具", onClicked=self.jumpAndroidResDialog)
        WidgetUtil.createPushButton(splitter, text="Android color资源管理工具", onClicked=self.jumpAndroidColorResDialog)
        WidgetUtil.createPushButton(splitter, text="照片墙", onClicked=self.jumpPhotoWall)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="图片压缩", onClicked=self.jumpCompressPicDialog)
        WidgetUtil.createPushButton(splitter, text="Json格式化工具", onClicked=self.jumpJsonDialog)
        WidgetUtil.createPushButton(splitter, text="Android adb指令工具", onClicked=self.jumpAndroidAdbDialog)
        WidgetUtil.createPushButton(splitter, text="算法可视化", onClicked=self.jumpAlgorithmVisualizer)
        WidgetUtil.createPushButton(splitter, text="模拟考试", onClicked=self.jumpMockExamDialog)
        return box

    def jumpAndroidAssistTestDialog(self):
        LogUtil.i("jumpAndroidAdbDialog")
        from widget.test.AndroidAssistTestDialog import AndroidAssistTestDialog
        AndroidAssistTestDialog()
        pass

    def jumpFileOperationDialog(self):
        LogUtil.i("jumpAndroidAdbDialog")
        from widget.fileOperation.FileOperationDialog import FileOperationDialog
        FileOperationDialog()
        pass

    def jumpAndroidResDialog(self):
        LogUtil.i("jumpAndroidResDialog")
        from widget.AndroidResDialog import AndroidResDialog
        AndroidResDialog()
        pass

    def jumpAndroidColorResDialog(self):
        LogUtil.i("jumpAndroidColorResDialog")
        from widget.colorManager.AndroidColorResDialog import AndroidColorResDialog
        AndroidColorResDialog()
        pass

    def jumpPhotoWall(self, filePath=None, photoType=None, previewFinishedFunc=None):
        LogUtil.i("jumpPhotoWall")
        from widget.photoWall.PhotoWallWindow import PhotoWallWindow
        window = PhotoWallWindow(filePath, photoType, previewFinishedFunc)
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        self.close()
        window.show()
        pass

    def jumpCompressPicDialog(self):
        LogUtil.i("jumpCompressPicDialog")
        from widget.compressPicture.CompressPicDialog import CompressPicDialog
        CompressPicDialog()
        pass

    def jumpJsonDialog(self):
        LogUtil.i("jumpJsonDialog")
        from widget.JsonDialog import JsonDialog
        JsonDialog()
        pass

    def jumpAndroidAdbDialog(self):
        LogUtil.i("jumpAndroidAdbDialog")
        from widget.test.AndroidAdbDialog import AndroidAdbDialog
        AndroidAdbDialog()
        pass

    def jumpAlgorithmVisualizer(self):
        LogUtil.i("jumpAlgorithmVisualizer")
        from widget.algorithm.AlgorithmVisualizerManagerDialog import AlgorithmVisualizerManagerDialog
        AlgorithmVisualizerManagerDialog()
        pass

    def jumpMockExamDialog(self):
        LogUtil.i("jumpAlgorithmVisualizer")
        from widget.mockExam.MockExamDialog import MockExamDialog
        MockExamDialog()
        pass
