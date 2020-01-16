# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidResDialog.py
# 定义一个AndroidResDialog类实现android xml资源文件移动合并的功能
from constant.WidgetConst import *
from util.WidgetUtil import *
from util.DialogUtil import *
from util.LogUtil import *

RES_TYPE_LIST = ['无', 'string', 'color', 'style', 'dimen', 'plurals', 'declare-styleable', 'array', 'string-array',
                 'integer-array', 'attr']


class AndroidResDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
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
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))

        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="目标文件路径", onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="资源文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)

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

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="输入namespace：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT))
        self.resNamespaceLineEdit = WidgetUtil.createLineEdit(splitter,
                                                              holderText='xmlns:android="http://schemas.android.com/apk/res/android"',
                                                              sizePolicy=sizePolicy)

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

    def resTypeToggled(self, radioButton):
        self.resType = RES_TYPE_LIST[self.resTypeBg.checkedId()]
        LogUtil.i("选择的资源类型：", self.resType)
        if self.resTypeBg.checkedId() == 0:
            self.resNamesLineEdit.setEnabled(False)
        else:
            self.resNamesLineEdit.setEnabled(True)
        pass

    def copyElements(self):
        self.modifyElements(False)
        pass

    def moveElements(self):
        self.modifyElements()
        pass

    def modifyElements(self, isMove=True):

        pass
