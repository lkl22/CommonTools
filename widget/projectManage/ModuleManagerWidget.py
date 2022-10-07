# -*- coding: utf-8 -*-
# python 3.x
# Filename: ModuleManagerWidget.py
# 定义一个ModuleManagerWidget窗口类实现模块管理的功能
import sys
from PyQt5.QtWidgets import QScrollArea, QFrame
from util.WidgetUtil import *
from widget.projectManage.AddOrEditModuleDialog import AddOrEditModuleDialog
from widget.projectManage.ProjectManager import *


class ModuleManagerWidget(QFrame):
    def __init__(self, projectManager: ProjectManager, getOptionGroupsFunc=None):
        super(ModuleManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.getOptionGroupsFunc = getOptionGroupsFunc
        self.projectInfo = None
        self.modules = []
        self.moduleWidgets: [ModuleWidget] = []

        self.setObjectName("ModuleManagerWidget")
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))
        vbox.addWidget(WidgetUtil.createLabel(self, text="模块管理"))

        hbox = WidgetUtil.createHBoxLayout(spacing=5)
        self.addModuleBtn = WidgetUtil.createPushButton(self, text="Add", toolTip="添加新的选项配置", isEnable=False,
                                                        onClicked=self.addModule)
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

        # self.setLineWidth(2)
        # self.setFrameShadow(QFrame.Plain)
        # self.setFrameShape(QFrame.Box)
        self.setStyleSheet("ModuleManagerWidget{border:1px solid rgb(255,0,0)}")
        pass

    def setProjectInfo(self, projectInfo):
        LogUtil.d("setProjectInfo", projectInfo)
        self.projectInfo = projectInfo
        projectId = DictUtil.get(projectInfo, KEY_ID)
        self.addModuleBtn.setEnabled(projectId is not None)
        self.modules = self.projectManager.getProjectModules(projectId) if projectId else []
        self.updateModuleList()
        pass

    def getProjectPath(self):
        return DictUtil.get(self.projectInfo, KEY_PATH)

    def getSelectedModules(self):
        res = []
        for item in self.moduleWidgets:
            if item.isChecked():
                res.append(item.getOptionGroupInfo())
        return res

    def getOptionGroups(self):
        if self.getOptionGroupsFunc:
            return self.getOptionGroupsFunc()
        else:
            return []

    def addModule(self):
        LogUtil.d("addModule")
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, openDir=self.getProjectPath(),
                              moduleList=self.modules, optionGroups=self.getOptionGroups())
        pass

    def editModule(self, moduleInfo):
        LogUtil.d("editModule", moduleInfo)
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, openDir=self.getProjectPath(), default=moduleInfo,
                              moduleList=self.modules, optionGroups=self.getOptionGroups())
        pass

    def addOrEditModuleCallback(self, info):
        LogUtil.d("addOrEditModuleCallback", info)
        if info:
            self.modules.append(info)
        self.modules = sorted(self.modules, key=lambda x: x[KEY_NAME])
        self.updateModuleList()
        self.projectManager.saveProjectModulesInfo(DictUtil.get(self.projectInfo, KEY_ID), self.modules)
        pass

    def delModule(self, moduleWidget, moduleInfo):
        LogUtil.d("delModule", moduleInfo)
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{moduleInfo[KEY_NAME]}（{moduleInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=lambda: (
                self.vLayout.removeWidget(moduleWidget),
                moduleWidget.deleteLater(),
                self.moduleWidgets.remove(moduleWidget),
                self.modules.remove(moduleInfo),
                self.projectManager.saveProjectModulesInfo(DictUtil.get(self.projectInfo, KEY_ID), self.modules)
            ))
        pass

    def updateModuleItem(self, index, moduleInfo):
        LogUtil.d("updateModuleItem", index, moduleInfo)
        if index >= len(self.moduleWidgets):
            moduleWidget = ModuleWidget(moduleInfo=moduleInfo, editFunc=self.editModule, delFunc=self.delModule)
            self.moduleWidgets.append(moduleWidget)
            self.vLayout.addWidget(moduleWidget)
        else:
            self.moduleWidgets[index].updateUi(moduleInfo)
        pass

    def updateModuleList(self):
        LogUtil.d("updateModuleList")
        moduleLen = len(self.modules)
        while moduleLen < len(self.moduleWidgets):
            widget = self.moduleWidgets[moduleLen]
            self.vLayout.removeWidget(widget)
            widget.deleteLater()
            self.moduleWidgets.remove(widget)
        self.vLayout.removeItem(self.spacerItem)
        for index, item in enumerate(self.modules):
            self.updateModuleItem(index, item)
        self.vLayout.addItem(self.spacerItem)
        pass


class ModuleWidget(QWidget):
    def __init__(self, moduleInfo, editFunc, delFunc):
        super(ModuleWidget, self).__init__()
        self.moduleInfo = moduleInfo

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(0, 0, 0, 0))
        self.checkBox = WidgetUtil.createCheckBox(self, text=moduleInfo[KEY_NAME], toolTip=moduleInfo[KEY_DESC])
        hbox.addWidget(self.checkBox)
        # 为窗口添加QActions
        self.addAction(WidgetUtil.createAction(self, text="编辑", func=lambda: editFunc(self.moduleInfo)))
        self.addAction(WidgetUtil.createAction(self, text="删除", func=lambda: delFunc(self, self.moduleInfo)))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setStyleSheet("QWidget:hover{background-color:rgb(0,255,255)}")
        pass

    def updateUi(self, moduleInfo):
        self.moduleInfo = moduleInfo
        self.checkBox.setText(moduleInfo[KEY_NAME])
        self.checkBox.setToolTip(moduleInfo[KEY_DESC])
        self.checkBox.setChecked(False)
        pass

    def getModuleInfo(self):
        return self.moduleInfo

    def isChecked(self):
        return self.checkBox.isChecked()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ModuleManagerWidget()
    e.show()
    sys.exit(app.exec_())
