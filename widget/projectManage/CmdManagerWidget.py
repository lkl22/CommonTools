# -*- coding: utf-8 -*-
# python 3.x
# Filename: CmdManagerWidget.py
# 定义一个CmdManagerWidget窗口类实现执行指令管理的功能，可以控制一系列指令是否需要执行
import sys
from PyQt5.QtWidgets import QScrollArea, QFrame
from util.WidgetUtil import *
from widget.projectManage.AddOrEditCmdGroupDialog import AddOrEditCmdGroupDialog
from widget.projectManage.ProjectManager import *


class CmdManagerWidget(QFrame):
    def __init__(self, projectManager: ProjectManager, getOptionGroupsFunc=None):
        super(CmdManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.getOptionGroupsFunc = getOptionGroupsFunc
        self.projectInfo = None
        self.cmdGroups = {}
        self.cmdGroupWidgets: [CmdGroupWidget] = []

        self.setObjectName("CmdManagerWidget")
        self.setToolTip("支持模块指令分组，通过分组控制指令是否需要执行。不在分组里的指令是都会执行的，在分组里的根据用户的选择来控制是否执行。")
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=0)
        hbox.addWidget(WidgetUtil.createLabel(self, text="指令管理"))
        self.addModuleBtn = WidgetUtil.createPushButton(self, text="Add", toolTip="添加新的指令分组配置", isEnable=False,
                                                        onClicked=self.addCmdGroup)
        hbox.addWidget(self.addModuleBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        box = WidgetUtil.createGroupBox(self, title="")
        vbox.addWidget(box, 1)

        groupBoxlayout = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0))
        scrollAres = QScrollArea(self)
        scrollAres.setWidgetResizable(True)
        scrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        scrollAres.setWidget(scrollAreaWidget)
        groupBoxlayout.addWidget(scrollAres, 1)

        # 进行垂直布局
        self.vLayout = WidgetUtil.createVBoxLayout(scrollAreaWidget, margins=QMargins(5, 5, 5, 5))
        self.spacerItem = WidgetUtil.createVSpacerItem(1, 1)
        self.vLayout.addItem(self.spacerItem)

        # self.setStyleSheet("CmdManagerWidget{border:1px solid rgb(0,0,255)}")
        pass

    def setProjectInfo(self, projectInfo):
        LogUtil.d("setProjectInfo", projectInfo)
        self.projectInfo = projectInfo
        projectId = DictUtil.get(projectInfo, KEY_ID)
        self.addModuleBtn.setEnabled(projectId is not None)
        self.cmdGroups = self.projectManager.getProjectCmdGroups(projectId) if projectId else []
        self.updateCmdGroupList()
        pass

    def getProjectPath(self):
        return DictUtil.get(self.projectInfo, KEY_PATH)

    def getSelectedCmdGroups(self):
        res = []
        for item in self.cmdGroupWidgets:
            if item.isChecked():
                res.append(item.getInfo())
        return res

    def addCmdGroup(self):
        LogUtil.d("addCmdGroup")
        AddOrEditCmdGroupDialog(cmdGroupList=DictUtil.get(self.cmdGroups, KEY_LIST, []), callback=self.addOrEditCmdGroupCallback)
        pass

    def editCmdGroup(self, cmdGroup):
        LogUtil.d("editCmdGroup", cmdGroup)
        AddOrEditCmdGroupDialog(cmdGroupList=DictUtil.get(self.cmdGroups, KEY_LIST, []), callback=self.addOrEditCmdGroupCallback, default=cmdGroup)
        pass

    def addOrEditCmdGroupCallback(self, info):
        LogUtil.d("addOrEditCmdGroupCallback", info)
        cmdGroupList = DictUtil.get(self.cmdGroups, KEY_LIST, [])
        if info:
            cmdGroupList.append(info)
        self.cmdGroups[KEY_LIST] = sorted(cmdGroupList, key=lambda x: x[KEY_NAME])
        self.updateCmdGroupList()
        self.saveProjectCmdGroups()
        pass

    def delCmdGroup(self, widget, info):
        LogUtil.d("delCmdGroup", info)
        cmdGroupList = DictUtil.get(self.cmdGroups, KEY_LIST, [])
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{info[KEY_NAME]}（{info[KEY_DESC]}）</span> 吗？",
            acceptFunc=lambda: (
                self.vLayout.removeWidget(widget),
                widget.deleteLater(),
                self.cmdGroupWidgets.remove(widget),
                cmdGroupList.remove(info),
                self.cmdGroups[KEY_DEFAULT].remove(info[KEY_NAME]),
                self.saveProjectCmdGroups()
            ))
        pass

    def saveProjectCmdGroups(self):
        self.projectManager.saveProjectCmdGroups(DictUtil.get(self.projectInfo, KEY_ID), self.cmdGroups)
        pass

    def getProjectCmdGroupList(self):
        return DictUtil.get(self.cmdGroups, KEY_LIST, [])

    def getProjectCmdGroupInfo(self):
        info = {KEY_DEFAULT: DictUtil.get(self.cmdGroups, KEY_DEFAULT, []), KEY_LIST: []}
        cmdGroups = DictUtil.get(self.cmdGroups, KEY_LIST, [])
        for item in cmdGroups:
            info[KEY_LIST].append(item[KEY_NAME])
        return info

    def updateCmdGroupItem(self, index, info):
        LogUtil.d("updateCmdGroupItem", index, info)
        if index >= len(self.cmdGroupWidgets):
            moduleWidget = CmdGroupWidget(info=info, defaultSelected=DictUtil.get(self.cmdGroups, KEY_DEFAULT),
                                          editFunc=self.editCmdGroup, delFunc=self.delCmdGroup,
                                          selectedChanged=self.saveProjectCmdGroups)
            self.cmdGroupWidgets.append(moduleWidget)
            self.vLayout.addWidget(moduleWidget)
        else:
            self.cmdGroupWidgets[index].updateUi(info, DictUtil.get(self.cmdGroups, KEY_DEFAULT))
        pass

    def updateCmdGroupList(self):
        LogUtil.d("updateCmdGroupList")
        cmdGroupList = DictUtil.get(self.cmdGroups, KEY_LIST, [])
        cmdGroupLen = len(cmdGroupList)
        while cmdGroupLen < len(self.cmdGroupWidgets):
            widget = self.cmdGroupWidgets[cmdGroupLen]
            self.vLayout.removeWidget(widget)
            widget.deleteLater()
            self.cmdGroupWidgets.remove(widget)
        self.vLayout.removeItem(self.spacerItem)
        for index, item in enumerate(cmdGroupList):
            self.updateCmdGroupItem(index, item)
        self.vLayout.addItem(self.spacerItem)
        pass


