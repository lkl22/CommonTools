# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditDynamicParamDialog.py
# 定义一个AddOrEditDynamicParamDialog类实现添加、编辑动态参数功能
import copy

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditDynamicParamDialog"


class AddOrEditDynamicParamDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, paramList=None, isDebug=False):
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
        if paramList is None:
            paramList = []
        self.paramList = paramList
        self.callback = callback
        self.isAdd = default is None
        if not default:
            default = {KEY_DEFAULT: -1, KEY_OPTION_VALUES: []}
        self.default = default

        self.setObjectName("AddOrEditDynamicParamDialog")
        self.resize(AddOrEditDynamicParamDialog.WINDOW_WIDTH, AddOrEditDynamicParamDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditDynamicParamDialog.WINDOW_WIDTH, AddOrEditDynamicParamDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 90

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Name：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      toolTip="动态参数名称")
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Description：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      toolTip="动态参数描述")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="选项所属群组：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.optionValuesComboBox = WidgetUtil.createComboBox(self, activated=self.optionGroupChanged)
        hbox.addWidget(self.optionValuesComboBox, 1)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.capitalizeCheckBox = WidgetUtil.createCheckBox(self, text="首字母是否大写",
                                                            toolTip="默认首字母大写，会在拼接时将首字母转为大写。",
                                                            isChecked=DictUtil.get(self.default, KEY_NEED_CAPITALIZE,
                                                                                   DEFAULT_VALUE_NEED_CAPITALIZE))
        hbox.addWidget(self.capitalizeCheckBox)
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

    def optionGroupChanged(self):
        pass

    def updateOptionValuesComboBox(self):
        # if self.optionValues:
        #     self.optionValuesComboBox.clear()
        #     for index, item in enumerate(self.optionValues):
        #         self.optionValuesComboBox.addItem(f"{item[KEY_DESC]}", item)
        #     if self.curOptionValueIndex < 0:
        #         self.curOptionValueIndex = 0
        #     curOptionValueInfo = self.optionValues[self.curOptionValueIndex]
        #     self.optionValuesComboBox.setCurrentText(f"{curOptionValueInfo[KEY_DESC]}")
        #     LogUtil.d(TAG, 'updateOptionValuesComboBox setCurrentText', curOptionValueInfo[KEY_DESC])
        # else:
        #     self.optionValuesComboBox.clear()
        #     self.curOptionValueIndex = -1
        #     LogUtil.d(TAG, "no option value")
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入动态参数名")
            return
        if not self.optionValues:
            WidgetUtil.showErrorDialog(message="请添加动态参数列表")
            return
        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.paramList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的动态参数名，{name}已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_NEED_CAPITALIZE] = self.capitalizeCheckBox.isChecked()
        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditDynamicParamDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window = AddOrEditDynamicParamDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                         default={KEY_OPTION_GROUP: "", KEY_OPTION: "", KEY_NAME: 'productFlavor',
                                                  KEY_DESC: '产品渠道信息'},
                                         isDebug=True)
    window.show()
    sys.exit(app.exec_())
