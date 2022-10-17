# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditOptionDialog.py
# 定义一个AddOrEditOptionDialog类实现添加、编辑执行指令参数选项功能
import copy

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.projectManage.ProjectManager import *


class AddOrEditOptionDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, optionList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditOptionDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditOptionDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("Add or Edit Option Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑执行指令参数选项"))
        if optionList is None:
            optionList = []
        self.optionList = optionList
        self.callback = callback
        self.isAdd = default is None
        if not default:
            default = {KEY_DEFAULT: -1, KEY_OPTION_VALUES: []}
        self.default = default
        self.optionValues = copy.deepcopy(default[KEY_OPTION_VALUES])
        self.curOptionValueIndex = self.default[KEY_DEFAULT]

        self.setObjectName("AddOrEditOptionDialog")
        self.resize(AddOrEditOptionDialog.WINDOW_WIDTH, AddOrEditOptionDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditOptionDialog.WINDOW_WIDTH, AddOrEditOptionDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 90

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Name：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      holderText="需要执行的命令行指令别名，唯一，用于区分多条指令",
                                                      isReadOnly=not self.isAdd)
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Description：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      holderText="需要执行的命令行指令描述")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="情景文本：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.echoLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_ECHO),
                                                      toolTip="控制台输出的询问文本，等待用户输入，对应参数选项里的自动输入文本（可选）")
        hbox.addWidget(self.echoLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="参数选项：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.optionValuesComboBox = WidgetUtil.createComboBox(self, activated=self.optionValueIndexChanged)
        hbox.addWidget(self.optionValuesComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Add", onClicked=self.addOptionValue))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Modify", onClicked=self.modifyOptionValue))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Del", onClicked=self.delOptionValue))
        vLayout.addLayout(hbox)

        # vLayout.addWidget(WidgetUtil.createLabel(self), 1)
        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)

        self.updateOptionValuesComboBox()
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def updateOptionValuesComboBox(self):
        if self.optionValues:
            self.optionValuesComboBox.clear()
            for index, item in enumerate(self.optionValues):
                self.optionValuesComboBox.addItem(f"{item[KEY_DESC]}", item)
            if self.curOptionValueIndex < 0:
                self.curOptionValueIndex = 0
            curOptionValueInfo = self.optionValues[self.curOptionValueIndex]
            self.optionValuesComboBox.setCurrentText(f"{curOptionValueInfo[KEY_DESC]}")
            LogUtil.d('updateOptionValuesComboBox setCurrentText', curOptionValueInfo[KEY_DESC])
        else:
            self.optionValuesComboBox.clear()
            self.curOptionValueIndex = -1
            LogUtil.d("no option value")
        pass

    def getCurOptionValueInfo(self):
        if self.curOptionValueIndex >= 0:
            return self.optionValues[self.curOptionValueIndex]
        else:
            return None

    def optionValueIndexChanged(self, index):
        LogUtil.d('optionValueIndexChanged', index)
        self.curOptionValueIndex = index
        self.default[KEY_DEFAULT] = index
        pass

    def addOptionValue(self):
        LogUtil.d("addOptionValue")
        AddOrEditOptionValueDialog(default=None, optionValues=self.optionValues,
                                   callback=self.addOrEditOptionValueCallback)
        pass

    def modifyOptionValue(self):
        LogUtil.d("modifyOptionValue")
        if self.curOptionValueIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个参数选项")
            return
        AddOrEditOptionValueDialog(default=self.optionValues[self.curOptionValueIndex],
                                   optionValues=self.optionValues,
                                   callback=self.addOrEditOptionValueCallback)
        pass

    def addOrEditOptionValueCallback(self, info):
        LogUtil.d("addOrEditOptionValueCallback", info)
        if info:
            self.optionValues.append(info)
        curOptionValueInfo = self.getCurOptionValueInfo()
        # 按项目名称重新排序
        self.optionValues = sorted(self.optionValues, key=lambda x: x[KEY_DESC])
        if curOptionValueInfo:
            for index, item in enumerate(self.optionValues):
                if curOptionValueInfo == item:
                    self.curOptionValueIndex = index
                    break
        # 更新工程下拉选择框
        self.updateOptionValuesComboBox()
        pass

    def delOptionValue(self):
        LogUtil.d("delOptionValue")
        if self.curOptionValueIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个参数选项")
            return
        optionValueInfo = self.getCurOptionValueInfo()
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{optionValueInfo[KEY_DESC]}（{optionValueInfo[KEY_VALUE]}）</span> 吗？",
            acceptFunc=self.delOptionValueItem)
        pass

    def delOptionValueItem(self):
        LogUtil.i("delOptionValueItem")
        optionValueInfo = self.getCurOptionValueInfo()
        self.optionValues.remove(optionValueInfo)
        self.curOptionValueIndex = -1
        self.updateOptionValuesComboBox()
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入需要执行的命令行指令参数别名")
            return
        if not self.optionValues:
            WidgetUtil.showErrorDialog(message="请添加参数选项列表")
            return
        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.optionList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的指令参数名，{name}已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()
        echo = self.echoLineEdit.text().strip()

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_ECHO] = echo
        self.default[KEY_DEFAULT] = self.curOptionValueIndex
        self.default[KEY_OPTION_VALUES] = self.optionValues

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


