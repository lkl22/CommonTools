# -*- coding: utf-8 -*-
# python 3.x
# Filename: ModuleManagerWidget.py
# 定义一个ModuleManagerWidget窗口类实现模块管理的功能
import copy
import sys

from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QScrollArea, QFrame

from util.FileUtil import FileUtil
from util.ListUtil import ListUtil
from util.WidgetUtil import *
from widget.projectManage.AddOrEditModuleDialog import AddOrEditModuleDialog
from widget.projectManage.ModuleDependencyDialog import ModuleDependencyDialog
from widget.projectManage.ProjectManager import *

TAG = "ModuleManagerWidget"


class ModuleManagerWidget(QFrame):
    def __init__(self, projectManager: ProjectManager, getOptionGroupsFunc=None, getCmdGroupsFunc=None, isDebug=False):
        super(ModuleManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.getOptionGroupsFunc = getOptionGroupsFunc
        self.getCmdGroupsFunc = getCmdGroupsFunc
        self.projectInfo = None
        self.modules = []
        self.moduleWidgets: [ModuleWidget] = []
        self.isDebug = isDebug

        self.setObjectName("ModuleManagerWidget")
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5))

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=0)
        hbox.addWidget(WidgetUtil.createLabel(self, text="模块管理"))
        self.addModuleBtn = WidgetUtil.createPushButton(self, text="Add", toolTip="添加新的选项配置", isEnable=False,
                                                        onClicked=self.addModule)
        hbox.addWidget(self.addModuleBtn)
        self.previewModuleDependencyBtn = WidgetUtil.createPushButton(self, text="Preview", toolTip="预览模块之间依赖关系",
                                                                      isEnable=False,
                                                                      onClicked=self.previewModuleDependency)
        hbox.addWidget(self.previewModuleDependencyBtn)
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

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=0)
        self.allSelectedCheckBox = WidgetUtil.createCheckBox(self, text="全选", toolTip="☑️选中所有显示的模块，否则取消全选。",
                                                             isEnable=False,
                                                             isChecked=False, clicked=self.allSelected)
        hbox.addWidget(self.allSelectedCheckBox)
        self.showAllBtn = WidgetUtil.createPushButton(self, text="显示所有", toolTip="显示所有配置的工程模块。",
                                                      onClicked=self.showAllModuleWidget)
        hbox.addWidget(self.showAllBtn)
        self.hideSelectedBtn = WidgetUtil.createPushButton(self, text="隐藏", toolTip="隐藏选择的工程模块。",
                                                           onClicked=self.hideSelectedModulesWidget)
        hbox.addWidget(self.hideSelectedBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        # self.setLineWidth(2)
        # self.setFrameShadow(QFrame.Plain)
        # self.setFrameShape(QFrame.Box)
        # self.setStyleSheet("ModuleManagerWidget{border:1px solid rgb(255,0,0)}")
        pass

    def setProjectInfo(self, projectInfo):
        LogUtil.d(TAG, "setProjectInfo", projectInfo)
        self.projectInfo = projectInfo
        projectId = DictUtil.get(projectInfo, KEY_ID)
        self.addModuleBtn.setEnabled(projectId is not None)
        self.previewModuleDependencyBtn.setEnabled(projectId is not None)
        self.allSelectedCheckBox.setEnabled(projectId is not None)
        self.modules = self.projectManager.getProjectModules(projectId) if projectId else []
        self.updateModuleList(False)
        self.updateAllSelectedCheckBoxStatus()
        pass

    def getProjectPath(self):
        return DictUtil.get(self.projectInfo, KEY_PATH)

    def getSelectedModules(self):
        res = []
        for item in self.moduleWidgets:
            if item.isChecked():
                res.append(item.getModuleInfo())
        return res

    def getOptionGroups(self):
        if self.getOptionGroupsFunc:
            return self.getOptionGroupsFunc()
        else:
            return []

    def getCmdGroups(self):
        if self.getCmdGroupsFunc:
            return self.getCmdGroupsFunc()
        else:
            return []

    def addModule(self):
        LogUtil.d(TAG, "addModule")
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, openDir=self.getProjectPath(),
                              moduleList=self.modules, optionGroups=self.getOptionGroups(),
                              cmdGroups=self.getCmdGroups())
        pass

    def previewModuleDependency(self):
        LogUtil.d(TAG, "previewModuleDependency")
        ModuleDependencyDialog(ProjectManager.generateDiGraph(self.modules))
        pass

    def allSelected(self):
        allSelected = self.allSelectedCheckBox.isChecked()
        LogUtil.d(TAG, "allSelected", allSelected)
        for moduleInfo in self.modules:
            if DictUtil.get(moduleInfo, KEY_IS_VISIBLE, DEFAULT_VALUE_IS_VISIBLE):
                moduleInfo[KEY_IS_SELECTED] = allSelected
        self.updateModuleList()
        pass

    def showAllModuleWidget(self):
        LogUtil.d(TAG, "showAllModuleWidget")
        for moduleInfo in self.modules:
            moduleInfo[KEY_IS_VISIBLE] = True
        self.updateModuleList()
        self.updateAllSelectedCheckBoxStatus()
        pass

    def hideSelectedModulesWidget(self):
        LogUtil.d(TAG, "hideSelectedModulesWidget")
        selectedModules = self.getSelectedModules()
        if not selectedModules:
            WidgetUtil.showAboutDialog(text="请先选择至少一个工程模块")
            return
        for moduleInfo in selectedModules:
            moduleInfo[KEY_IS_VISIBLE] = False
            # 隐藏了就取消选中状态
            moduleInfo[KEY_IS_SELECTED] = False
        self.allSelectedCheckBox.setChecked(False)
        self.updateModuleList()
        pass

    def updateAllSelectedCheckBoxStatus(self):
        isChecked = True if self.modules else False
        for moduleInfo in self.modules:
            if DictUtil.get(moduleInfo, KEY_IS_VISIBLE, DEFAULT_VALUE_IS_VISIBLE) and \
                    not DictUtil.get(moduleInfo, KEY_IS_SELECTED, DEFAULT_VALUE_IS_SELECTED):
                isChecked = False
                break
        self.allSelectedCheckBox.setChecked(isChecked)
        pass

    def editModule(self, moduleInfo):
        LogUtil.d(TAG, "editModule", moduleInfo)
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, openDir=self.getProjectPath(), default=moduleInfo,
                              moduleList=self.modules, optionGroups=self.getOptionGroups(),
                              cmdGroups=self.getCmdGroups())
        pass

    def copyModule(self, moduleInfo):
        LogUtil.d(TAG, "copyModule", moduleInfo)
        AddOrEditModuleDialog(callback=self.addOrEditModuleCallback, openDir=self.getProjectPath(),
                              default=copy.deepcopy(moduleInfo),
                              moduleList=self.modules, optionGroups=self.getOptionGroups(),
                              cmdGroups=self.getCmdGroups(), isCopyEdit=True)
        pass

    def addOrEditModuleCallback(self, info):
        LogUtil.d(TAG, "addOrEditModuleCallback", info)
        if info:
            self.modules.append(info)
        self.modules = sorted(self.modules, key=lambda x: x[KEY_NAME])
        self.updateModuleList()
        pass

    def delModule(self, moduleWidget, moduleInfo):
        LogUtil.d(TAG, "delModule", moduleInfo)
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{moduleInfo[KEY_NAME]}（{moduleInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=lambda: (
                self.vLayout.removeWidget(moduleWidget),
                moduleWidget.deleteLater(),
                self.moduleWidgets.remove(moduleWidget),
                self.modules.remove(moduleInfo),
                self.saveProjectModulesInfo()
            ))
        pass

    def saveProjectModulesInfo(self):
        self.projectManager.saveProjectModulesInfo(DictUtil.get(self.projectInfo, KEY_ID), self.modules)
        pass

    def updateModuleItem(self, index, moduleInfo):
        LogUtil.d(TAG, "updateModuleItem", index, moduleInfo)
        if index >= len(self.moduleWidgets):
            moduleWidget = ModuleWidget(moduleInfo=moduleInfo,
                                        editFunc=self.editModule,
                                        copyFunc=self.copyModule,
                                        hideFunc=self.saveProjectModulesInfo,
                                        delFunc=self.delModule,
                                        selectedChanged=self.saveProjectModulesInfo,
                                        isDebug=self.isDebug)
            self.moduleWidgets.append(moduleWidget)
            self.vLayout.addWidget(moduleWidget)
        else:
            self.moduleWidgets[index].updateUi(moduleInfo)
        self.moduleWidgets[index].setVisible(DictUtil.get(moduleInfo, KEY_IS_VISIBLE, DEFAULT_VALUE_IS_VISIBLE))
        pass

    def updateModuleList(self, needSaveModulesInfo=True):
        LogUtil.d(TAG, "updateModuleList")
        if needSaveModulesInfo:
            self.saveProjectModulesInfo()
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

    def updateModuleExecStatus(self, moduleName, status):
        LogUtil.d(TAG, "updateModuleExecStatus", moduleName, status)
        for index, moduleInfo in enumerate(self.modules):
            if moduleName == moduleInfo[KEY_NAME] or moduleName == KEY_ALL:
                self.moduleWidgets[index].updateStatus(status)
        pass


