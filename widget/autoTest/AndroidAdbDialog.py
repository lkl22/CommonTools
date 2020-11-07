# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAdbDialog.py
# 定义一个AndroidAdbDialog类实现android adb指令操作功能
from constant.TestStepConst import *
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.ShellUtil import *
from util.LogUtil import *
from util.Uiautomator import *
from widget.autoTest.EditTestStepDialog import *


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

        self.u: Uiautomator = None
        self.execTestSteps = []

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
        WidgetUtil.createLabel(splitter, text="输入要执行的shell指令：", minSize=QSize(80, const.HEIGHT))
        self.cmdLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要执行的指令，多个以\";\"分隔", sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="执行", onClicked=self.execShellCmd)
        yPos += const.HEIGHT_OFFSET * 2
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="输入要连接设备的addr：", minSize=QSize(80, const.HEIGHT))
        self.devAddrEdit = WidgetUtil.createLineEdit(splitter, holderText="the device serial/device IP", sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="connect", onClicked=self.connectDevice)
        WidgetUtil.createPushButton(splitter, text="open weditor", onClicked=self.openWeditor)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 200, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="add step", onClicked=self.addStep)
        WidgetUtil.createPushButton(splitter, text="exec steps", onClicked=self.execSteps)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 180))
        self.findResTableView = WidgetUtil.createTableView(splitter, minSize=QSize(width, 150), sizePolicy=sizePolicy)

        yPos += 185
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="操作信息：", minSize=QSize(80, const.HEIGHT))
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 180))
        self.execResTE = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        return box

    def execCmd(self, cmd: str):
        LogUtil.d("exec cmd:", cmd)
        if cmd:
            WidgetUtil.appendTextEdit(self.execResTE, '执行指令：')
            WidgetUtil.appendTextEdit(self.execResTE, cmd + '\n')
            out, err = ShellUtil.exec(cmd)
            WidgetUtil.appendTextEdit(self.execResTE, '输出结果：')
            WidgetUtil.appendTextEdit(self.execResTE, out)
            if err:
                WidgetUtil.appendTextEdit(self.execResTE, '错误信息：\n', '#f00')
                WidgetUtil.appendTextEdit(self.execResTE, err, '#f00')
        pass

    def execShellCmd(self):
        cmdStr = self.cmdLineEdit.text().strip()
        if not cmdStr:
            WidgetUtil.showErrorDialog(message="请输入要执行的指令列表")
            return
        cmds = cmdStr.split(';')
        if cmds and len(cmds) > 0:
            for cmd in cmds:
                if not cmd:
                    continue
                self.execCmd(cmd)
        pass

    def connectDevice(self):
        addr = self.devAddrEdit.text().strip()
        LogUtil.d("要连接的设备addr：", addr)
        if self.u:
            self.u.reConnect(addr)
        else:
            self.u = Uiautomator(addr)
        WidgetUtil.appendTextEdit(self.execResTE, '设备info：' + str(self.u.deviceInfo()))
        self.devAddrEdit.setText(self.u.serial())
        pass

    def openWeditor(self):
        self.execCmd('weditor')

        WidgetUtil.appendTextEdit(self.execResTE, 'Another weditor(0.6.1) is already running. 请打开浏览器输入"http://localhost:17310"访问')
        pass

    def addStep(self):
        LogUtil.d("add step")
        EditTestStepDialog(self.addStepCallback)
        pass

    def addStepCallback(self):
        LogUtil.i('addStepCallback')
        pass

    def execSteps(self):
        LogUtil.d("exec steps")
        pass
