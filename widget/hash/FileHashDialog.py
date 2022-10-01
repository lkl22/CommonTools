# -*- coding: utf-8 -*-
# python 3.x
# Filename: FileHashDialog.py
# 定义一个FileHashDialog类实现计算文件hash值及值对比功能
from util.DialogUtil import *
from util.OperaIni import *
from util.HashUtil import HashUtil
from widget.custom.DragInputWidget import DragInputWidget
from widget.mockExam.Excel2Word import *

HASH_ALGORITHM = ['MD5', 'SHA1', 'SHA256', 'CRC32']


class FileHashDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        FileHashDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        FileHashDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d("File Hash Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="计算文件Hash"))
        self.setObjectName("FileHashDialog")

        self.curHashAlgorithm = HASH_ALGORITHM[0]
        self.curFilePath = None
        self.curFileHash = None
        self.yourHashData = None

        self.resize(FileHashDialog.WINDOW_WIDTH, FileHashDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.fileHashGroupBox = self.createFileHashGroupBox(self)
        vLayout.addWidget(self.fileHashGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createFileHashGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="计算文件Hash")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()
        self.dragInputWidget = DragInputWidget(isReadOnly=True, holderText="请拖动您要计算hash值的文件到此框或者双击选择您需要的文件", textChanged=self.dragInputTextChanged)
        hbox.addWidget(self.dragInputWidget)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择hash算法："))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.hashAlgorithmGroup = WidgetUtil.createButtonGroup(onToggled=self.hashAlgorithmToggled)
        for index, hashAlgorith in enumerate(HASH_ALGORITHM):
            radioButton = WidgetUtil.createRadioButton(box, text=hashAlgorith, isChecked=index == 0)
            self.hashAlgorithmGroup.addButton(radioButton, index)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="计算的hash值：", minSize=QSize(120, 20)))
        self.calcHashLineEdit = WidgetUtil.createLineEdit(box, toolTip="显示输入文件对应选择的hash算法的hash值。", isReadOnly=True)
        hbox.addWidget(self.calcHashLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="您的hash数据：", minSize=QSize(120, 20)))
        self.yourHashLineEdit = WidgetUtil.createLineEdit(box, holderText="请输入您要跟本工具计算结果对比的hash值",
                                                          toolTip="绿色表示一致，红色表示不一致。",
                                                          textChanged=self.yourHashTextChanged)
        hbox.addWidget(self.yourHashLineEdit)
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def dragInputTextChanged(self, fp):
        LogUtil.d("dragInputTextChanged", fp)
        if not FileUtil.existsFile(fp):
            WidgetUtil.showErrorDialog(message="请拖动一个文件或者选择一个文件")
            return
        self.curFilePath = fp
        self.calcFileHash()
        pass

    def hashAlgorithmToggled(self):
        self.curHashAlgorithm = HASH_ALGORITHM[self.hashAlgorithmGroup.checkedId()]
        LogUtil.d('hashAlgorithmToggled', self.curHashAlgorithm)
        self.calcFileHash()
        pass

    def calcFileHash(self):
        if not self.curFilePath:
            return

        self.curFileHash = HashUtil.calcFileHash(self.curFilePath, self.curHashAlgorithm)
        self.calcHashLineEdit.setText(self.curFileHash)

        self.compareHashDataDiff()
        pass

    def yourHashTextChanged(self, hashData):
        LogUtil.d("yourHashTextChanged", hashData)
        self.yourHashData = hashData
        if hashData:
            self.compareHashDataDiff()
        pass

    def compareHashDataDiff(self):
        LogUtil.d("compareHashDataDiff")
        if self.yourHashData == self.curFileHash:
            self.yourHashLineEdit.setStyleSheet("QLineEdit{ background:rgb(0,255,0);}")
        else:
            self.yourHashLineEdit.setStyleSheet("QLineEdit{ background:rgb(255,0,0);}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileHashDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
