# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditCmdDialog.py
# 定义一个AddOrEditCmdDialog类实现添加、编辑执行指令功能
import copy

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QScrollArea, QFrame, QAbstractItemView

from constant.WidgetConst import *
from util.ClipboardUtil import ClipboardUtil
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.AddOrEditDynamicParamDialog import AddOrEditDynamicParamDialog
from widget.projectManage.ProjectManager import *
from widget.projectManage.ProjectManagerUtil import ProjectManagerUtil

TAG = "AddOrEditCmdDialog"


class AddOrEditCmdDialog(QtWidgets.QDialog):
    def __init__(self, callback, moduleDir=None, default=None, cmdList=None, optionGroups=None, cmdGroups=None,
                 isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditCmdDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditCmdDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.6)
        LogUtil.d(TAG, "Add or Edit Cmd Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑执行指令"))
        self.callback = callback
        if cmdList is None:
            cmdList = []
        self.cmdList = cmdList

        if optionGroups is None:
            optionGroups = []
        # 拷贝，避免影响原有数据
        # self.optionGroups = copy.deepcopy(optionGroups)
        self.optionGroups = optionGroups

        self.isAdd = default is None
        if not default:
            default = {KEY_DYNAMIC_ARGUMENTS: [], KEY_CMD_GROUPS: []}
        else:
            if KEY_DYNAMIC_ARGUMENTS not in default:
                default[KEY_DYNAMIC_ARGUMENTS] = []
            if KEY_CMD_GROUPS not in default:
                default[KEY_CMD_GROUPS] = []
        # 删除无效的动态参数
        ProjectManagerUtil.delInvalidDynParam(dynParams=default[KEY_DYNAMIC_ARGUMENTS], optionGroups=self.optionGroups)
        self.dynamicArguments = copy.deepcopy(default[KEY_DYNAMIC_ARGUMENTS])
        self.default = default

        if cmdGroups is None:
            cmdGroups = []
        self.cmdGroups = cmdGroups
        self.cmdGroupWidgets = []
        # 拷贝，避免影响原有数据
        self.selectedCmdGroups = copy.deepcopy(default[KEY_CMD_GROUPS])

        self.isDebug = isDebug

        self.moduleDir = moduleDir if moduleDir else './'

        self.setObjectName("AddOrEditCmdDialog")
        self.resize(AddOrEditCmdDialog.WINDOW_WIDTH, AddOrEditCmdDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditCmdDialog.WINDOW_WIDTH, AddOrEditCmdDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        scrollAres = QScrollArea(self)
        scrollAres.setWidgetResizable(True)
        scrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        scrollAres.setWidget(scrollAreaWidget)
        vLayout.addWidget(scrollAres, 1)

        # 进行垂直布局
        self.vLayout = WidgetUtil.createVBoxLayout(scrollAreaWidget, margins=QMargins(5, 5, 5, 5))
        self.spacerItem = WidgetUtil.createVSpacerItem(1, 1)
        self.vLayout.addItem(self.spacerItem)

        labelWidth = 150

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Name：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      holderText="需要执行的命令行指令别名，唯一，用于区分多条指令",
                                                      isReadOnly=not self.isAdd)
        hbox.addWidget(self.nameLineEdit)
        self.vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Description：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      holderText="需要执行的命令行指令描述")
        hbox.addWidget(self.descLineEdit)
        self.vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Program：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.programInputWidget = DragInputWidget(text=DictUtil.get(default, KEY_PROGRAM),
                                                  fileParam=['', self.moduleDir, '', ''],
                                                  dirParam=["", self.moduleDir],
                                                  isReadOnly=False,
                                                  holderText="需要执行的命令行指令",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.programInputWidget)
        self.vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Working directory：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.workDirInputWidget = DragInputWidget(text=self.getCmdDir(),
                                                  fileParam=['', self.moduleDir, '', ''],
                                                  dirParam=["", self.moduleDir],
                                                  isReadOnly=False,
                                                  holderText="执行命令行指令所在的工作空间，不填，默认跟随模块工作目录",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.workDirInputWidget)
        self.vLayout.addLayout(hbox)

        self.ignoreFailedCheckBox = WidgetUtil.createCheckBox(self, text="忽略指令执行失败",
                                                              toolTip="勾选了该指令失败了会继续执行后续的指令，否则直接终止该模块的执行，并标记为失败。",
                                                              isChecked=DictUtil.get(default, KEY_IGNORE_FAILED, False))
        self.vLayout.addWidget(self.ignoreFailedCheckBox)

        if self.cmdGroups:
            self.createCmdGroupSelectedWidget()

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Arguments：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.argumentsLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_ARGUMENTS),
                                                           holderText="需要执行的命令行指令参数，多个参数使用空格分隔")
        hbox.addWidget(self.argumentsLineEdit)
        self.vLayout.addLayout(hbox)

        if self.optionGroups:
            self.createAddDynParamWidget()
        else:
            self.spacerItem = WidgetUtil.createLabel(self)
            self.vLayout.addWidget(self.spacerItem, 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def getCmdDir(self):
        workingDir = DictUtil.get(self.default, KEY_WORKING_DIR, "")
        return self.moduleDir + workingDir if DictUtil.get(self.default, KEY_IS_RELATIVE_PATH, False) else workingDir

    def createCmdGroupSelectedWidget(self):
        self.vLayout.addWidget(WidgetUtil.createLabel(self, text="选择指令所属分组："))

        hbox = None
        if len(self.cmdGroups) < 3:
            maxCol = 1
        else:
            maxCol = 6
        for index, item in enumerate(self.cmdGroups):
            if index % maxCol == 0:
                hbox = WidgetUtil.createHBoxLayout(spacing=10)
                self.vLayout.addLayout(hbox)
            checkBox = WidgetUtil.createCheckBox(self, text=DictUtil.get(item, KEY_NAME),
                                                 toolTip=DictUtil.get(item, KEY_DESC),
                                                 isChecked=item[KEY_NAME] in self.selectedCmdGroups,
                                                 clicked=self.cmdGroupSelectedChanged)
            self.cmdGroupWidgets.append(checkBox)
            hbox.addWidget(checkBox)
        self.vLayout.addLayout(hbox)
        pass

    def cmdGroupSelectedChanged(self):
        self.selectedCmdGroups.clear()
        for index, widget in enumerate(self.cmdGroupWidgets):
            if widget.isChecked():
                self.selectedCmdGroups.append(widget.text())
        LogUtil.d(TAG, "cmdGroupSelectedChanged", self.selectedCmdGroups)
        pass

    def createAddDynParamWidget(self):
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(self, text="添加动态参数", onClicked=self.addDynParam))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.vLayout.addLayout(hbox)

        self.cmdTableView = WidgetUtil.createTableView(self, doubleClicked=self.tableDoubleClicked)
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
        self.vLayout.addWidget(self.cmdTableView, 1)
        pass

    def addDynParam(self):
        LogUtil.d(TAG, "addDynParam")
        AddOrEditDynamicParamDialog(callback=self.addOrEditDynParamCallback,
                                    dynParamList=self.dynamicArguments,
                                    optionGroups=self.optionGroups)
        pass

    def addOrEditDynParamCallback(self, info):
        LogUtil.d(TAG, "addOrEditDynParamCallback", info)
        if info:
            self.dynamicArguments.append(info)
        self.updateCmdTableView()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditDynamicParamDialog(callback=self.addOrEditDynParamCallback,
                                    default=self.dynamicArguments[row],
                                    dynParamList=self.dynamicArguments,
                                    optionGroups=self.optionGroups)
        pass

    def customRightMenu(self, pos):
        self.curRow = self.cmdTableView.currentIndex().row()
        LogUtil.i(TAG, "customRightMenu", pos, ' row: ', self.curRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delDynParam, action2="Copy", func2=self.copyToClipboard)
        menu.exec(self.cmdTableView.mapToGlobal(pos))
        pass

    def delDynParam(self):
        dynParamName = self.dynamicArguments[self.curRow][KEY_NAME]
        LogUtil.i(TAG, f"delDynParam {dynParamName}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{dynParamName}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def copyToClipboard(self):
        ClipboardUtil.copyToClipboard("{" + self.dynamicArguments[self.curRow][KEY_NAME] + "}")
        pass

    def delTableItem(self):
        LogUtil.i(TAG, "delTableItem")
        self.dynamicArguments.remove(self.dynamicArguments[self.curRow])
        self.updateCmdTableView()
        pass

    def updateCmdTableView(self):
        tableData = []
        for dynParam in self.dynamicArguments:
            tableData.append({
                KEY_NAME: dynParam[KEY_NAME],
                KEY_DESC: DictUtil.get(dynParam, KEY_DESC, ""),
                KEY_OPTION_GROUP: dynParam[KEY_OPTION_GROUP],
                KEY_OPTION: dynParam[KEY_OPTION],
                KEY_NEED_CAPITALIZE: DictUtil.get(dynParam, KEY_NEED_CAPITALIZE, DEFAULT_VALUE_NEED_CAPITALIZE)
            })
        WidgetUtil.addTableViewData(self.cmdTableView, tableData,
                                    headerLabels=["动态参数名称", "动态参数描述", "选项所属群组", "选项", "是否需要添加空格"])
        # WidgetUtil.tableViewSetColumnWidth(self.cmdTableView, 0, 100)
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入需要执行的命令行指令别名")
            return
        program = self.programInputWidget.text().strip()
        if not program:
            WidgetUtil.showErrorDialog(message="请输入需要执行的命令行指令")
            return
        if DictUtil.get(self.default, KEY_NAME) != name:
            for item in self.cmdList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的指令别名，{name}已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()
        workDir = self.workDirInputWidget.text().strip()
        arguments = self.argumentsLineEdit.text().strip()
        if not self.default:
            self.default = {}

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_PROGRAM] = program

        isRelativePath = False
        if workDir and self.moduleDir and workDir.startswith(self.moduleDir):
            workDir = workDir.replace(self.moduleDir, "")
            isRelativePath = True
        if not workDir:
            # 没有设置workDir，认为是相对路径，使用模块路径
            isRelativePath = True
        self.default[KEY_WORKING_DIR] = workDir
        self.default[KEY_IS_RELATIVE_PATH] = isRelativePath
        self.default[KEY_CMD_GROUPS] = self.selectedCmdGroups
        self.default[KEY_ARGUMENTS] = arguments
        self.default[KEY_IGNORE_FAILED] = self.ignoreFailedCheckBox.isChecked()
        self.default[KEY_DYNAMIC_ARGUMENTS] = self.dynamicArguments

        if self.isDebug:
            self.callback(self.default)
        else:
            self.callback(self.default if self.isAdd else None)
        LogUtil.d(TAG, "acceptFunc", self.default)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                default={'name': 'ls操作', 'desc': 'ls -l', 'program': 'ls', 'workingDir': './',
                                         'arguments': '-l'},
                                optionGroups=[
                                    {'desc': '构建参数', 'id': '25ce396132a320ac6fb53346ab7d450f', 'name': 'buildParams',
                                     'options': [{'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType',
                                                  'optionValues': [
                                                      {'desc': '支持动态模块的打包', 'input': '', 'value': 'bundle'},
                                                      {'desc': '正常打全量包', 'input': '', 'value': 'assemble'}]},
                                                 {'default': 1, 'desc': '打包环境渠道', 'echo': '请输入环境渠道',
                                                  'name': 'productFlavors',
                                                  'optionValues': [{'desc': '测试环境', 'input': 'C', 'value': 'staging'},
                                                                   {'desc': '现网环境', 'input': 'A', 'value': 'product'},
                                                                   {'desc': '镜像环境', 'input': 'B', 'value': 'mirror'}]},
                                                 {'default': 0, 'desc': '打包类型 - debug、release', 'echo': '请输入打包类型',
                                                  'name': 'buildType',
                                                  'optionValues': [{'desc': 'debug包', 'input': 'A', 'value': 'debug'},
                                                                   {'desc': 'release包', 'input': 'B',
                                                                    'value': 'release'}]}]},
                                    {'desc': '构建参数1', 'id': '25ce396132a320ac6fb53346ab7d4111', 'name': 'buildParams1',
                                     'options': [{'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType1',
                                                  'optionValues': [
                                                      {'desc': '支持动态模块的打包', 'input': '', 'value': 'bundle'},
                                                      {'desc': '正常打全量包', 'input': '', 'value': 'assemble'}]},
                                                 {'default': 1, 'desc': '打包环境渠道', 'echo': '请输入环境渠道',
                                                  'name': 'productFlavors1',
                                                  'optionValues': [{'desc': '测试环境', 'input': 'C', 'value': 'staging'},
                                                                   {'desc': '现网环境', 'input': 'A', 'value': 'product'},
                                                                   {'desc': '镜像环境', 'input': 'B', 'value': 'mirror'}]},
                                                 {'default': 0, 'desc': '打包类型 - debug、release', 'echo': '请输入打包类型',
                                                  'name': 'buildType1',
                                                  'optionValues': [{'desc': 'debug包', 'input': 'A', 'value': 'debug'},
                                                                   {'desc': 'release包', 'input': 'B',
                                                                    'value': 'release'}]}]},
                                    {'desc': '构建参数2', 'id': '25ce396132a320ac6fb53346abeee1', 'name': 'buildParams2',
                                     'options': [{'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType2',
                                                  'optionValues': [
                                                      {'desc': '支持动态模块的打包', 'input': '', 'value': 'bundle'},
                                                      {'desc': '正常打全量包', 'input': '', 'value': 'assemble'}]},
                                                 {'default': 1, 'desc': '打包环境渠道', 'echo': '请输入环境渠道',
                                                  'name': 'productFlavors2',
                                                  'optionValues': [{'desc': '测试环境', 'input': 'C', 'value': 'staging'},
                                                                   {'desc': '现网环境', 'input': 'A', 'value': 'product'},
                                                                   {'desc': '镜像环境', 'input': 'B', 'value': 'mirror'}]},
                                                 {'default': 0, 'desc': '打包类型 - debug、release', 'echo': '请输入打包类型',
                                                  'name': 'buildType2',
                                                  'optionValues': [{'desc': 'debug包', 'input': 'A', 'value': 'debug'},
                                                                   {'desc': 'release包', 'input': 'B',
                                                                    'value': 'release'}]}]}],
                                cmdGroups=[{"name": "dd", "desc": "dd"}, {"name": "eee", "desc": "dgggd"}],
                                isDebug=True)
    # window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
