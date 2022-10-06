# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditCmdDialog.py
# 定义一个AddOrEditCmdDialog类实现添加、编辑执行指令功能
from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.ProjectManager import *


class AddOrEditCmdDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, cmdList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.WindowStaysOnTopHint)
        AddOrEditCmdDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditCmdDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d("Add or Edit Cmd Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑执行指令"))
        if cmdList is None:
            cmdList = []
        self.cmdList = cmdList
        self.callback = callback
        self.default = default
        self.isAdd = default is None

        self.setObjectName("AddOrEditCmdDialog")
        self.resize(AddOrEditCmdDialog.WINDOW_WIDTH, AddOrEditCmdDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditCmdDialog.WINDOW_WIDTH, AddOrEditCmdDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 120

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
        hbox.addWidget(WidgetUtil.createLabel(self, text="Program：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.programInputWidget = DragInputWidget(text=DictUtil.get(default, KEY_PROGRAM),
                                                  fileParam=['', './', '', ''],
                                                  dirParam=["", "./"],
                                                  isReadOnly=False,
                                                  holderText="需要执行的命令行指令",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.programInputWidget)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Working directory：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.workDirInputWidget = DragInputWidget(text=DictUtil.get(default, KEY_WORKING_DIR),
                                                  fileParam=['', './', '', ''],
                                                  dirParam=["", "./"],
                                                  isReadOnly=False,
                                                  holderText="执行命令行指令所在的工作空间，不填，默认跟随模块工作目录",
                                                  toolTip="您可以拖动文件或者文件夹到此或者点击右侧的图标")
        hbox.addWidget(self.workDirInputWidget)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="Arguments：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.argumentsLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_ARGUMENTS),
                                                           holderText="需要执行的命令行指令参数，多个参数使用空格分隔")
        hbox.addWidget(self.argumentsLineEdit)
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
            WidgetUtil.showErrorDialog(message="请输入需要执行的命令行指令别名")
            return
        program = self.programInputWidget.text().strip()
        if not program:
            WidgetUtil.showErrorDialog(message="请输入需要执行的命令行指令")
            return
        if not self.default or self.default[KEY_NAME] != name:
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
        self.default[KEY_ARGUMENTS] = arguments

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d("callback", it), isDebug=True)
    window = AddOrEditCmdDialog(callback=lambda it: LogUtil.d("callback", it),
                                default={'name': 'ls操作', 'desc': 'ls -l', 'program': 'ls', 'workingDir': './', 'arguments': '-l'},
                                isDebug=True)
    window.show()
    sys.exit(app.exec_())