class ModuleWidget(QWidget):
    def __init__(self, moduleInfo, editFunc, copyFunc, hideFunc, delFunc, selectedChanged, isDebug=False):
        super(ModuleWidget, self).__init__()
        self.moduleInfo = moduleInfo
        self.hideFunc = hideFunc
        self.selectedChanged = selectedChanged
        self.isDebug = isDebug

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(0, 0, 0, 0))
        self.checkBox = WidgetUtil.createCheckBox(self, clicked=self.moduleSelectedChange)
        hbox.addWidget(self.checkBox)
        self.label = WidgetUtil.createLabel(self)
        hbox.addWidget(self.label)
        # 为窗口添加QActions
        self.addAction(WidgetUtil.createAction(self, text="编辑", func=lambda: editFunc(self.moduleInfo)))
        self.addAction(WidgetUtil.createAction(self, text="Copy", func=lambda: copyFunc(self.moduleInfo)))
        self.addAction(WidgetUtil.createAction(self, text="隐藏", func=self.hideWidget))
        self.addAction(WidgetUtil.createAction(self, text="删除", func=lambda: delFunc(self, self.moduleInfo)))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        # self.setStyleSheet("QWidget:hover{background-color:rgb(0,255,255)}")

        self.updateUi(moduleInfo)
        self.updateStatus(STATUS_HIDE)
        pass

    def hideWidget(self):
        self.setVisible(False)
        self.moduleInfo[KEY_IS_VISIBLE] = False
        self.moduleInfo[KEY_IS_SELECTED] = False
        self.hideFunc()

    def updateUi(self, moduleInfo):
        self.moduleInfo = moduleInfo
        self.checkBox.setText(moduleInfo[KEY_NAME])
        self.checkBox.setToolTip(moduleInfo[KEY_DESC])
        self.checkBox.setChecked(DictUtil.get(moduleInfo, KEY_IS_SELECTED, DEFAULT_VALUE_IS_SELECTED))
        font = QFont()
        font.setBold(self.checkBox.isChecked()),
        self.checkBox.setFont(font)
        pass

    def moduleSelectedChange(self):
        self.moduleInfo[KEY_IS_SELECTED] = self.isChecked()
        LogUtil.d(TAG, "moduleSelectedChange", self.moduleInfo[KEY_IS_SELECTED])
        self.selectedChanged()
        pass

    def getModuleInfo(self):
        return self.moduleInfo

    def isChecked(self):
        return self.checkBox.isChecked()

    def updateStatus(self, status):
        self.label.setVisible(status != STATUS_HIDE)
        if status == STATUS_LOADING:
            movie = QMovie("../../resources/icons/loading.gif" if self.isDebug else FileUtil.getIconFp("loading.gif"))
            movie.setScaledSize(QSize(16, 16))
            self.label.setMovie(movie)
            movie.start()
        elif status == STATUS_SUCCESS:
            pixmap = QPixmap("../../resources/icons/projectManager/success.png" if self.isDebug else FileUtil.getIconFp(
                "projectManager/success.png"))
            pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        elif status == STATUS_FAILED:
            pixmap = QPixmap("../../resources/icons/projectManager/error.png" if self.isDebug else FileUtil.getIconFp(
                "projectManager/error.png"))
            pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(pixmap)
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = ModuleManagerWidget()
    e.show()
    sys.exit(app.exec_())
