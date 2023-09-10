# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAdbDialog.py
# 定义一个AndroidAdbDialog类实现android adb指令操作功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView
from util.WeditorUtil import *
from widget.test.EditTestStepDialog import *

TAG = "AndroidAdbDialog"


class AndroidAdbDialog(QtWidgets.QDialog):
    TABLE_KEY_TYPE = '操作类型'
    TABLE_KEY_DESC = '操作描述信息'

    def __init__(self, execSteps=[], callback=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AndroidAdbDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AndroidAdbDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init Android adb Dialog")
        self.setObjectName("AndroidAdbDialog")
        self.resize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android Adb"))

        self.callback = callback
        self.u: Uiautomator = None
        self.t: AutoTestUtil = None
        self.execTestSteps = execSteps
        self.execTestStepTableDatas = []
        if self.callback:
            self.adbGroupBoxHeight = 530
        else:
            self.adbGroupBoxHeight = 580

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        adbGroupBox = self.createAdbGroupBox(self)
        vLayout.addWidget(adbGroupBox)

        if self.callback:
            btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                      rejectedFunc=lambda: self.close())
            vLayout.addWidget(btnBox)

        if self.execTestSteps:
            self.updateTableData()

        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createAdbGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="Android adb")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        if not self.callback:
            hbox = WidgetUtil.createHBoxLayout()
            hbox.addWidget(WidgetUtil.createLabel(box, text="输入要执行的shell指令：", minSize=QSize(80, const.HEIGHT)))
            self.cmdLineEdit = WidgetUtil.createLineEdit(box, holderText="请输入要执行的指令，多个以\";\"分隔",
                                                         sizePolicy=sizePolicy)
            hbox.addWidget(self.cmdLineEdit)
            hbox.addWidget(WidgetUtil.createPushButton(box, text="执行", onClicked=self.execShellCmd))
            vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="输入要连接设备的addr：", minSize=QSize(80, const.HEIGHT)))
        self.devAddrEdit = WidgetUtil.createLineEdit(box, holderText="the device serial/device IP",
                                                     sizePolicy=sizePolicy)
        hbox.addWidget(self.devAddrEdit)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="connect", onClicked=self.connectDevice))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="open weditor", onClicked=self.openWeditor))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="add step", onClicked=self.addStep))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="exec steps", onClicked=self.execSteps))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.stepsTableView = WidgetUtil.createTableView(box, sizePolicy=sizePolicy,
                                                         doubleClicked=self.tableDoubleClicked)
        hbox.addWidget(self.stepsTableView)
        # 设为不可编辑
        self.stepsTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.stepsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.stepsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.stepsTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stepsTableView.customContextMenuRequested.connect(self.customRightMenu)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="操作信息：", minSize=QSize(80, const.HEIGHT)))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.execResTE = WidgetUtil.createTextEdit(box, isReadOnly=True)
        hbox.addWidget(self.execResTE)
        vbox.addLayout(hbox, 1)
        return box

    def execCmd(self, cmd: str):
        LogUtil.d(TAG, "exec cmd:", cmd)
        if cmd:
            self.printRes('执行指令：')
            self.printRes(cmd + '\n')
            out, err = ShellUtil.exec(cmd)
            if out:
                self.printRes('输出结果：')
                self.printRes(out)
            if err:
                self.printRes('错误信息：\n', '#f00')
                self.printRes(err, '#f00')
                return False
        return True

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
        LogUtil.d(TAG, "要连接的设备addr：", addr)
        if self.u:
            self.u.reConnect(addr)
        else:
            self.u = Uiautomator(addr)
        self.printRes('设备info：' + str(self.u.deviceInfo()))
        self.devAddrEdit.setText(self.u.serial())
        if self.u.err:
            WidgetUtil.showErrorDialog(message='connect device错误信息：{}'.format(self.u.err))
            return False
        return True

    def openWeditor(self):
        self.printRes(WeditorUtil.open())
        pass

    def updateTableData(self):
        LogUtil.i(TAG, "updateTableData")
        self.src2TableDatas()
        WidgetUtil.addTableViewData(self.stepsTableView, data=self.execTestStepTableDatas)
        WidgetUtil.tableViewSetColumnWidth(self.stepsTableView)
        pass

    def addStep(self):
        LogUtil.d(TAG, "add step")
        EditTestStepDialog(self.addStepCallback, u=self.u)
        pass

    def addStepCallback(self, stepType, params):
        LogUtil.i(TAG, 'addStepCallback', stepType, params)
        self.execTestSteps.append({const.KEY_STEP_TYPE: stepType, const.KEY_STEP_PARAMS: params})
        self.printRes('add step ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        self.updateTableData()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        self.curEditData = self.execTestSteps[row]
        EditTestStepDialog(self.editStepCallback, self.curEditData[const.KEY_STEP_TYPE],
                           self.curEditData[const.KEY_STEP_PARAMS], self.u)
        pass

    def editStepCallback(self, stepType, params):
        LogUtil.i(TAG, 'editStepCallback', stepType, params)
        self.printRes('edit step ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        self.curEditData[const.KEY_STEP_TYPE] = stepType
        self.curEditData[const.KEY_STEP_PARAMS] = params
        self.updateTableData()
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.stepsTableView.currentIndex().row()
        LogUtil.i(TAG, "customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delItem)
        menu.exec_(self.stepsTableView.mapToGlobal(pos))
        pass

    def delItem(self):
        LogUtil.i(TAG, "delItem")
        WidgetUtil.showQuestionDialog(message="你确定需要删除吗？", acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i(TAG, "delTreeWidgetItem")
        self.execTestSteps.remove(self.execTestSteps[self.curDelRow])
        self.printRes('del No.' + str(self.curDelRow + 1) + ' step')
        self.updateTableData()
        pass

    def src2TableDatas(self):
        self.execTestStepTableDatas = []
        for src in self.execTestSteps:
            self.execTestStepTableDatas.append(self.src2TableData(src))

    def src2TableData(self, srcData: dict):
        name = AutoTestUtil.stepName(srcData[const.KEY_STEP_TYPE])
        value = srcData[const.KEY_STEP_PARAMS][const.KEY_DESC]
        return {AndroidAdbDialog.TABLE_KEY_TYPE: name, AndroidAdbDialog.TABLE_KEY_DESC: value}

    def execSteps(self):
        LogUtil.d(TAG, "exec steps")
        if not self.execTestSteps:
            WidgetUtil.showErrorDialog(message="请先添加要执行的操作")
            return
        if not self.connectDevice():
            return
        if self.u.err:
            WidgetUtil.showErrorDialog(message='连接设备错误信息：{}'.format(self.u.err))
            return
        if not self.t:
            self.t = AutoTestUtil(self.u)
        self.printRes('start exec')
        for step in self.execTestSteps:
            self.t.startTestStep(stepType=step[const.KEY_STEP_TYPE], params=step[const.KEY_STEP_PARAMS],
                                 logCallback=self.printRes)
        self.printRes('exec finished')
        pass

    def printRes(self, res: str = '', color='#00f'):
        WidgetUtil.textEditAppendMessage(self.execResTE, res, color)
        pass

    def acceptFunc(self):
        LogUtil.d(TAG, 'acceptFunc')
        if self.callback:
            self.callback(self.execTestSteps)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AndroidAdbDialog(isDebug=True)
    window = AndroidAdbDialog(execSteps=[{'type': 0, 'params': {'xpath': '', 'x': 0.5, 'y': 0.5, 'desc': ""}},
                                         {'type': 1, 'params': {'xpath': '', 'x': 0.5, 'y': 0.5, 'desc': ""}}],
                              callback=lambda aa: {
                                  LogUtil.d(TAG, "callback:", str(aa))
                              }, isDebug=True)
    window.show()
    sys.exit(app.exec_())
