# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidResDialog.py
# 定义一个AndroidResDialog类实现android xml资源文件移动合并的功能
import sys

from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *

RES_TYPE_LIST = ['无', 'string', 'color', 'style', 'dimen', 'plurals', 'declare-styleable', 'array', 'string-array',
                 'integer-array', 'attr']


class AndroidResDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AndroidResDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AndroidResDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.35)
        LogUtil.d("Init Android Res Dialog")
        self.setObjectName("AndroidResDialog")
        self.resize(AndroidResDialog.WINDOW_WIDTH, AndroidResDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AndroidResDialog.WINDOW_WIDTH, AndroidResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android xml资源文件处理"))

        self.resType = RES_TYPE_LIST[0]
        self.isDebug = isDebug

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        androidResGroupBox = self.createXmlResGroupBox(self)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createXmlResGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="xml resource")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        vLayout = WidgetUtil.createVBoxLayout()
        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="目标文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout(spacing=20)
        hbox.addLayout(vLayout)

        btn = WidgetUtil.createPushButton(box, text="", fixedSize=QSize(30, 40),
                                          styleSheet="background-color: white",
                                          iconSize=QSize(30, 40), icon=QIcon(
                '../resources/icons/androidRes/exchange.png' if self.isDebug else FileUtil.getIconFp(
                    'androidRes/exchange.png')),
                                          onClicked=self.exchangeDirs)
        hbox.addWidget(btn)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="源资源文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.srcFnPatternsLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy,
                                                               holderText="请输入源资源文件名称正则表达式，多个以\";\"分隔",
                                                               textChanged=self.srcFnTextChanged)
        hbox.addWidget(self.srcFnPatternsLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="目标资源文件名：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.dstFnPatternsLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy, isEnable=False,
                                                               holderText="请输入目标资源文件名称")
        hbox.addWidget(self.dstFnPatternsLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="选择资源类型：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(30, 0, 30, 0), spacing=10)
        vbox.addLayout(hbox)
        self.resTypeBg = WidgetUtil.createButtonGroup(onToggled=self.resTypeToggled)
        for i in range(len(RES_TYPE_LIST)):
            if i == 12:
                hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
                hbox = WidgetUtil.createHBoxLayout(margins=QMargins(30, 0, 30, 0), spacing=10)
            radioButton = WidgetUtil.createRadioButton(box, text=RES_TYPE_LIST[i] + "  ", isChecked=i == 0)
            self.resTypeBg.addButton(radioButton, i)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="输入资源名称：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.resNamesLineEdit = WidgetUtil.createLineEdit(box, holderText="请输入要复制/移动的资源名称，多个以\";\"分隔",
                                                          isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.resNamesLineEdit)
        vbox.addLayout(hbox)

        # WidgetUtil.createLabel(splitter, text="输入namespace：", alignment=Qt.AlignVCenter | Qt.AlignRight,
        #                        minSize=QSize(120, const.HEIGHT))
        # self.resNamespaceLineEdit = WidgetUtil.createLineEdit(splitter,
        #                                                       holderText='xmlns:android="http://schemas.android.com/apk/res/android"',
        #                                                       sizePolicy=sizePolicy)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="复制", onClicked=self.copyElements))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="移动", onClicked=self.moveElements))
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidResDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
