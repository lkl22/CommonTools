# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditEvnDialog.py
# 定义一个AddOrEditEvnDialog类实现添加、编辑环境变量功能
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditEvnDialog"


class AddOrEditEvnDialog(QtWidgets.QDialog):
    def __init__(self, evnList, callback, default=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditEvnDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AddOrEditEvnDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Evn Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑环境变量"))
        if evnList is None:
            evnList = []
        self.callback = callback
        self.evnList = evnList
        self.default = default

        self.setObjectName("AddOrEditEvnDialog")
        self.resize(AddOrEditEvnDialog.WINDOW_WIDTH, AddOrEditEvnDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditEvnDialog.WINDOW_WIDTH, AddOrEditEvnDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 100

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="环境变量名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_NAME] if default else "",
                                                      holderText="工程运行时的环境变量名")
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="环境变量值：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.valueLineEdit = DragInputWidget(text=default[KEY_VALUE] if default else "",
                                             fileParam=['', './', '', ''],
                                             dirParam=["", "./"],
                                             isReadOnly=False,
                                             holderText="工程运行时的环境变量值",
                                             toolTip="您可以拖动文件或者文件夹到此")
        hbox.addWidget(self.valueLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="环境变量描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=default[KEY_DESC] if default else "",
                                                      holderText="工程运行时的环境变量描述")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.isPathRadioButton = WidgetUtil.createRadioButton(self, text="Path环境变量", toolTip="勾选会加入到path环境变量",
                                                              autoExclusive=False,
                                                              isChecked=default[KEY_EVN_IS_PATH] if default else False)
        hbox.addWidget(self.isPathRadioButton)
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
            WidgetUtil.showErrorDialog(message="请输入环境变量名")
            return
        value = self.valueLineEdit.text().strip()
        if not value:
            WidgetUtil.showErrorDialog(message="请输入环境变量值")
            return
        if not self.default or self.default[KEY_NAME] != name:
            for item in self.evnList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的环境变量，{name}已经存在了，不能重复添加")
                    return
        desc = self.descLineEdit.text().strip()
        isPath = self.isPathRadioButton.isChecked()
        if self.default:
            self.default[KEY_NAME] = name
            self.default[KEY_VALUE] = value
            self.default[KEY_DESC] = desc
            self.default[KEY_EVN_IS_PATH] = isPath
            self.callback(None)
        else:
            self.callback({KEY_NAME: name, KEY_VALUE: value, KEY_DESC: desc, KEY_EVN_IS_PATH: isPath})
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditEvnDialog(evnList=[], callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
