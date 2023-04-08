# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditMatchDialog.py
# 定义一个AddOrEditMatchDialog类实现添加、编辑环境变量功能
import sys

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from widget.findFileContent.FindFileContentManager import *

TAG = "AddOrEditMatchDialog"


class AddOrEditMatchDialog(QtWidgets.QDialog):
    def __init__(self, default=None, matchList=None, callback=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditMatchDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AddOrEditMatchDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "AddOrEditMatchDialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑内容匹配规则"))
        if matchList is None:
            matchList = []
        self.callback = callback
        self.matchList = matchList
        self.default = default if default else {}
        self.isAdd = default is None

        self.setObjectName("AddOrEditMatchDialog")
        self.resize(AddOrEditMatchDialog.WINDOW_WIDTH, AddOrEditMatchDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditMatchDialog.WINDOW_WIDTH, AddOrEditMatchDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 100

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="匹配规则名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME, ""),
                                                      holderText="查找内容时匹配规则名")
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="匹配规则描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC, ""),
                                                      holderText="查找内容时匹配规则描述")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="匹配规则：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.patternLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_PATTERN, ""),
                                                         holderText="查找内容时匹配规则，可以是正则表达式，也可以是普通文本。")
        hbox.addWidget(self.patternLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.isRegRadioButton = WidgetUtil.createRadioButton(self, text="正则规则", toolTip="勾选会按正则规则匹配",
                                                             autoExclusive=False,
                                                             isChecked=DictUtil.get(default, KEY_IS_REG, DEFAULT_VALUE_IS_REG))
        hbox.addWidget(self.isRegRadioButton)
        vLayout.addLayout(hbox)

        vLayout.addWidget(WidgetUtil.createLabel(self), 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入匹配规则名")
            return
        if self.isAdd or DictUtil.get(self.default, KEY_NAME) != name:
            for item in self.matchList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的匹配规则名，{name}已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()
        pattern = self.patternLineEdit.text().strip()
        isReg = self.isRegRadioButton.isChecked()
        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_PATTERN] = pattern
        self.default[KEY_IS_REG] = isReg

        if self.callback:
            self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditMatchDialog(default=None,
                                  matchList=[], callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    # window = AddOrEditMatchDialog(default={'name': '11', 'desc': '33', 'pattern': '44', 'isReg': True},
    #                               matchList=[], callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
