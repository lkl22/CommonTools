# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditProjectDialog.py
# 定义一个AddOrEditProjectDialog类实现添加、编辑项目配置功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.AddOrEditEvnDialog import AddOrEditEvnDialog
from widget.projectManage.ProjectManager import *


class AddOrEditProjectDialog(QtWidgets.QDialog):
    def __init__(self, projectInfo=None, projectList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.isDebug = isDebug
        if projectList is None:
            projectList = []
        self.projectInfo = projectInfo
        self.projectList = projectList

        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditProjectDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditProjectDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d("Add Or Edit Project Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/修改项目配置"))
        self.setObjectName("AddOrEditProjectDialog")
        self.resize(AddOrEditProjectDialog.WINDOW_WIDTH, AddOrEditProjectDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.projectConfigGroupBox = self.createProjectConfigGroupBox(self)
        vLayout.addWidget(self.projectConfigGroupBox)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createProjectConfigGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        labelWidth = 120
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="项目名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectNameLineEdit = WidgetUtil.createLineEdit(box, text=self.projectInfo[
            KEY_PROJECT_NAME] if self.projectInfo else "",
                                                             isReadOnly=self.projectInfo is not None)
        hbox.addWidget(self.projectNameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="项目描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectDescLineEdit = WidgetUtil.createLineEdit(box, text=self.projectInfo[
            KEY_DESC] if self.projectInfo else "",
                                                             isReadOnly=self.projectInfo is not None)
        hbox.addWidget(self.projectDescLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="项目路径：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectPathInputWidget = DragInputWidget(dirParam=["请选择您工程工作目录", "./"], isReadOnly=True,
                                                      holderText="请拖动您工程的工作目录到此框或者双击选择您的工程路径",
                                                      textChanged=self.dragInputTextChanged)
        hbox.addWidget(self.projectPathInputWidget)
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createPushButton(box, text="添加工程环境变量", onClicked=self.addEvn))
        self.evnTableView = WidgetUtil.createTableView(box, doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.evnTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.evnTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.evnTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.evnTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.evnTableView.customContextMenuRequested.connect(self.customRightMenu)
        vbox.addWidget(self.evnTableView)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def dragInputTextChanged(self):
        LogUtil.d("dragInputTextChanged")
        pass

    def addEvn(self):
        LogUtil.d("addEvn")
        if self.projectInfo is None:
            self.projectInfo = {KEY_PROJECT_ENV_LIST: []}
        evnList = DictUtil.get(self.projectInfo, KEY_PROJECT_ENV_LIST)
        AddOrEditEvnDialog(evnList=evnList, callback=self.addOrEditEvnCallback,
                           isDebug=self.isDebug)
        pass

    def addOrEditEvnCallback(self, evnInfo):
        LogUtil.d("addOrEditEvnCallback", evnInfo)
        evnList = self.projectInfo[KEY_PROJECT_ENV_LIST]
        if evnInfo:
            evnList.append(evnInfo)
        self.projectInfo[KEY_PROJECT_ENV_LIST] = sorted(evnList, key=lambda x: x[KEY_EVN_NAME])
        self.updateEvnTableView()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d("双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)

        evnInfo = self.projectInfo[KEY_PROJECT_ENV_LIST][row]
        AddOrEditEvnDialog(evnList=self.projectInfo[KEY_PROJECT_ENV_LIST], callback=self.addOrEditEvnCallback,
                           default=evnInfo,
                           isDebug=self.isDebug).show()
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.evnTableView.currentIndex().row()
        LogUtil.i("customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delProjectEvn)
        menu.exec(self.evnTableView.mapToGlobal(pos))
        pass

    def delProjectEvn(self):
        evn = self.projectInfo[KEY_PROJECT_ENV_LIST][self.curDelRow][KEY_EVN_NAME]
        LogUtil.i(f"delAccount {evn}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{evn}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i("delTreeWidgetItem")
        self.projectInfo[KEY_PROJECT_ENV_LIST].remove(self.projectInfo[KEY_PROJECT_ENV_LIST][self.curDelRow])
        self.updateEvnTableView()
        pass

    def updateEvnTableView(self):
        if not self.projectInfo or not self.projectInfo[KEY_PROJECT_ENV_LIST]:
            evnList = []
        else:
            evnList = self.projectInfo[KEY_PROJECT_ENV_LIST]
        WidgetUtil.addTableViewData(self.evnTableView, evnList,
                                    headerLabels=["环境变量名", "环境变量值", "环境变量描述"])
        WidgetUtil.tableViewSetColumnWidth(self.evnTableView, 0, 150)
        WidgetUtil.tableViewSetColumnWidth(self.evnTableView, 2, 150)
        pass

    def acceptFunc(self):
        LogUtil.d("acceptFunc")
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditProjectDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
