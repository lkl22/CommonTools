# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditPreconditionsDialog.py
# 定义一个AddOrEditPreconditionsDialog类实现添加、编辑动态参数功能
import copy

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditPreconditionsDialog"


class AddOrEditPreconditionDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, preconditionList=None, optionGroups=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditPreconditionDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditPreconditionDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Preconditions Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑指令执行前置条件"))
        if preconditionList is None:
            preconditionList = []
        self.preconditionList = preconditionList
        self.callback = callback
        self.isAdd = default is None
        if not default:
            default = {}
        self.default = default
        if not optionGroups:
            optionGroups = []
        self.optionGroups = optionGroups

        self.setObjectName("AddOrEditPreconditionsDialog")
        self.resize(AddOrEditPreconditionDialog.WINDOW_WIDTH, AddOrEditPreconditionDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditPreconditionsDialog.WINDOW_WIDTH, AddOrEditPreconditionsDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 90

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="Name：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      toolTip="动态参数名称")
        hBox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="Description：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      toolTip="动态参数描述")
        hBox.addWidget(self.descLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="选项所属群组：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.optionGroupComboBox = WidgetUtil.createComboBox(self, activated=self.optionGroupChanged)
        self.optionGroupComboBox.addItem("", "")
        for index, item in enumerate(self.optionGroups):
            self.optionGroupComboBox.addItem(f"{item[KEY_NAME]}（{item[KEY_DESC]}）", item[KEY_NAME])
        hBox.addWidget(self.optionGroupComboBox, 1)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="选项：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.optionComboBox = WidgetUtil.createComboBox(self, activated=self.optionChanged)
        hBox.addWidget(self.optionComboBox, 1)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="选项值：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.optionValueComboBox = WidgetUtil.createComboBox(self)
        hBox.addWidget(self.optionValueComboBox, 1)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        self.eqCheckBox = WidgetUtil.createRadioButton(self, text="值相等", toolTip="选项的值等于当前选择的值时条件才满足",
                                                       autoExclusive=True,
                                                       isChecked=DictUtil.get(self.default,
                                                                              KEY_PRECONDITION_LOGIC) == PRECONDITION_LOGIC_EQ)
        self.neqCheckBox = WidgetUtil.createRadioButton(self, text="值不相等", toolTip="选项的值不等于当前选择的值时条件才满足",
                                                        autoExclusive=True,
                                                        isChecked=DictUtil.get(self.default,
                                                                               KEY_PRECONDITION_LOGIC) == PRECONDITION_LOGIC_NEQ)
        hBox.addWidget(self.eqCheckBox)
        hBox.addWidget(self.neqCheckBox)
        vLayout.addLayout(hBox)

        # vLayout.addWidget(WidgetUtil.createLabel(self), 1)
        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)

        self.updateOptionGroupComboBox()
        self.updateOptionComboBox(True)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def optionGroupChanged(self):
        LogUtil.i(TAG, "optionGroupChanged")
        self.updateOptionComboBox()
        pass

    def updateOptionGroupComboBox(self):
        defaultGroup = DictUtil.get(self.default, KEY_OPTION_GROUP)
        if defaultGroup:
            index = ListUtil.findIndex(self.optionGroups, KEY_NAME, defaultGroup)
            self.optionGroupComboBox.setCurrentIndex(index + 1)
        else:
            self.optionGroupComboBox.setCurrentText("")
        pass

    def updateOptionComboBox(self, needDefaultValue=False):
        self.optionComboBox.clear()

        optionGroup = self.optionGroupComboBox.currentData()
        if optionGroup:
            options = ListUtil.get(self.optionGroups, KEY_NAME, optionGroup, KEY_OPTIONS)
            if options:
                self.optionComboBox.addItem("", "")
                for index, item in enumerate(options):
                    self.optionComboBox.addItem(f"{item[KEY_NAME]}（{item[KEY_DESC]}）", item[KEY_NAME])
                if needDefaultValue:
                    defaultOption = DictUtil.get(self.default, KEY_OPTION)
                    self.optionComboBox.setCurrentIndex(ListUtil.findIndex(options, KEY_NAME, defaultOption) + 1)
                    self.updateOptionValueComboBox(needDefaultValue=needDefaultValue)
                    return
            self.optionComboBox.setCurrentText("")
        self.updateOptionValueComboBox(needDefaultValue=needDefaultValue)
        pass

    def optionChanged(self):
        LogUtil.i(TAG, "optionChanged")
        self.updateOptionValueComboBox()

    def updateOptionValueComboBox(self, needDefaultValue=False):
        self.optionValueComboBox.clear()

        optionGroup = self.optionGroupComboBox.currentData()
        option = self.optionComboBox.currentData()
        if optionGroup and option:
            options = ListUtil.get(self.optionGroups, KEY_NAME, optionGroup, KEY_OPTIONS)
            optionValues = ListUtil.get(options, KEY_NAME, option, KEY_OPTION_VALUES)
            if optionValues:
                self.optionValueComboBox.addItem("", "")
                for index, item in enumerate(optionValues):
                    self.optionValueComboBox.addItem(f"{item[KEY_VALUE]}（{item[KEY_DESC]}）", item[KEY_VALUE])
                if needDefaultValue:
                    defaultOptionValue = DictUtil.get(self.default, KEY_OPTION_VALUE)
                    self.optionValueComboBox.setCurrentIndex(
                        ListUtil.findIndex(optionValues, KEY_VALUE, defaultOptionValue) + 1)
                    return
            self.optionValueComboBox.setCurrentText("")
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入前置条件名")
            return

        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.preconditionList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的前置条件名，{name}已经存在了，不能重复添加")
                    return

        optionGroup = self.optionGroupComboBox.currentData()
        if not optionGroup:
            WidgetUtil.showErrorDialog(message="请选择选项所属群组")
            return

        option = self.optionComboBox.currentData()
        if not option:
            WidgetUtil.showErrorDialog(message="请选择选项")
            return

        optionValue = self.optionValueComboBox.currentData()
        if not optionValue:
            WidgetUtil.showErrorDialog(message="请选择选项值")
            return

        desc = self.descLineEdit.text().strip()

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_OPTION_GROUP] = optionGroup
        self.default[KEY_OPTION] = option
        self.default[KEY_OPTION_VALUE] = optionValue
        self.default[KEY_PRECONDITION_LOGIC] = PRECONDITION_LOGIC_NEQ if self.neqCheckBox.isChecked() else PRECONDITION_LOGIC_EQ
        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditPreconditionsDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window = AddOrEditPreconditionDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                         default={
                                             KEY_NAME: 'productFlavor',
                                             KEY_DESC: '产品渠道信息',
                                             KEY_OPTION_GROUP: "buildParams1",
                                             KEY_OPTION: "packageType1",
                                             KEY_OPTION_VALUE: "assemble"},
                                         optionGroups=[
                                             {'desc': '构建参数', 'id': '25ce396132a320ac6fb53346ab7d450f',
                                              'name': 'buildParams',
                                              'options': [
                                                  {'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType',
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
                                             {'desc': '构建参数1', 'id': '25ce396132a320ac6fb53346ab7d4111',
                                              'name': 'buildParams1',
                                              'options': [
                                                  {'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType1',
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
                                             {'desc': '构建参数2', 'id': '25ce396132a320ac6fb53346abeee1',
                                              'name': 'buildParams2',
                                              'options': [
                                                  {'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType2',
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
                                         isDebug=True)
    window.show()
    sys.exit(app.exec_())
