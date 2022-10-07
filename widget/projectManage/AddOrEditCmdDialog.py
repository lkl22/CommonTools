# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditCmdDialog.py
# 定义一个AddOrEditCmdDialog类实现添加、编辑执行指令功能
import copy

from PyQt5.QtWidgets import QScrollArea, QFrame

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditCmdDialog"


class OptionGroupWidget(QFrame):
    def __init__(self, optionGroupInfo, optionNames, delFunc):
        super(OptionGroupWidget, self).__init__()
        self.optionGroupInfo = None
        self.optionNames = None
        self.optionWidgets = []
        self.setObjectName("OptionGroupWidget")
        self.vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        self.optionGroupNameLabel = WidgetUtil.createLabel(self)
        self.vbox.addWidget(self.optionGroupNameLabel)

        # 为窗口添加QActions
        self.addAction(WidgetUtil.createAction(self, text="删除", func=lambda: delFunc(self, self.optionGroupInfo)))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setStyleSheet("OptionGroupWidget{border:1px solid rgb(255,0,0)}")

        self.updateUi(optionGroupInfo, optionNames)
        pass

    def updateUi(self, optionGroupInfo, optionNames):
        self.optionGroupInfo = optionGroupInfo
        self.optionNames = optionNames
        self.optionGroupNameLabel.setText(f"{optionGroupInfo[KEY_NAME]}（{optionGroupInfo[KEY_DESC]}）")
        options = DictUtil.get(optionGroupInfo, KEY_OPTIONS)
        optionsLen = len(options)
        while optionsLen < len(self.optionWidgets):
            widget = self.optionWidgets[optionsLen]
            self.vbox.removeWidget(widget)
            widget.deleteLater()
            self.optionWidgets.remove(widget)
        for index, option in enumerate(options):
            if index >= len(self.optionWidgets):
                widget = WidgetUtil.createCheckBox(self, clicked=self.selectedChanged)
                self.optionWidgets.append(widget)
                self.vbox.addWidget(widget)
            else:
                widget = self.optionWidgets[index]
            widget.setText(f"{DictUtil.get(option, KEY_NAME)}（{DictUtil.get(option, KEY_DESC)}）")
            widget.setToolTip(f"支持的选项：{DictUtil.get(option, KEY_OPTION_VALUES)}")
            widget.setChecked(option[KEY_NAME] in optionNames)
        pass

    def selectedChanged(self, status):
        LogUtil.d("selectedChanged", status)
        options = DictUtil.get(self.optionGroupInfo, KEY_OPTIONS)
        self.optionNames.clear()
        for index, widget in enumerate(self.optionWidgets):
            if widget.isChecked():
                self.optionNames.append(options[index][KEY_NAME])
        LogUtil.d("selectedChanged", self.optionNames)
        pass


class AddOrEditCmdDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, cmdList=None, optionGroups=None, cmdGroups=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        AddOrEditCmdDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditCmdDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d("Add or Edit Cmd Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑执行指令"))
        self.callback = callback
        if cmdList is None:
            cmdList = []
        self.cmdList = cmdList

        if optionGroups is None:
            optionGroups = []
        self.srcOptionGroups = optionGroups
        # 拷贝，避免影响原有数据
        self.optionGroups = copy.deepcopy(optionGroups)

        self.isAdd = default is None
        if not default:
            default = {KEY_DYNAMIC_ARGUMENTS: [], KEY_CMD_GROUPS: []}
        else:
            if KEY_DYNAMIC_ARGUMENTS not in default:
                default[KEY_DYNAMIC_ARGUMENTS] = []
            if KEY_CMD_GROUPS not in default:
                default[KEY_CMD_GROUPS] = []
        self.dynamicArguments = copy.deepcopy(default[KEY_DYNAMIC_ARGUMENTS])
        self.dynamicOptionGroup = []
        self.default = default

        if cmdGroups is None:
            cmdGroups = []
        self.cmdGroups = cmdGroups
        self.cmdGroupWidgets = []
        # 拷贝，避免影响原有数据
        self.selectedCmdGroups = copy.deepcopy(default[KEY_CMD_GROUPS])

        self.dynamicArgumentWidgets = []
        self.isDebug = isDebug

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
                                                  fileParam=['', './', '', ''],
                                                  dirParam=["", "./"],
                                                  isReadOnly=False,
                                                  holderText="需要执行的命令行指令",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.programInputWidget)
        self.vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Working directory：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.workDirInputWidget = DragInputWidget(text=DictUtil.get(default, KEY_WORKING_DIR),
                                                  fileParam=['', './', '', ''],
                                                  dirParam=["", "./"],
                                                  isReadOnly=False,
                                                  holderText="执行命令行指令所在的工作空间，不填，默认跟随模块工作目录",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.workDirInputWidget)
        self.vLayout.addLayout(hbox)

        if self.cmdGroups:
            self.createCmdGroupSelectedWidget()

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Arguments：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.argumentsLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_ARGUMENTS),
                                                           holderText="需要执行的命令行指令参数，多个参数使用空格分隔")
        hbox.addWidget(self.argumentsLineEdit)
        self.vLayout.addLayout(hbox)

        if self.optionGroups:
            self.createOptionGroupSelectedWidget(labelWidth)

        self.spacerItem = WidgetUtil.createLabel(self)
        self.vLayout.addWidget(self.spacerItem, 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)

        self.handleDynamicArgumentsData()
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def createCmdGroupSelectedWidget(self):
        self.vLayout.addWidget(WidgetUtil.createLabel(self, text="选择指令所属分组："))

        hbox = None
        maxCol = 1
        for index, item in enumerate(self.cmdGroups):
            if index % maxCol == 0:
                hbox = WidgetUtil.createHBoxLayout(spacing=10)
                self.vLayout.addLayout(hbox)
            checkBox = WidgetUtil.createCheckBox(self, text=DictUtil.get(item, KEY_NAME), toolTip=DictUtil.get(item, KEY_DESC),
                                                 isChecked=ListUtil.find(self.selectedCmdGroups, KEY_NAME, item[KEY_NAME]) is not None,
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

    def createOptionGroupSelectedWidget(self, labelWidth):
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Dynamic Arguments：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.dynamicArgumentsComboBox = WidgetUtil.createComboBox(self,
                                                                  toolTip="需要执行的命令行指令参数，可以通过用户选择自动拼接，按照选项分组拼接命令参数",
                                                                  activated=self.dynamicArgumentsChanged)
        hbox.addWidget(self.dynamicArgumentsComboBox, 1)
        self.vLayout.addLayout(hbox)

        self.needSpaceCheckBox = WidgetUtil.createCheckBox(self, text="是否需要添加空格",
                                                           toolTip="跟固定参数拼接时是否需要添加空格，默认需要添加",
                                                           isChecked=DictUtil.get(self.default, KEY_NEED_SPACE,
                                                                                  DEFAULT_VALUE_NEED_SPACE))
        self.vLayout.addWidget(self.needSpaceCheckBox)
        pass

    def handleDynamicArgumentsData(self):
        # 拷贝避免影响原始数据
        self.optionGroups = copy.deepcopy(self.srcOptionGroups)
        if not self.optionGroups:
            return
        self.dynamicOptionGroup.clear()
        needDelDynamicArguments = []
        for item in self.dynamicArguments:
            optionGroup = ListUtil.find(self.optionGroups, KEY_ID, item[KEY_OPTION_GROUP_ID])
            if optionGroup:
                # 工程的选项群组里包含该动态参数配置项
                self.dynamicOptionGroup.append(optionGroup)
                # 已经在下面显示里从下拉选择框里移除
                self.optionGroups.remove(optionGroup)
            else:
                # 之前的配置项已经删除
                needDelDynamicArguments.append(item)
        for item in needDelDynamicArguments:
            self.dynamicArguments.remove(item)

        self.updateDynamicArgumentsComboBox()
        self.updateDynamicOptionWidget()
        pass

    def updateDynamicArgumentsComboBox(self):
        self.dynamicArgumentsComboBox.clear()
        # self.dynamicArgumentsComboBox.addItem("", -1)
        for index, item in enumerate(self.optionGroups):
            self.dynamicArgumentsComboBox.addItem(
                f"{DictUtil.get(item, KEY_NAME)}（{DictUtil.get(item, KEY_DESC)}）", userData=index)
        self.dynamicArgumentsComboBox.setCurrentIndex(-1)
        pass

    def dynamicArgumentsChanged(self, index):
        LogUtil.d("dynamicArgumentsChanged", index)
        curOptionGroup = self.optionGroups[index]
        self.optionGroups.remove(curOptionGroup)
        self.updateDynamicArgumentsComboBox()
        self.dynamicOptionGroup.append(curOptionGroup)
        self.dynamicArguments.append({KEY_OPTION_GROUP_ID: curOptionGroup[KEY_ID], KEY_OPTION_NAMES: []})
        self.updateDynamicOptionWidget()

    def updateDynamicOptionWidget(self):
        dynamicArgumentLen = len(self.dynamicOptionGroup)
        while dynamicArgumentLen < len(self.dynamicArgumentWidgets):
            widget = self.dynamicArgumentWidgets[dynamicArgumentLen]
            self.vLayout.removeWidget(widget)
            widget.deleteLater()
            self.dynamicArgumentWidgets.remove(widget)
        self.vLayout.removeWidget(self.needSpaceCheckBox)
        self.vLayout.removeWidget(self.spacerItem)
        for index, option in enumerate(self.dynamicOptionGroup):
            optionNames = ListUtil.get(self.dynamicArguments, KEY_OPTION_GROUP_ID, option[KEY_ID], KEY_OPTION_NAMES, [])
            if index >= len(self.dynamicArgumentWidgets):
                widget = OptionGroupWidget(option, optionNames, delFunc=self.delOptionGroupWidget)
                self.dynamicArgumentWidgets.append(widget)
                self.vLayout.addWidget(widget)
            else:
                widget = self.dynamicArgumentWidgets[index]
                widget.updateUi(option, optionNames)
        self.vLayout.addWidget(self.needSpaceCheckBox)
        self.vLayout.addWidget(self.spacerItem, 1)

    def delOptionGroupWidget(self, widget: OptionGroupWidget, optionGroupInfo):
        LogUtil.d("delOptionGroupWidget")
        delDynArg = ListUtil.find(self.dynamicArguments, KEY_OPTION_GROUP_ID, optionGroupInfo[KEY_ID])
        self.dynamicArguments.remove(delDynArg)
        self.handleDynamicArgumentsData()
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
        self.default[KEY_WORKING_DIR] = workDir
        self.default[KEY_CMD_GROUPS] = self.selectedCmdGroups
        self.default[KEY_ARGUMENTS] = arguments
        # 清除空的动态参数配置
        for item in self.dynamicArguments:
            if not item[KEY_OPTION_NAMES]:
                self.dynamicArguments.remove(item)
        self.default[KEY_DYNAMIC_ARGUMENTS] = self.dynamicArguments
        self.default[KEY_NEED_SPACE] = self.needSpaceCheckBox.isChecked()

        if self.isDebug:
            self.callback(self.default)
        else:
            self.callback(self.default if self.isAdd else None)
        LogUtil.d(TAG, "acceptFunc", self.default)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d("callback", it),
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
    # window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d("callback", it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
