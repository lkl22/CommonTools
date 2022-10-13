# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditModuleDialog.py
# 定义一个AddOrEditModuleDialog类实现添加、编辑模块配置功能
import copy
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.MD5Util import MD5Util
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.AddOrEditCmdDialog import AddOrEditCmdDialog
from widget.projectManage.ProjectManager import *


class AddOrEditModuleDialog(QtWidgets.QDialog):
    def __init__(self, callback, openDir=None, default=None, moduleList=None, optionGroups=None, cmdGroups=None,
                 isCopyEdit=False, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.currentRow = -1
        self.callback = callback
        self.isDebug = isDebug
        if moduleList is None:
            moduleList = []
        self.moduleList = moduleList
        if optionGroups is None:
            optionGroups = []
        self.optionGroups = optionGroups

        if cmdGroups is None:
            cmdGroups = []
        self.cmdGroups = cmdGroups

        self.isAdd = default is None or isCopyEdit
        if not default:
            default = {KEY_CMD_LIST: []}
        elif KEY_CMD_LIST not in default:
            default[KEY_CMD_LIST] = []
        self.default = default
        self.cmdList = copy.deepcopy(default[KEY_CMD_LIST])

        self.openDir = openDir if openDir else './'

        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        AddOrEditModuleDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditModuleDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d("Add Or Edit Module Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/修改模块配置"))
        self.setObjectName("AddOrEditModuleDialog")
        self.resize(AddOrEditModuleDialog.WINDOW_WIDTH, AddOrEditModuleDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.moduleConfigGroupBox = self.createModuleConfigGroupBox(self)
        vLayout.addWidget(self.moduleConfigGroupBox)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def getModuleDir(self):
        workDir = DictUtil.get(self.default, KEY_PATH, "")
        return self.openDir + workDir if DictUtil.get(self.default, KEY_IS_RELATIVE_PATH, False) else workDir

    def createModuleConfigGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        labelWidth = 80
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="模块名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.default, KEY_NAME),
                                                      isReadOnly=not self.isAdd)
        hbox.addWidget(self.nameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="模块描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.default, KEY_DESC))
        hbox.addWidget(self.descLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="模块路径：", minSize=QSize(labelWidth, const.HEIGHT)))

        self.pathInputWidget = DragInputWidget(
            text=self.getModuleDir(),
            dirParam=["请选择您模块工作目录", self.openDir], isReadOnly=True,
            holderText="请拖动您模块的工作目录到此框或者点击右侧的文件夹图标选择您的模块路径，默认使用工程的路径",
            toolTip="不设置的话，默认使用工程的路径")
        hbox.addWidget(self.pathInputWidget)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加执行指令", onClicked=self.addCmd))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addWidget(WidgetUtil.createLabel(box, text="顺序调整:"))
        self.topPostionBtn = WidgetUtil.createPushButton(box, text="⬆️️", toolTip="移动到首行", isEnable=False,
                                                         onClicked=lambda: self.moveCmdPosition(0))
        hbox.addWidget(self.topPostionBtn)
        self.upOnePostionBtn = WidgetUtil.createPushButton(box, text="↑️️", toolTip="向上移动一行", isEnable=False,
                                                           onClicked=lambda: self.moveCmdPosition(self.currentRow - 1))
        hbox.addWidget(self.upOnePostionBtn)
        self.downOnePostionBtn = WidgetUtil.createPushButton(box, text="↓️", toolTip="向下移动一行", isEnable=False,
                                                             onClicked=lambda: self.moveCmdPosition(
                                                                 self.currentRow + 1))
        hbox.addWidget(self.downOnePostionBtn)
        self.bottomPostionBtn = WidgetUtil.createPushButton(box, text="⬇️️", toolTip="移动到末行", isEnable=False,
                                                            onClicked=lambda: self.moveCmdPosition(-1))
        hbox.addWidget(self.bottomPostionBtn)
        vbox.addLayout(hbox)

        self.cmdTableView = WidgetUtil.createTableView(box, clicked=self.tableClicked,
                                                       doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.cmdTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.cmdTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.cmdTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.cmdTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cmdTableView.customContextMenuRequested.connect(self.customRightMenu)
        self.updateCmdTableView()
        vbox.addWidget(self.cmdTableView, 1)
        return box

    def moveCmdPosition(self, newPos):
        LogUtil.d("moveCmdPosition", newPos)
        # 交换数据
        ListUtil.insert(self.cmdList, self.currentRow, newPos)
        # 更新table表格数据
        self.updateCmdTableView()
        # 更新当前选择的行
        self.currentRow = newPos if newPos >= 0 else len(self.cmdList) - 1
        self.cmdTableView.selectRow(self.currentRow)
        # 更新调整位置按钮的状态
        self.updatePositionBtnStatus()
        pass

    def getCurWorkingDir(self):
        path = self.pathInputWidget.text().strip()
        return path if path else self.openDir

    def addCmd(self):
        LogUtil.d("addCmd")
        AddOrEditCmdDialog(callback=self.addOrEditCmdCallback, moduleDir=self.getCurWorkingDir(), cmdList=self.cmdList,
                           optionGroups=self.optionGroups, cmdGroups=self.cmdGroups)
        pass

    def addOrEditCmdCallback(self, info):
        LogUtil.d("addOrEditCmdCallback", info)
        if info:
            self.cmdList.append(info)
        self.updateCmdTableView()
        pass

    def updatePositionBtnStatus(self):
        LogUtil.d("updatePositionBtnStatus")
        size = len(self.cmdList)
        self.topPostionBtn.setEnabled(self.currentRow > 0)
        self.upOnePostionBtn.setEnabled(self.currentRow > 0)
        self.downOnePostionBtn.setEnabled(0 <= self.currentRow < size - 1)
        self.bottomPostionBtn.setEnabled(0 <= self.currentRow < size - 1)
        pass

    def tableClicked(self):
        currentRow = self.cmdTableView.currentIndex().row()
        LogUtil.d("tableClicked", currentRow)
        if currentRow != self.currentRow:
            self.currentRow = currentRow
            self.updatePositionBtnStatus()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d("双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditCmdDialog(callback=self.addOrEditCmdCallback, moduleDir=self.getCurWorkingDir(), default=self.cmdList[row],
                           cmdList=self.cmdList, optionGroups=self.optionGroups, cmdGroups=self.cmdGroups)
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.cmdTableView.currentIndex().row()
        LogUtil.i("customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delCmd)
        menu.exec(self.cmdTableView.mapToGlobal(pos))
        pass

    def delCmd(self):
        cmd = self.cmdList[self.curDelRow][KEY_NAME]
        LogUtil.i(f"delCmd {cmd}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{cmd}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i("delTableItem")
        self.cmdList.remove(self.cmdList[self.curDelRow])
        self.updateCmdTableView()
        pass

    def updateCmdTableView(self):
        tableData = []
        for cmd in self.cmdList:
            dynArgs = DictUtil.get(cmd, KEY_DYNAMIC_ARGUMENTS, [])
            dynArgsShowTxt = []
            for dynArg in dynArgs:
                dynArgsShowTxt += dynArg[KEY_OPTION_NAMES]
            tableData.append({
                KEY_NAME: cmd[KEY_NAME],
                KEY_DESC: cmd[KEY_DESC],
                KEY_PROGRAM: cmd[KEY_PROGRAM],
                KEY_WORKING_DIR: cmd[KEY_WORKING_DIR],
                KEY_ARGUMENTS: cmd[KEY_ARGUMENTS],
                KEY_DYNAMIC_ARGUMENTS: dynArgsShowTxt,
                KEY_CMD_GROUPS: DictUtil.get(cmd, KEY_CMD_GROUPS, []),
                KEY_IGNORE_FAILED: DictUtil.get(cmd, KEY_IGNORE_FAILED, False)
            })
        WidgetUtil.addTableViewData(self.cmdTableView, tableData,
                                    headerLabels=["执行指令名", "描述", "指令", "工作空间", "指令参数", "动态参数选项", "指令所属群组", "执行失败可忽略"])
        # WidgetUtil.tableViewSetColumnWidth(self.cmdTableView, 0, 100)
        pass

    def acceptFunc(self):
        LogUtil.d("acceptFunc")
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入模块名")
            return
        desc = self.descLineEdit.text().strip()
        if not desc:
            WidgetUtil.showErrorDialog(message="请输入模块描述")
            return
        path = self.pathInputWidget.text().strip()
        isRelativePath = False
        if path and self.openDir and path.startswith(self.openDir):
            path = path.replace(self.openDir, "")
            isRelativePath = True
        if not path:
            # 没有设置path，认为是相对路径，使用工程路径
            isRelativePath = True

        if self.isAdd:
            for item in self.moduleList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的模块，{name}已经存在了。")
                    return

        id = MD5Util.md5(name)

        if self.default is None:
            self.default = {}
        self.default[KEY_ID] = id
        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_PATH] = path
        self.default[KEY_IS_RELATIVE_PATH] = isRelativePath
        self.default[KEY_CMD_LIST] = self.cmdList

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditProjectDialog(callback=lambda it: LogUtil.d("callback", it), isDebug=True)
    window = AddOrEditModuleDialog(callback=lambda it: LogUtil.d("callback", it),
                                   isDebug=True)
    window.show()
    sys.exit(app.exec_())
