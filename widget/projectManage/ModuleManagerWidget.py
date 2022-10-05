# -*- coding: utf-8 -*-
# python 3.x
# Filename: ModuleManagerWidget.py
# 定义一个ModuleManagerWidget窗口类实现模块管理的功能
import sys
from PyQt5.QtWidgets import QScrollArea
from util.WidgetUtil import *
from widget.projectManage.AddOrEditModuleDialog import AddOrEditModuleDialog
from widget.projectManage.ProjectManager import *


class ModuleManagerWidget(QWidget):
    def __init__(self, projectManager: ProjectManager):
        super(ModuleManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.projectId = None
        self.modules = []
        self.moduleWidgets: [ModuleWidget] = []

        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(WidgetUtil.createLabel(self, text="模块管理"))

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.addModuleBtn = WidgetUtil.createPushButton(self, text="Add", toolTip="添加新的模块", isEnable=False, onClicked=self.addModule)
        hbox.addWidget(self.addModuleBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        box = WidgetUtil.createGroupBox(self, title="")
        vbox.addWidget(box, 1)

        groupBoxlayout = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        scrollAres = QScrollArea(self)
        scrollAres.setWidgetResizable(True)
        scrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        scrollAres.setWidget(scrollAreaWidget)
        groupBoxlayout.addWidget(scrollAres, 1)

        # 进行垂直布局
        self.vLayout = WidgetUtil.createVBoxLayout(scrollAreaWidget)
        self.spacerItem = WidgetUtil.createVSpacerItem(1, 1)
        self.vLayout.addItem(self.spacerItem)
        pass

    def setProjectId(self, projectId):
        LogUtil.d("setProjectId", projectId)
        self.addModuleBtn.setEnabled(projectId is not None)
        self.projectId = projectId
        self.modules = self.projectManager.getProjectModules(projectId)
        self.updateModuleList()
        pass

    def addModule(self):
        LogUtil.d("addModule")
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, moduleList=self.modules)
        pass

    def addOrEditModuleCallback(self, info):
        LogUtil.d("addOrEditModuleCallback", info)
        if info:
            self.modules.append(info)
        self.modules = sorted(self.modules, key=lambda x: x[KEY_NAME])
        self.updateModuleList()
        self.projectManager.saveProjectModulesInfo(self.projectId, self.modules)
        pass

    def updateModuleItem(self, index, moduleInfo):
        LogUtil.d("updateModuleItem", index, moduleInfo)
        if index >= len(self.moduleWidgets):
            moduleWidget = ModuleWidget(moduleInfo)
            self.moduleWidgets.append(moduleWidget)
            self.vLayout.addWidget(moduleWidget)
        else:
            self.moduleWidgets[index].updateUi(moduleInfo)
        pass

    def updateModuleList(self):
        LogUtil.d("updateModuleList")
        if len(self.modules) < len(self.moduleWidgets):
            for index in range(len(self.modules), len(self.moduleWidgets)):
                widget = self.moduleWidgets[index]
                self.vLayout.removeWidget(widget)
                widget.deleteLater()
                self.moduleWidgets.remove(widget)
        self.vLayout.removeItem(self.spacerItem)
        for index, item in enumerate(self.modules):
            self.updateModuleItem(index, item)
        self.vLayout.addItem(self.spacerItem)
        pass


class ModuleWidget(QWidget):
    def __init__(self, moduleInfo):
        super(ModuleWidget, self).__init__()
        hbox = WidgetUtil.createHBoxLayout(self)
        self.checkBox = WidgetUtil.createCheckBox(self, text=moduleInfo[KEY_NAME], toolTip=moduleInfo[KEY_DESC])
        hbox.addWidget(self.checkBox)
        pass

    def updateUi(self, moduleInfo):
        self.checkBox.setText(moduleInfo[KEY_NAME])
        self.checkBox.setToolTip(moduleInfo[KEY_DESC])
        self.checkBox.setChecked(False)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ModuleManagerWidget()
    e.show()
    sys.exit(app.exec_())
