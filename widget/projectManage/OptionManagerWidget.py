# -*- coding: utf-8 -*-
# python 3.x
# Filename: OptionManagerWidget.py
# 定义一个OptionManagerWidget窗口类实现执行构建选项管理的功能
import sys
from PyQt5.QtWidgets import QScrollArea, QFrame
from util.WidgetUtil import *
from widget.projectManage.AddOrEditOptionGroupDialog import AddOrEditOptionGroupDialog
from widget.projectManage.ProjectManager import *


class OptionManagerWidget(QFrame):
    def __init__(self, projectManager: ProjectManager):
        super(OptionManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.projectInfo = None
        self.optionGroups = []
        self.optionGroupWidgets: [OptionGroupWidget] = []

        self.setObjectName("OptionManagerWidget")
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        vbox.addWidget(WidgetUtil.createLabel(self, text="指令参数管理"))

        hbox = WidgetUtil.createHBoxLayout(spacing=5)
        self.addOptionGroupBtn = WidgetUtil.createPushButton(self, text="Add", toolTip="添加新的模块", isEnable=False,
                                                             onClicked=self.addOptionGroup)
        hbox.addWidget(self.addOptionGroupBtn)
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
        self.vLayout = WidgetUtil.createVBoxLayout(scrollAreaWidget)
        self.spacerItem = WidgetUtil.createVSpacerItem(1, 1)
        self.vLayout.addItem(self.spacerItem)
        self.setStyleSheet("OptionManagerWidget{border:1px solid rgb(0,255,0)}")
        pass

    def setProjectInfo(self, projectInfo):
        LogUtil.d("setProjectInfo", projectInfo)
        self.projectInfo = projectInfo
        projectId = DictUtil.get(projectInfo, KEY_ID)
        self.addOptionGroupBtn.setEnabled(projectId is not None)
        self.optionGroups = self.projectManager.getProjectOptionGroups(projectId) if projectId else []
        self.updateOptionGroupList()
        pass

    def addOptionGroup(self):
        LogUtil.d("addOptionGroup")
        AddOrEditOptionGroupDialog(callback=self.addOrEditOptionGroupCallback, groupList=self.optionGroups)
        pass

    def editOptionGroup(self, optionGroupInfo):
        LogUtil.d("editOptionGroup", optionGroupInfo)
        AddOrEditOptionGroupDialog(callback=self.addOrEditOptionGroupCallback, default=optionGroupInfo, groupList=self.optionGroups)
        pass

    def addOrEditOptionGroupCallback(self, info):
        LogUtil.d("addOrEditOptionGroupCallback", info)
        if info:
            self.optionGroups.append(info)
        self.optionGroups = sorted(self.optionGroups, key=lambda x: x[KEY_NAME])
        self.updateOptionGroupList()
        self.projectManager.saveProjectOptionGroups(DictUtil.get(self.projectInfo, KEY_ID), self.optionGroups)
        pass

    def delOptionGroup(self, optionGroupWidget, optionGroupInfo):
        LogUtil.d("delOptionGroup", optionGroupInfo)
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{optionGroupInfo[KEY_NAME]}（{optionGroupInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=lambda: (
                self.vLayout.removeWidget(optionGroupWidget),
                optionGroupWidget.deleteLater(),
                self.optionGroupWidgets.remove(optionGroupWidget),
                self.optionGroups.remove(optionGroupInfo),
                self.projectManager.saveProjectOptionGroups(DictUtil.get(self.projectInfo, KEY_ID), self.optionGroups)
            ))
        pass

    def updateOptionGroupItem(self, index, optionGroupInfo):
        LogUtil.d("updateOptionGroupItem", index, optionGroupInfo)
        if index >= len(self.optionGroupWidgets):
            widget = OptionGroupWidget(info=optionGroupInfo, editFunc=self.editOptionGroup, delFunc=self.delOptionGroup)
            self.optionGroupWidgets.append(widget)
            self.vLayout.addWidget(widget)
        else:
            self.optionGroupWidgets[index].updateUi(optionGroupInfo)
        pass

    def updateOptionGroupList(self):
        LogUtil.d("updateModuleList")
        moduleLen = len(self.optionGroups)
        while moduleLen < len(self.optionGroupWidgets):
            widget = self.optionGroupWidgets[moduleLen]
            self.vLayout.removeWidget(widget)
            widget.deleteLater()
            self.optionGroupWidgets.remove(widget)
        self.vLayout.removeItem(self.spacerItem)
        for index, item in enumerate(self.optionGroups):
            self.updateOptionGroupItem(index, item)
        self.vLayout.addItem(self.spacerItem)
        pass


class OptionGroupWidget(QWidget):
    def __init__(self, info, editFunc, delFunc):
        super(OptionGroupWidget, self).__init__()
        self.info = info

        hbox = WidgetUtil.createHBoxLayout(self)
        self.checkBox = WidgetUtil.createCheckBox(self, text=info[KEY_NAME], toolTip=info[KEY_DESC])
        hbox.addWidget(self.checkBox)
        # 为窗口添加QActions
        self.addAction(WidgetUtil.createAction(self, text="编辑", func=lambda: editFunc(self.info)))
        self.addAction(WidgetUtil.createAction(self, text="删除", func=lambda: delFunc(self, self.info)))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setStyleSheet("QWidget:hover{background-color:rgb(0,255,255)}")
        pass

    def updateUi(self, moduleInfo):
        self.info = moduleInfo
        self.checkBox.setText(moduleInfo[KEY_NAME])
        self.checkBox.setToolTip(moduleInfo[KEY_DESC])
        self.checkBox.setChecked(False)
        pass

    def getOptionGroupInfo(self):
        return self.info

    def isChecked(self):
        return self.checkBox.isChecked()