class CmdGroupWidget(QWidget):
    def __init__(self, info, defaultSelected, editFunc, delFunc, selectedChanged):
        super(CmdGroupWidget, self).__init__()
        self.info = info
        self.defaultSelected = defaultSelected
        self.selectedChanged = selectedChanged

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(0, 0, 0, 0))
        self.checkBox = WidgetUtil.createCheckBox(self, clicked=self.cmdGroupSelectedChange)
        hbox.addWidget(self.checkBox)
        # 为窗口添加QActions
        self.addAction(WidgetUtil.createAction(self, text="编辑", func=lambda: editFunc(self.info)))
        self.addAction(WidgetUtil.createAction(self, text="删除", func=lambda: delFunc(self, self.info)))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setStyleSheet("QWidget:hover{background-color:rgb(0,255,255)}")

        self.updateUi(info, defaultSelected)
        pass

    def updateUi(self, info, defaultSelected):
        LogUtil.d("CmdGroupWidget updateUi", info, defaultSelected)
        self.info = info
        self.defaultSelected = defaultSelected
        self.checkBox.setText(info[KEY_NAME])
        self.checkBox.setToolTip(info[KEY_DESC])
        self.checkBox.setChecked(info[KEY_NAME] in defaultSelected)
        pass

    def cmdGroupSelectedChange(self):
        name = DictUtil.get(self.info, KEY_NAME)
        if self.isChecked():
            self.defaultSelected.append(name)
        else:
            self.defaultSelected.remove(name)
        LogUtil.d("cmdGroupSelectedChange", self.defaultSelected)
        self.selectedChanged()
        pass

    def getInfo(self):
        return self.info

    def isChecked(self):
        return self.checkBox.isChecked()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CmdManagerWidget()
    e.show()
    sys.exit(app.exec_())
