# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAdbDialog.py
# 定义一个AndroidAdbDialog类实现android adb指令操作功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.TestStepConst import *
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.ShellUtil import *
from util.LogUtil import *
from util.WeditorUtil import *
from widget.test.EditTestStepDialog import *


class AndroidAdbDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    TABLE_KEY_TYPE = '操作类型'
    TABLE_KEY_DESC = '操作描述信息'

    def __init__(self, execSteps=[], callback=None):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android adb Dialog")
        self.setObjectName("AndroidAdbDialog")
        self.resize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
        self.setFixedSize(AndroidAdbDialog.WINDOW_WIDTH, AndroidAdbDialog.WINDOW_HEIGHT)
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

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, AndroidAdbDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       AndroidAdbDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        adbGroupBox = self.createAdbGroupBox(layoutWidget)
        vLayout.addWidget(adbGroupBox)

        if self.callback:
            splitter = DialogUtil.createBottomBtn(self, okCallback=self.acceptFunc, cancelBtnText="Cancel")
            vLayout.addLayout(splitter)

        if self.execTestSteps:
            self.updateTableData()

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createAdbGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidAdbDialog.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="Android adb", minSize=QSize(width, self.adbGroupBoxHeight))
        sizePolicy = WidgetUtil.createSizePolicy()

        if not self.callback:
            splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
            WidgetUtil.createLabel(splitter, text="输入要执行的shell指令：", minSize=QSize(80, const.HEIGHT))
            self.cmdLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要执行的指令，多个以\";\"分隔",
                                                         sizePolicy=sizePolicy)
            WidgetUtil.createPushButton(splitter, text="执行", onClicked=self.execShellCmd)
            yPos += const.HEIGHT_OFFSET * 2

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="输入要连接设备的addr：", minSize=QSize(80, const.HEIGHT))
        self.devAddrEdit = WidgetUtil.createLineEdit(splitter, holderText="the device serial/device IP",
                                                     sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="connect", onClicked=self.connectDevice)
        WidgetUtil.createPushButton(splitter, text="open weditor", onClicked=self.openWeditor)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 200, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="add step", onClicked=self.addStep)
        WidgetUtil.createPushButton(splitter, text="exec steps", onClicked=self.execSteps)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 180))
        self.stepsTableView = WidgetUtil.createTableView(splitter, minSize=QSize(width, 150), sizePolicy=sizePolicy,
                                                         doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.stepsTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.stepsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.stepsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.stepsTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.stepsTableView.customContextMenuRequested.connect(self.customRightMenu)

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
        LogUtil.d("要连接的设备addr：", addr)
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
        LogUtil.i("updateTableData")
        self.src2TableDatas()
        WidgetUtil.addTableViewData(self.stepsTableView, data=self.execTestStepTableDatas)
        WidgetUtil.tableViewSetColumnWidth(self.stepsTableView)
        pass

    def addStep(self):
        LogUtil.d("add step")
        EditTestStepDialog(self.addStepCallback, u=self.u)
        pass

    def addStepCallback(self, stepType, params):
        LogUtil.i('addStepCallback', stepType, params)
        self.execTestSteps.append({const.KEY_STEP_TYPE: stepType, const.KEY_STEP_PARAMS: params})
        self.printRes('add step ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        self.updateTableData()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d("双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        self.curEditData = self.execTestSteps[row]
        EditTestStepDialog(self.editStepCallback, self.curEditData[const.KEY_STEP_TYPE],
                           self.curEditData[const.KEY_STEP_PARAMS], self.u)
        pass

    def editStepCallback(self, stepType, params):
        LogUtil.i('editStepCallback', stepType, params)
        self.printRes('edit step ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        self.curEditData[const.KEY_STEP_TYPE] = stepType
        self.curEditData[const.KEY_STEP_PARAMS] = params
        self.updateTableData()
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.stepsTableView.currentIndex().row()
        LogUtil.i("customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delItem)
        menu.exec_(self.stepsTableView.mapToGlobal(pos))
        pass

    def delItem(self):
        LogUtil.i("delItem")
        WidgetUtil.showQuestionDialog(message="你确定需要删除吗？", acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i("delTreeWidgetItem")
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
        LogUtil.d("exec steps")
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
        WidgetUtil.appendTextEdit(self.execResTE, res, color)
        pass

    def acceptFunc(self):
        LogUtil.d('acceptFunc')
        if self.callback:
            self.callback(self.execTestSteps)
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AndroidAdbDialog()
    window = AndroidAdbDialog(execSteps=[{'type': 0, 'params': {'xpath': '', 'x': 0.5, 'y': 0.5, 'desc': ""}},
                                         {'type': 1, 'params': {'xpath': '', 'x': 0.5, 'y': 0.5, 'desc': ""}}],
                              callback=lambda aa: {
                                  LogUtil.d(str(aa))
                              })
    window.show()
    sys.exit(app.exec_())
