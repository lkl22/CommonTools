# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditProjectDialog.py
# 定义一个AddOrEditProjectDialog类实现添加、编辑项目配置功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView
import copy
from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.MD5Util import MD5Util
from util.OperaIni import *
from widget.custom.DragInputWidget import DragInputWidget
from widget.projectManage.AddOrEditEvnDialog import AddOrEditEvnDialog
from widget.projectManage.ProjectManager import *


class AddOrEditProjectDialog(QtWidgets.QDialog):
    def __init__(self, callback, projectInfo=None, projectList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.isDebug = isDebug
        self.callback = callback
        if projectList is None:
            projectList = []
        self.projectList = projectList
        self.isAdd = projectInfo is None
        if projectInfo is None:
            projectInfo = {KEY_EVN_LIST: []}
        elif KEY_EVN_LIST not in projectInfo:
            projectInfo[KEY_EVN_LIST] = []
        self.projectInfo = projectInfo
        self.evnList = copy.deepcopy(projectInfo[KEY_EVN_LIST])

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
        hbox.addWidget(WidgetUtil.createLabel(box, text="工程名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectNameLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.projectInfo, KEY_NAME),
                                                             isReadOnly=not self.isAdd)
        hbox.addWidget(self.projectNameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="工程描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectDescLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.projectInfo, KEY_DESC))
        hbox.addWidget(self.projectDescLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="工程路径：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.projectPathInputWidget = DragInputWidget(
            text=DictUtil.get(self.projectInfo, KEY_PATH),
            dirParam=["请选择您工程工作目录", "./"], isReadOnly=True,
            holderText="请拖动您工程的工作目录到此框或者点击右侧的按钮选择您的工程路径")
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
        self.updateEvnTableView()
        vbox.addWidget(self.evnTableView)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def addEvn(self):
        LogUtil.d("addEvn")
        AddOrEditEvnDialog(evnList=self.evnList, callback=self.addOrEditEvnCallback)
        pass

    def addOrEditEvnCallback(self, info):
        LogUtil.d("addOrEditEvnCallback", info)
        if info:
            self.evnList.append(info)
        self.evnList = sorted(self.evnList, key=lambda x: x[KEY_NAME])
        self.updateEvnTableView()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d("双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditEvnDialog(evnList=self.evnList, callback=self.addOrEditEvnCallback,
                           default=self.evnList[row])
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.evnTableView.currentIndex().row()
        LogUtil.i("customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delProjectEvn)
        menu.exec(self.evnTableView.mapToGlobal(pos))
        pass

    def delProjectEvn(self):
        evn = self.evnList[self.curDelRow][KEY_NAME]
        LogUtil.i(f"delAccount {evn}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{evn}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i("delTreeWidgetItem")
        self.evnList.remove(self.evnList[self.curDelRow])
        self.updateEvnTableView()
        pass

    def updateEvnTableView(self):
        tableData = []
        for evn in self.evnList:
            tableData.append({
                KEY_NAME: evn[KEY_NAME],
                KEY_VALUE: evn[KEY_VALUE],
                KEY_DESC: evn[KEY_DESC],
                KEY_EVN_IS_PATH: "Path环境变量" if evn[KEY_EVN_IS_PATH] else "普通环境变量"
            })
        WidgetUtil.addTableViewData(self.evnTableView, tableData,
                                    headerLabels=["环境变量名", "环境变量值", "环境变量描述", "Path环境变量"])
        if len(self.evnList) > 0:
            WidgetUtil.tableViewSetColumnWidth(self.evnTableView, 0, 100)
        pass

    def acceptFunc(self):
        LogUtil.d("acceptFunc")
        name = self.projectNameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入工程名")
            return
        desc = self.projectDescLineEdit.text().strip()
        if not desc:
            WidgetUtil.showErrorDialog(message="请输入工程描述")
            return
        path = self.projectPathInputWidget.text().strip()
        if not path:
            WidgetUtil.showErrorDialog(message="请选择工程路径")
            return

        if self.isAdd:
            for item in self.projectList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的工程名，{name}已经存在了，可以下拉选择")
                    return

        id = MD5Util.md5(name)
        if self.projectInfo is None:
            self.projectInfo = {}
        self.projectInfo[KEY_ID] = id
        self.projectInfo[KEY_NAME] = name
        self.projectInfo[KEY_DESC] = desc
        self.projectInfo[KEY_PATH] = path
        self.projectInfo[KEY_EVN_LIST] = self.evnList

        self.callback(self.projectInfo if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditProjectDialog(callback=lambda it: LogUtil.d("callback", it), isDebug=True)
    # window = AddOrEditProjectDialog(callback=lambda it: LogUtil.d("callback", it),
    #                                 projectInfo={'evnList': [
    #                                     {'name': 'ss', 'value': 'dd', 'desc': 'ff', "isPath": True}],
    #                                              'id': '0cc175b9c0f1b6a831c399e269772661',
    #                                              'name': 'a', 'desc': 'dd',
    #                                              'path': '/Users/likunlun/PycharmProjects/CommonTools/widget/projectManage'},
    #                                 isDebug=True)
    window.show()
    sys.exit(app.exec_())
