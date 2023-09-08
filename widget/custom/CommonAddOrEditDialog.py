# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonAddOrEditDialog.py
# 定义一个CommonAddOrEditDialog类实现添加、编辑相关数据相关的功能
import sys

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.ICommonWidget import ICommonWidget

TAG = "CommonAddOrEditDialog"

KEY_ITEM_KEY = 'key'
KEY_ITEM_LABEL = 'label'
KEY_ITEM_TYPE = 'type'
KEY_IS_UNIQUE = 'isUnique'
KEY_IS_OPTIONAL = 'isOptional'
KEY_TOOLTIP = 'toolTip'

TYPE_LINE_EDIT = 'lineEdit'
TYPE_SELECT_FILE = 'selectFile'
TYPE_SELECT_DIR = 'selectDir'


class CommonAddOrEditDialog(QtWidgets.QDialog):
    def __init__(self, windowTitle: str, optionInfos: [{}], default=None, items: [] = None, callback=None, width=0.7,
                 height=0.2,
                 isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        CommonAddOrEditDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * width)
        CommonAddOrEditDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * height)
        LogUtil.d(TAG, "CommonAddOrEditDialog")
        self.setWindowTitle(WidgetUtil.translate(text=windowTitle))
        self.setObjectName("CommonAddOrEditDialog")
        self.resize(CommonAddOrEditDialog.WINDOW_WIDTH, CommonAddOrEditDialog.WINDOW_HEIGHT)
        # self.setFixedSize(CommonAddOrEditDialog.WINDOW_WIDTH, CommonAddOrEditDialog.WINDOW_HEIGHT)

        self.__default = default if default else {}
        self.__items = items if items else []
        self.__callback = callback
        self.__isAdd = default is None

        self.__optionInfos = optionInfos
        self.__widgets: [ICommonWidget] = []

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 100
        for optionInfo in optionInfos:
            itemType = DictUtil.get(optionInfo, KEY_ITEM_TYPE)
            if itemType == TYPE_LINE_EDIT:
                widget = CommonLineEdit(label=DictUtil.get(optionInfo, KEY_ITEM_LABEL),
                                        text=DictUtil.get(self.__default, optionInfo[KEY_ITEM_KEY], ''),
                                        labelMinSize=QSize(labelWidth, 0),
                                        toolTip=DictUtil.get(optionInfo, KEY_TOOLTIP))
            else:
                LogUtil.e(TAG, f'{itemType} not support.')
                return
            vLayout.addWidget(widget)
            self.__widgets.append(widget)

        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        for index, optionInfo in enumerate(self.__optionInfos):
            if not DictUtil.get(optionInfo, KEY_IS_OPTIONAL, True):
                if not self.__widgets[index].getData():
                    WidgetUtil.showErrorDialog(
                        message=DictUtil.get(optionInfo, KEY_TOOLTIP, f'{optionInfo[KEY_ITEM_LABEL]}必须设置值'))
                    return
            self.__default[optionInfo[KEY_ITEM_KEY]] = self.__widgets[index].getData()
        # name = self.nameLineEdit.text().strip()
        # if not name:
        #     WidgetUtil.showErrorDialog(message="请输入匹配规则名")
        #     return
        # if self.isAdd or DictUtil.get(self.default, KEY_NAME) != name:
        #     for item in self.items:
        #         if name == item[KEY_NAME]:
        #             WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的匹配规则名，{name}已经存在了，不能重复添加")
        #             return

        if self.__callback:
            self.__callback(self.__default if self.__isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CommonAddOrEditDialog(windowTitle='添加/编辑规则',
                                   optionInfos=[{
                                       KEY_ITEM_KEY: 'name',
                                       KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                       KEY_ITEM_LABEL: '规则名：',
                                       KEY_IS_OPTIONAL: True,
                                       KEY_TOOLTIP: '请输入规则名'
                                   },
                                   #     {
                                   #     KEY_ITEM_KEY: 'srcFile',
                                   #     KEY_ITEM_TYPE: TYPE_SELECT_FILE,
                                   #     KEY_ITEM_LABEL: '请选则源文件：'
                                   # }
                                   ],
                                   callback=lambda it: LogUtil.d(TAG, "callback", it),
                                   isDebug=True)
    window.show()
    sys.exit(app.exec_())
