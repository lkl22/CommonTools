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
    WINDOW_WIDTH = 1180
    WINDOW_HEIGHT = 620
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
        fileGroupBox = self.createFileUtilGroupBox(layoutWidget)
        otherGroupBox = self.createOtherUtilGroupBox(layoutWidget)

        vLayout.addWidget(commonGroupBox)
        vLayout.addWidget(fileGroupBox)
        vLayout.addWidget(otherGroupBox)

        self.setWindowTitle(WidgetUtil.translate("MainWidget", "开发工具"))
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
        self.timeLineEdit1 = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy1)

        # splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, const.HEIGHT_OFFSET * 3, 1000, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="时间转化时间戳：", alignment=Qt.AlignRight | Qt.AlignVCenter,
                               minSize=QSize(150, const.HEIGHT))
        self.timeLineEdit2 = WidgetUtil.createLineEdit(splitter, text=str(DateUtil.nowTime()),
                                                       holderText="2020-01-11 10:28:28", sizePolicy=sizePolicy1)
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

    def createFileUtilGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = MainWidget.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="文件工具", minSize=QSize(width, 300))
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="文件批量复制/移动：")

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="源文件路径", onClicked=self.getSrcFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        WidgetUtil.createPushButton(splitter, text="目标文件路径", onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="复制/移动文件的名称：")
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要复制/移动的文件名的正则表达式，多个以\";\"分隔",
                                                               sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 300, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="复制", onClicked=self.copyFiles)
        WidgetUtil.createPushButton(splitter, text="移动", onClicked=self.moveFiles)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="批量修改文件名：")

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="文件路径", onClicked=self.getChangeFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.changeFpLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)


        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="修改前文件名称：")
        self.fnChangeBeforeLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="修改后文件名称：")
        self.fnChangeAfterLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 150, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="修改", onClicked=self.modifyFilesName)
        return box

    def getSrcFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.srcFilePathLineEdit.setText(fp)
        pass

    def getDstFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.dstFilePathLineEdit.setText(fp)
        pass

    def copyFiles(self):
        self.modifyFiles()
        pass

    def moveFiles(self):
        self.modifyFiles(False)
        pass

    def modifyFiles(self, isCopy=True):
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件目录")
            return
        dstFileDirPath = self.dstFilePathLineEdit.text().strip()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件目录")
            return
        while dstFileDirPath.endswith("/") or dstFileDirPath.endswith("\\"):
            dstFileDirPath = dstFileDirPath[:len(dstFileDirPath) - 1]
        LogUtil.d("目标目录：", dstFileDirPath)
        srcFnPatterns = self.srcFnPatternsLineEdit.text().strip()
        if not srcFnPatterns:
            WidgetUtil.showErrorDialog(message="请输入文件名匹配正则表达式")
            return
        srcFnPs = srcFnPatterns.split(";")
        LogUtil.d("源文件名匹配正则表达式：", srcFnPs)
        # ic_launch.*png;strings.xml
        WidgetUtil.showQuestionDialog(message="你确认需要复制/移动文件吗？",
                                      acceptFunc=lambda: FileUtil.modifyFilesPath(srcFnPs, srcFileDirPath,
                                                                                  dstFileDirPath, isCopy))
        pass

    def getChangeFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.changeFpLineEdit.setText(fp)
        pass

    def modifyFilesName(self):
        changeFileDirPath = self.changeFpLineEdit.text().strip()
        if not changeFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择要修改文件所在的目录")
            return
        beforeFn = self.fnChangeBeforeLineEdit.text().strip()
        if not beforeFn:
            WidgetUtil.showErrorDialog(message="请输入修改前文件名称")
            return
        afterFn = self.fnChangeAfterLineEdit.text().strip()
        if not afterFn:
            WidgetUtil.showErrorDialog(message="请输入修改后文件名称")
            return
        LogUtil.d("将指定目录：", changeFileDirPath, " 下的所有文件 ", beforeFn, " 修改为 ", afterFn)
        # 查找需要修改名称的文件列表
        srcFiles = FileUtil.findFilePathList(changeFileDirPath, [beforeFn])
        if srcFiles:
            if FileUtil.modifyFilesName(srcFiles, afterFn):
                WidgetUtil.showErrorDialog(message="修改成功")
        else:
            WidgetUtil.showErrorDialog(message="指定目录下未查找到指定的文件")


    def createOtherUtilGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="其他工具")
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 600, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="Json格式化工具", onClicked=self.jumpJsonDialog)

        WidgetUtil.createPushButton(splitter, text="Android资源移动工具", onClicked=self.jumpAndroidResDialog)

        WidgetUtil.createPushButton(splitter, text="Android color资源管理工具", onClicked=self.jumpAndroidColorResDialog)

        yPos += const.HEIGHT_OFFSET
        return box

    def jumpJsonDialog(self):
        LogUtil.i("jumpJsonDialog")
        from widget.JsonDialog import JsonDialog
        dialog = JsonDialog()
        # dialog.show()
        pass

    def jumpAndroidResDialog(self):
        LogUtil.i("jumpAndroidResDialog")
        from widget.AndroidResDialog import AndroidResDialog
        dialog = AndroidResDialog()
        # dialog.show()
        pass

    def jumpAndroidColorResDialog(self):
        LogUtil.i("jumpAndroidResDialog")
        from widget.colorManager.AndroidColorResDialog import AndroidColorResDialog
        dialog = AndroidColorResDialog()
        # dialog.show()
        pass
