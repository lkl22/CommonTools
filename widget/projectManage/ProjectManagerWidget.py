# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManagerWidget.py
# 定义一个ProjectManagerWidget窗口类实现工程配置管理相关功能
import os
from PyQt5.QtWidgets import QFrame
from util.DateUtil import DateUtil
from util.FileUtil import FileUtil
from util.ListUtil import ListUtil
from util.WidgetUtil import *
from widget.projectManage.AddOrEditProjectDialog import AddOrEditProjectDialog
from widget.projectManage.ProjectManager import *

TAG = "ProjectManagerWidget"


class ProjectManagerWidget(QFrame):
    def __init__(self, projectManager: ProjectManager, modifyCallback):
        super(ProjectManagerWidget, self).__init__()

        self.projectManager = projectManager
        self.modifyCallback = modifyCallback
        self.projects = self.projectManager.projects
        if not self.projects:
            self.projects = {KEY_DEFAULT: -1, KEY_LIST: []}
        self.curProjectIndex = self.projects[KEY_DEFAULT]

        self.setObjectName(TAG)
        self.setToolTip("工程配置信息管理")
        widgetLayout = WidgetUtil.createVBoxLayout()

        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(self, text="请选择工程："))
        self.projectComboBox = WidgetUtil.createComboBox(self, activated=self.projectIndexChanged, sizePolicy=WidgetUtil.createSizePolicy())
        hbox.addWidget(self.projectComboBox, 1)

        hbox.addWidget(WidgetUtil.createPushButton(self, text="Add", toolTip="添加新项目", onClicked=self.addProject))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Modify", toolTip="修改项目配置", onClicked=self.modifyProject))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Del", toolTip="删除项目", onClicked=self.delProject))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Save As", toolTip="导出该项目配置", onClicked=self.saveAsProject))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Import", toolTip="导入项目配置", onClicked=self.importProject))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(self, text="项目配置信息："))

        self.projectConfigInfoTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        vbox.addWidget(self.projectConfigInfoTextEdit)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("ProjectManagerWidget{border:1px solid rgb(0,0,255)}")
        self.updateProjectComboBox()
        pass

    def genProjectDesc(self, projectInfo):
        evnList = DictUtil.get(projectInfo, KEY_EVN_LIST)
        evnDesc = ""
        if evnList:
            evnDesc = "<span style='color:blue;'>环境变量：</span><br/>"
            for item in evnList:
                evnDesc += f"<span style='color:green;'>变量名：{item[KEY_NAME]}<br/>变量值：{item[KEY_VALUE]}</span><br/>" \
                           f"{'Path环境变量' if item[KEY_EVN_IS_PATH] else '普通环境变量'}<br/>描述：{item[KEY_DESC]}<br/><br/>"

        desc = f"<span style='color:blue;'>工程路径：<br/></span><span style='color:green;'>{projectInfo[KEY_PATH]}</span>" \
               f"<br/><br/>{evnDesc}"
        return desc

    def updateProjectDesc(self):
        projectInfo = self.getCurProjectInfo()
        self.modifyCallback(projectInfo)
        self.projectConfigInfoTextEdit.setText(self.genProjectDesc(projectInfo) if projectInfo else "")

    def updateProjectComboBox(self):
        if self.projects and self.projects[KEY_LIST]:
            self.projectComboBox.clear()
            for index, item in enumerate(self.projects[KEY_LIST]):
                self.projectComboBox.addItem(f"{item[KEY_NAME]}（{item[KEY_DESC]}）", item)
            if self.curProjectIndex < 0:
                self.curProjectIndex = 0
            curProjectInfo = self.projects[KEY_LIST][self.curProjectIndex]
            self.projectComboBox.setCurrentText(f"{curProjectInfo[KEY_NAME]}（{curProjectInfo[KEY_DESC]}）")
            self.updateProjectDesc()
            LogUtil.d(TAG, 'updateFlavorComboBox setCurrentText', curProjectInfo[KEY_NAME])
        else:
            self.projectComboBox.clear()
            self.curProjectIndex = -1
            self.updateProjectDesc()
            LogUtil.d(TAG, "no project")
        pass

    def projectIndexChanged(self, index):
        LogUtil.d(TAG, 'projectIndexChanged', index)
        self.curProjectIndex = index
        self.updateProjectDesc()
        self.saveProjects()
        pass

    def saveProjects(self):
        # 更新当前默认打开的项目信息
        self.projects[KEY_DEFAULT] = self.curProjectIndex
        # 将项目配置保存到ini文件
        self.projectManager.saveProjects(self.projects)
        pass

    def addProject(self):
        LogUtil.d(TAG, "addProject")
        AddOrEditProjectDialog(callback=self.addOrEditProjectCallback)
        pass

    def modifyProject(self):
        LogUtil.d(TAG, "modifyProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return
        AddOrEditProjectDialog(callback=self.addOrEditProjectCallback,
                               projectInfo=self.projects[KEY_LIST][self.curProjectIndex], projectList=self.projects)
        pass

    def addOrEditProjectCallback(self, info):
        LogUtil.d(TAG, "addOrEditProjectCallback", info)
        projects = self.projects[KEY_LIST]
        if info:
            projects.append(info)
        curProjectInfo = self.getCurProjectInfo()
        # 按项目名称重新排序
        self.projects[KEY_LIST] = sorted(projects, key=lambda x: x[KEY_NAME])
        if curProjectInfo:
            for index, item in enumerate(self.projects[KEY_LIST]):
                if curProjectInfo == item:
                    self.curProjectIndex = index
                    break
        # 更新工程下拉选择框
        self.updateProjectComboBox()
        # 将工程信息保存到ini文件
        self.saveProjects()
        pass

    def getCurProjectInfo(self):
        if self.curProjectIndex >= 0:
            return self.projects[KEY_LIST][self.curProjectIndex]
        else:
            return None

    def delProject(self):
        LogUtil.d(TAG, "delProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return
        projectInfo = self.getCurProjectInfo()
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{projectInfo[KEY_NAME]}（{projectInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=self.delProjectItem)
        pass

    def delProjectItem(self):
        LogUtil.i(TAG, "delProjectItem")
        curProjectInfo = self.getCurProjectInfo()
        self.projects[KEY_LIST].remove(curProjectInfo)
        self.curProjectIndex = -1
        self.updateProjectComboBox()
        self.projectManager.delProjectInfoById(curProjectInfo[KEY_ID])
        self.saveProjects()
        pass

    def saveAsProject(self):
        LogUtil.d(TAG, "saveAsProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return

        curProjectInfo = self.getCurProjectInfo()
        detailProjectInfo = self.projectManager.getProjectInfoById(curProjectInfo[KEY_ID])

        saveData = {"simpleInfo": curProjectInfo, "detailInfo": detailProjectInfo if detailProjectInfo else {}}
        fp = WidgetUtil.getExistingDirectory(caption="请选择要备份保存的路径，不选的话默认使用当前工程路径。",
                                             directory=DictUtil.get(curProjectInfo, KEY_PATH, "./"))
        if not fp:
            fp = DictUtil.get(curProjectInfo, KEY_PATH, "./")
        saveFile = os.path.join(fp,
                                f"{curProjectInfo[KEY_NAME]}_{DateUtil.nowTime(timeFormat='%Y-%m-%d_%H:%M:%S')}.json")
        with open(saveFile, 'w', encoding="utf-8") as file:
            file.write(JsonUtil.encode(saveData, ensureAscii=False))
        WidgetUtil.showAboutDialog(
            text=f"你成功保存<span style='color:red;'>{curProjectInfo[KEY_NAME]}</span>工程信息到<span style='color:red;'>{saveFile}</span>")
        pass

    def importProject(self):
        LogUtil.d(TAG, "importProject")
        curProjectInfo = self.getCurProjectInfo()
        directory = DictUtil.get(curProjectInfo, KEY_PATH, "./")
        fp = WidgetUtil.getOpenFileName(caption='选择备份的工程配置文件', directory=directory, filter='*.json',
                                        initialFilter='*.json')
        if not fp:
            WidgetUtil.showAboutDialog(text="您未选择配置文件，导入工程配置失败。")
            return

        fileContent = FileUtil.readFile(fp)
        if not fileContent:
            WidgetUtil.showAboutDialog(text="您选择的配置文件没有内容，导入工程配置失败。")
            return
        projectInfo = JsonUtil.decode(fileContent)
        if not DictUtil.get(DictUtil.get(projectInfo, "simpleInfo", {}), KEY_NAME):
            WidgetUtil.showAboutDialog(text="您选择的配置文件格式错误，导入工程配置失败。")
            return
        if ListUtil.contain(self.projects[KEY_LIST], KEY_NAME, projectInfo["simpleInfo"][KEY_NAME]):
            WidgetUtil.showQuestionDialog(message=f"{projectInfo['simpleInfo'][KEY_NAME]}已经存在，是否继续，继续将覆盖现有的配置。",
                                          acceptFunc=lambda: self.startImportProject(projectInfo, True))
            return
        self.startImportProject(projectInfo)
        pass

    def startImportProject(self, projectInfo, has=False):
        LogUtil.d(TAG, "startImportProject", has)
        projects = self.projects[KEY_LIST]
        if has:
            projects.remove(ListUtil.find(projects, KEY_NAME, projectInfo['simpleInfo'][KEY_NAME]))
        projects.append(projectInfo['simpleInfo'])
        # 按项目名称重新排序
        self.projects[KEY_LIST] = sorted(projects, key=lambda x: x[KEY_NAME])
        self.projectManager.saveProjectInfoById(projectInfo['simpleInfo'][KEY_ID], projectInfo['detailInfo'])
        # 更新工程下拉选择框
        self.updateProjectComboBox()
        # 将工程信息保存到ini文件
        self.saveProjects()
        WidgetUtil.showAboutDialog(
            text=f"您成功导入<span style='color:red;'>{projectInfo['simpleInfo'][KEY_NAME]}</span>工程信息")
        pass
