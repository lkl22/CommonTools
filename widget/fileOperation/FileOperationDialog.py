# -*- coding: utf-8 -*-
# python 3.x
# Filename: FileOperationDialog.py
# 定义一个FileOperationDialog类实现文件操作相关的功能
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.LogUtil import *


class FileOperationDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 360

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init File Operation Dialog")
        self.setObjectName("FileOperationDialog")
        self.resize(FileOperationDialog.WINDOW_WIDTH, FileOperationDialog.WINDOW_HEIGHT)
        self.setFixedSize(FileOperationDialog.WINDOW_WIDTH, FileOperationDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="文件相关操作"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, FileOperationDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       FileOperationDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        androidResGroupBox = self.createFileUtilGroupBox(layoutWidget)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createFileUtilGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = FileOperationDialog.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="文件工具")
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

        yPos += int(const.HEIGHT_OFFSET * 1.6)
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