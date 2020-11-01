# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAdbDialog.py
# 定义一个AndroidAdbDialog类实现android adb指令操作功能
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.ShellUtil import *
from util.LogUtil import *


class AndroidAdbDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android adb Dialog")
        self.setObjectName("AndroidAdbDialog")
        self.resize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
        self.setFixedSize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android Adb"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, AndroidAdbDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       AndroidAdbDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        androidResGroupBox = self.createXmlResGroupBox(layoutWidget)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createXmlResGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="Android adb")
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidAdbDialog.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        WidgetUtil.createLabel(splitter, text="输入指令：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(80, const.HEIGHT))
        self.cmdLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要执行的指令，多个以\";\"分隔", sizePolicy=sizePolicy)
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="执行", onClicked=self.execCmd)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 200))

        self.execResTE = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        return box

    def execCmd(self):
        cmdStr = self.cmdLineEdit.text().strip()
        if not cmdStr:
            WidgetUtil.showErrorDialog(message="请输入要执行的指令列表")
            return
        cmds = cmdStr.split(';')
        if cmds and len(cmds) > 0:
            for cmd in cmds:
                if not cmd:
                    continue
                WidgetUtil.appendTextEdit(self.execResTE, '执行指令：')
                WidgetUtil.appendTextEdit(self.execResTE, cmd + '\n')
                out, err = ShellUtil.exec(cmd)
                WidgetUtil.appendTextEdit(self.execResTE, '输出结果：')
                WidgetUtil.appendTextEdit(self.execResTE, out)
                if err:
                    WidgetUtil.appendTextEdit(self.execResTE, '错误信息：\n', '#f00')
                    WidgetUtil.appendTextEdit(self.execResTE, err, '#f00')
        pass
