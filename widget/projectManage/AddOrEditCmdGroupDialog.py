# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditCmdGroupDialog.py
# 定义一个AddOrEditCmdGroupDialog类实现添加、编辑指令分组功能
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditCmdGroupDialog"


class AddOrEditCmdGroupDialog(QtWidgets.QDialog):
    def __init__(self, cmdGroupList, callback, default=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditCmdGroupDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddOrEditCmdGroupDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.1)
        LogUtil.d(TAG, "Add or Edit Cmd Group Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑指令群组"))
        if cmdGroupList is None:
            cmdGroupList = []
        self.callback = callback
        self.cmdGroupList = cmdGroupList
        self.default = default
        self.isAdd = default is None

        self.setObjectName("AddOrEditCmdGroupDialog")
        self.setMinimumWidth(AddOrEditCmdGroupDialog.WINDOW_WIDTH)
        # self.resize(AddOrEditCmdGroupDialog.WINDOW_WIDTH, AddOrEditCmdGroupDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditCmdGroupDialog.WINDOW_WIDTH, AddOrEditCmdGroupDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 100

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="指令群组名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_NAME] if default else "",
                                                      holderText="指令分组组名，可以在模块设置指令里选择所属分组")
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="指令群组描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_DESC] if default else "",
                                                      holderText="对指令群组的描述，方便用户识别出具体的功能。")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        vLayout.addWidget(WidgetUtil.createLabel(self), 1)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.adjustSize()
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入指令群组名")
            return
        if DictUtil.get(self.default, KEY_NAME) != name:
            for item in self.cmdGroupList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的指令群组，<span style='color:red;'>{name}</span>已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()
        if not self.default:
            self.default = {}

        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditCmdGroupDialog(cmdGroupList=[], callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