class AddOrEditOptionValueDialog(QtWidgets.QDialog):
    def __init__(self, default, optionValues, callback):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditOptionValueDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddOrEditOptionValueDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("AddOrEditOptionValueDialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑参数选项"))

        self.callback = callback
        if optionValues is None:
            optionValues = []
        self.optionValues = optionValues
        self.isAdd = default is None
        if self.isAdd:
            default = {}
        self.default = default

        self.setObjectName("AddOrEditOptionValueDialog")
        self.resize(AddOrEditOptionValueDialog.WINDOW_WIDTH, AddOrEditOptionValueDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddOrEditOptionValueDialog.WINDOW_WIDTH, AddOrEditOptionValueDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 130
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入命令参数值：", minSize=QSize(labelWidth, 20)))
        self.valueLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(self.default, KEY_VALUE),
                                                       holderText="命令参数值", isReadOnly=not self.isAdd)
        hbox.addWidget(self.valueLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入命令参数描述：", minSize=QSize(labelWidth, 20)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(self.default, KEY_DESC),
                                                      holderText="命令参数值描述，用于说明该参数值作用")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="命令参数自动输入值：", minSize=QSize(labelWidth, 20)))
        self.inputLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(self.default, KEY_INPUT),
                                                       holderText="可选，默认跟命令参数值一样",
                                                       toolTip="可选，默认跟命令参数值一样，只有在设置了使用情景参数时有效")
        hbox.addWidget(self.inputLineEdit)
        vLayout.addLayout(hbox)

        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()
        pass

    def acceptFunc(self):
        value = self.valueLineEdit.text().strip()
        if not value:
            WidgetUtil.showAboutDialog(text="请输入命令参数值")
            return
        desc = self.descLineEdit.text().strip()
        if not desc:
            WidgetUtil.showAboutDialog(text="请输入命令参数描述")
            return
        for item in self.optionValues:
            if value == item[KEY_VALUE]:
                if self.isAdd:
                    WidgetUtil.showAboutDialog(text=f"请重新添加一个其他的命令参数值，{value}已经存在了")
                    return
                elif desc == item[KEY_DESC]:
                    break
            if desc == item[KEY_DESC]:
                WidgetUtil.showErrorDialog(message=f"请设置一个其他的描述，{desc}已经存在了，相同的描述会产生混淆")
                return
        self.default[KEY_VALUE] = value
        self.default[KEY_DESC] = desc
        self.default[KEY_INPUT] = self.inputLineEdit.text().strip()

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditOptionDialog(callback=lambda it: LogUtil.d("callback", it), isDebug=True)
    window = AddOrEditOptionDialog(callback=lambda it: LogUtil.d("callback", it),
                                   default={'default': 1, 'optionValues': [
                                       {'value': 'dev', 'desc': '开发环境', 'input': '1'},
                                       {'value': 'product', 'desc': '现网环境', 'input': '0'}
                                   ], 'name': 'productFlavor', 'desc': '产品渠道信息', 'echo': '请选择你的渠道'},
                                   isDebug=True)
    window.show()
    sys.exit(app.exec_())
