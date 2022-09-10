# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidResDialog.py
# 定义一个AndroidResDialog类实现android xml资源文件移动合并的功能
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *

RES_TYPE_LIST = ['无', 'string', 'color', 'style', 'dimen', 'plurals', 'declare-styleable', 'array', 'string-array',
                 'integer-array', 'attr']


class AndroidResDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 600

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android Res Dialog")
        self.setObjectName("AndroidResDialog")
        self.resize(AndroidResDialog.WINDOW_WIDTH, AndroidResDialog.WINDOW_HEIGHT)
        self.setFixedSize(AndroidResDialog.WINDOW_WIDTH, AndroidResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android xml资源文件处理"))

        self.resType = RES_TYPE_LIST[0]

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, AndroidResDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       AndroidResDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        androidResGroupBox = self.createXmlResGroupBox(layoutWidget)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createXmlResGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="xml resource")
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidResDialog.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, int(const.HEIGHT * 2.5)))
        sizePolicy = WidgetUtil.createSizePolicy()
        vLayout = WidgetUtil.createVBoxWidget(splitter, margins=QMargins(0, 0, 0, 0), sizePolicy=sizePolicy)

        vLayout1 = WidgetUtil.createVBoxWidget(splitter, margins=QMargins(20, 0, 10, 0))
        btn = WidgetUtil.createPushButton(splitter, text="", fixedSize=QSize(30, 40), styleSheet="background-color: white",
                                          iconSize=QSize(30, 40), icon=QIcon(FileUtil.getIconFp('androidRes/exchange.png')),
                                          onClicked=self.exchangeDirs)
        vLayout1.addWidget(btn)

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.HEIGHT, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.HEIGHT, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="目标文件路径", onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="源资源文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy,
                            holderText="请输入源资源文件名称正则表达式，多个以\";\"分隔", textChanged=self.srcFnTextChanged)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="目标资源文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.dstFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy, isEnable=False,
                                                               holderText="请输入目标资源文件名称")

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="选择资源类型：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.resTypeBg = WidgetUtil.createButtonGroup(onToggled=self.resTypeToggled)
        for i in range(len(RES_TYPE_LIST)):
            if i == 0:
                self.resTypeBg.addButton(
                    WidgetUtil.createRadioButton(splitter, text=RES_TYPE_LIST[i] + "  ", isChecked=True), i)
            else:
                if i == 8:
                    WidgetUtil.createLabel(splitter, text="", sizePolicy=WidgetUtil.createSizePolicy())
                    yPos += const.HEIGHT_OFFSET
                    splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
                    WidgetUtil.createLabel(splitter, text="", minSize=QSize(120, 20))
                self.resTypeBg.addButton(WidgetUtil.createRadioButton(splitter, text=RES_TYPE_LIST[i] + "  "), i)

        WidgetUtil.createLabel(splitter, text="", sizePolicy=WidgetUtil.createSizePolicy())

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="输入资源名称：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.resNamesLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要复制/移动的资源名称，多个以\";\"分隔",
                                                          isEnable=False, sizePolicy=sizePolicy)

        # yPos += const.HEIGHT_OFFSET
        # splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        # WidgetUtil.createLabel(splitter, text="输入namespace：", alignment=Qt.AlignVCenter | Qt.AlignRight,
        #                        minSize=QSize(120, const.HEIGHT))
        # self.resNamespaceLineEdit = WidgetUtil.createLineEdit(splitter,
        #                                                       holderText='xmlns:android="http://schemas.android.com/apk/res/android"',
        #                                                       sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 300, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="复制", onClicked=self.copyElements)
        WidgetUtil.createPushButton(splitter, text="移动", onClicked=self.moveElements)
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

    def exchangeDirs(self):
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        dstFileDirPath = self.dstFilePathLineEdit.text().strip()
        self.srcFilePathLineEdit.setText(dstFileDirPath)
        self.dstFilePathLineEdit.setText(srcFileDirPath)
        pass

    def resTypeToggled(self, radioButton):
        self.resType = RES_TYPE_LIST[self.resTypeBg.checkedId()]
        LogUtil.i("选择的资源类型：", self.resType)
        if self.resTypeBg.checkedId() == 0:
            self.resNamesLineEdit.setEnabled(False)
        else:
            self.resNamesLineEdit.setEnabled(True)
        pass

    def srcFnTextChanged(self, data):
        if not data:
            self.dstFnPatternsLineEdit.setEnabled(False)
            return
        srcFnPs = data.split(";")
        if len(srcFnPs) > 1:
            self.dstFnPatternsLineEdit.setEnabled(False)
        else:
            self.dstFnPatternsLineEdit.setEnabled(True)

    def copyElements(self):
        self.modifyElements()
        pass

    def moveElements(self):
        self.modifyElements(False)
        pass

    def modifyElements(self, isCopy=True):
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
            WidgetUtil.showErrorDialog(message="请输入资源文件名")
            return
        srcFnPs = srcFnPatterns.split(";")
        LogUtil.d("源资源文件名：", srcFnPs)

        dstFnPs = self.dstFnPatternsLineEdit.text().strip()
        LogUtil.d("目标资源文件名：", dstFnPs)

        resNamesStr = self.resNamesLineEdit.text().strip()
        attrValues = ''
        if resNamesStr:
            attrValues = resNamesStr.split(';')
            LogUtil.d('资源attr名称：', attrValues)
        attrName = 'name'
        if self.resType == RES_TYPE_LIST[0]:
            self.resType = ''
            attrName = ''
            attrValues = ''

        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(srcFileDirPath, srcFnPs)
        if srcFiles:
            for srcFile in srcFiles:
                dstFile = srcFile.replace(srcFileDirPath, dstFileDirPath, 1)
                if len(srcFnPs) == 1 and dstFnPs:
                    fp, fn = os.path.split(dstFile)  # 分离文件名和路径
                    dstFile = os.path.join(fp, dstFnPs)
                DomXmlUtil.modifyDomElements(srcFile, dstFile, self.resType, attrName, attrValues, isCopy)
        else:
            WidgetUtil.showErrorDialog(message="指定目录下未查找到指定的资源文件")
        pass
