# -*- coding: utf-8 -*-
# python 3.x
# Filename: MainWidget.py
# 定义一个MainWidget类实现MainWindow主窗口的功能
from PyQt5.QtWidgets import QMainWindow
from util.WidgetUtil import *
from util.DateUtil import *
from util.FileUtil import *


class MainWidget(QMainWindow):
    windowList = []

    def __init__(self):
        # 调用父类的构函
        QMainWindow.__init__(self)
        MainWidget.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        MainWidget.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.6)
        self.setObjectName("MainWidget")
        self.resize(MainWidget.WINDOW_WIDTH, MainWidget.WINDOW_HEIGHT)

        centralWidget = QtWidgets.QWidget(self)
        centralWidget.setObjectName("centralWidget")

        vLayout = WidgetUtil.createVBoxLayout(centralWidget, margins=QMargins(10, 10, 10, 10), spacing=5)
        centralWidget.setLayout(vLayout)

        commonGroupBox = self.createCommonGroupBox(centralWidget)
        otherGroupBox = self.createOtherUtilGroupBox(centralWidget)

        vLayout.addWidget(commonGroupBox, 1)
        vLayout.addWidget(otherGroupBox, 3)
        # vLayout.setStretch(0, 1)
        # vLayout.setStretch(1, 3)

        self.createMenuBar()

        self.setCentralWidget(centralWidget)

        self.setWindowTitle(WidgetUtil.translate("MainWidget", "开发测试辅助工具"))
        QtCore.QMetaObject.connectSlotsByName(self)
        pass

    def createMenuBar(self):
        # 顶部菜单栏
        menuBar: QMenuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        sizeMenu = menuBar.addMenu('&Setting')
        sizeMenu.setStatusTip('配置备份与恢复')
        sizeMenu.addAction(WidgetUtil.createAction(parent=menuBar, text='备份', func=self.backupConfig, statusTip='显示小图标'))
        sizeMenu.addAction(WidgetUtil.createAction(parent=menuBar, text='恢复', func=self.restoreConfig, statusTip='显示中图标'))

    def backupConfig(self):
        configFp = FileUtil.getConfigFp("BaseConfig.ini")
        LogUtil.d("backupConfig", configFp)
        fp = WidgetUtil.getExistingDirectory(caption="请选择要备份保存的路径", directory="./")
        if not fp:
            WidgetUtil.showAboutDialog(text="您未选择备份路径，备份失败。")
            return
        if FileUtil.modifyFilePath(configFp, os.path.join(fp, "BaseConfig.ini")):
            WidgetUtil.showAboutDialog(text=f"恭喜您成功备份到<span style='color:red;'>{os.path.join(fp, 'BaseConfig.ini')}</span>")
        pass

    def restoreConfig(self):
        LogUtil.d("restoreConfig")
        fp = WidgetUtil.getOpenFileName(caption='选择备份的配置文件', filter='*.ini', initialFilter='*.ini')
        if not fp:
            WidgetUtil.showAboutDialog(text="您未选择配置文件，恢复失败。")
            return
        configFp = FileUtil.getConfigFp("BaseConfig.ini")
        if FileUtil.modifyFilePath(fp, configFp):
            WidgetUtil.showAboutDialog(text=f"恭喜您成功恢复配置。")
        pass

    def createCommonGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="常用工具")
        vbox = WidgetUtil.createVBoxLayout(box, spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="时间转化工具："))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="时间戳转化时间："))
        self.timestampLineEdit1 = WidgetUtil.createLineEdit(box, text=str(DateUtil.nowTimestamp()),
                                                            holderText="1578623033")
        hbox.addWidget(self.timestampLineEdit1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="转化", onClicked=self.timestamp2Time))
        self.timeLineEdit1 = WidgetUtil.createLineEdit(box, isEnable=False)
        hbox.addWidget(self.timeLineEdit1)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="时间转化时间戳："))
        self.timeLineEdit2 = WidgetUtil.createLineEdit(box, text=str(DateUtil.nowTime()),
                                                       holderText="2020-01-11 10:28:28")
        hbox.addWidget(self.timeLineEdit2)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="转化", onClicked=self.time2Timestamp))
        self.timestampLineEdit2 = WidgetUtil.createLineEdit(box, isEnable=False)
        hbox.addWidget(self.timestampLineEdit2)
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
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
        vbox = WidgetUtil.createVBoxLayout(box, spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="Android测试辅助工具", onClicked=self.jumpAndroidAssistTestDialog))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="文件操作工具", onClicked=self.jumpFileOperationDialog))
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="Android资源移动工具", onClicked=self.jumpAndroidResDialog))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Android color资源管理工具",
                                                   onClicked=self.jumpAndroidColorResDialog))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="照片墙", onClicked=self.jumpPhotoWall))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="图片压缩", onClicked=self.jumpCompressPicDialog))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Json格式化工具", onClicked=self.jumpJsonDialog))
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="Android adb指令工具", onClicked=self.jumpAndroidAdbDialog))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="算法可视化", onClicked=self.jumpAlgorithmVisualizer))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="模拟考试", onClicked=self.jumpMockExamDialog))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="计算文件hash", onClicked=self.jumpFileHashDialog), 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="账号管理", onClicked=self.jumpAccountManagerDialog), 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="项目管理", onClicked=self.jumpProjectManagerWindow), 1)
        hbox.addWidget(WidgetUtil.createLabel(box), 2)
        vbox.addLayout(hbox)
        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
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

    def jumpFileHashDialog(self):
        LogUtil.i("jumpFileHashDialog")
        from widget.hash.FileHashDialog import FileHashDialog
        FileHashDialog()
        pass

    def jumpAccountManagerDialog(self):
        LogUtil.i("jumpAccountManagerDialog")
        from widget.account.AccountManagerDialog import AccountManagerDialog
        AccountManagerDialog()
        pass

    def jumpProjectManagerWindow(self):
        LogUtil.i("jumpProjectManagerWindow")
        from widget.projectManage.ProjectManagerWindow import ProjectManagerWindow
        window = ProjectManagerWindow()
        window.center()
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        self.close()
        window.show()
        pass
