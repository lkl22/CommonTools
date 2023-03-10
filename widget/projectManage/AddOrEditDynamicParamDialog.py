# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditDynamicParamDialog.py
# 定义一个AddOrEditDynamicParamDialog类实现添加、编辑动态参数功能
import copy

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditDynamicParamDialog"


class AddOrEditDynamicParamDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, dynParamList=None, optionGroups=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditDynamicParamDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditDynamicParamDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Dynamic Param Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑动态参数"))
        if dynParamList is None:
            dynParamList = []
        self.dynParamList = dynParamList
        self.callback = callback
        self.isAdd = default is None
        if not default:
            default = {}
        self.default = default
        if not optionGroups:
            optionGroups = []
        self.optionGroups = optionGroups

        self.setObjectName("AddOrEditDynamicParamDialog")
        self.resize(AddOrEditDynamicParamDialog.WINDOW_WIDTH, AddOrEditDynamicParamDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditDynamicParamDialog.WINDOW_WIDTH, AddOrEditDynamicParamDialog.WINDOW_HEIGHT)

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
        self.optionComboBox = WidgetUtil.createComboBox(self)
        hBox.addWidget(self.optionComboBox, 1)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        self.capitalizeCheckBox = WidgetUtil.createCheckBox(self, text="首字母是否大写",
                                                            toolTip="默认首字母大写，会在拼接时将首字母转为大写。",
                                                            isChecked=DictUtil.get(self.default, KEY_NEED_CAPITALIZE,
                                                                                   DEFAULT_VALUE_NEED_CAPITALIZE))
        hBox.addWidget(self.capitalizeCheckBox)
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
                    return
            self.optionComboBox.setCurrentText("")
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入动态参数名")
            return

        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.dynParamList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的动态参数名，{name}已经存在了，不能重复添加")
                    return

        optionGroup = self.optionGroupComboBox.currentData()
        if not optionGroup:
            WidgetUtil.showErrorDialog(message="请选择选项所属群组")
            return

        option = self.optionComboBox.currentData()
        if not option:
            WidgetUtil.showErrorDialog(message="请选择选项")
            return

        desc = self.descLineEdit.text().strip()

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_OPTION_GROUP] = optionGroup
        self.default[KEY_OPTION] = option
        self.default[KEY_NEED_CAPITALIZE] = self.capitalizeCheckBox.isChecked()
        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditDynamicParamDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window = AddOrEditDynamicParamDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                         default={KEY_OPTION_GROUP: "buildParams1", KEY_OPTION: "packageType1", KEY_NAME: 'productFlavor',
                                                  KEY_DESC: '产品渠道信息'},
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
