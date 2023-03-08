# -*- coding: utf-8 -*-
# python 3.x
# Filename: FileOperationDialog.py
# 定义一个FileOperationDialog类实现文件操作相关的功能
from util.FileUtil import *
from util.DialogUtil import *
from util.LogUtil import *

TAG = "FileOperationDialog"


class FileOperationDialog(QtWidgets.QDialog):
    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        FileOperationDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        FileOperationDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init File Operation Dialog")
        self.setObjectName("FileOperationDialog")
        self.resize(FileOperationDialog.WINDOW_WIDTH, FileOperationDialog.WINDOW_HEIGHT)
        # self.setFixedSize(FileOperationDialog.WINDOW_WIDTH, FileOperationDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="文件相关操作"))

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        androidResGroupBox = self.createFileUtilGroupBox(self)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createFileUtilGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="文件工具")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        vbox.addWidget(WidgetUtil.createLabel(box, text="文件批量复制/移动："))

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="源文件路径", onClicked=self.getSrcFilePath))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.srcFilePathLineEdit)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="目标文件路径", onClicked=self.getDstFilePath))
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.dstFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="复制/移动文件的名称："))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(box, holderText="请输入要复制/移动的文件名的正则表达式，多个以\";\"分隔",
                                                               sizePolicy=sizePolicy)
        hbox.addWidget(self.srcFnPatternsLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="复制", onClicked=self.copyFiles))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="移动", onClicked=self.moveFiles))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box, text="批量修改文件名："))

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="文件路径", onClicked=self.getChangeFilePath))
        self.changeFpLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.changeFpLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="修改前文件名称："))
        self.fnChangeBeforeLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.fnChangeBeforeLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="修改后文件名称："))
        self.fnChangeAfterLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.fnChangeAfterLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="修改", onClicked=self.modifyFilesName))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
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
        LogUtil.d(TAG, "目标目录：", dstFileDirPath)
        srcFnPatterns = self.srcFnPatternsLineEdit.text().strip()
        if not srcFnPatterns:
            WidgetUtil.showErrorDialog(message="请输入文件名匹配正则表达式")
            return
        srcFnPs = srcFnPatterns.split(";")
        LogUtil.d(TAG, "源文件名匹配正则表达式：", srcFnPs)
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
        LogUtil.d(TAG, "将指定目录：", changeFileDirPath, " 下的所有文件 ", beforeFn, " 修改为 ", afterFn)
        # 查找需要修改名称的文件列表
        srcFiles = FileUtil.findFilePathList(changeFileDirPath, [beforeFn])
        if srcFiles:
            if FileUtil.modifyFilesName(srcFiles, afterFn):
                WidgetUtil.showErrorDialog(message="修改成功")
        else:
            WidgetUtil.showErrorDialog(message="指定目录下未查找到指定的文件")
