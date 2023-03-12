# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManagerDialog.py
# 定义一个ProjectManagerDialog类实现项目管理功能
import copy
import os.path
import threading
from concurrent.futures import as_completed, CancelledError
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtCore import pyqtSignal

from util.DateUtil import DateUtil
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from util.PlatformUtil import PlatformUtil
from util.ProcessManager import ProcessManager
from util.StrUtil import StrUtil
from util.WidgetUtil import *
from PyQt5.QtWidgets import *

from widget.custom.LoadingDialog import LoadingDialog
from widget.projectManage.AddOrEditProjectDialog import AddOrEditProjectDialog
from widget.projectManage.CmdManagerWidget import CmdManagerWidget
from widget.projectManage.ModuleManagerWidget import ModuleManagerWidget
from widget.projectManage.OptionManagerWidget import OptionManagerWidget
from widget.projectManage.ProjectManager import *
from widget.projectManage.ProjectManagerUtil import ProjectManagerUtil

TYPE_HIDE_LOADING_DIALOG = 1

TAG = "ProjectManagerWindow"
PROCESS_MANAGER = "processManager"


class ProjectManagerWindow(QMainWindow):
    windowList = []
    execUi = pyqtSignal(int)

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        # 宽度不能设置太宽，设置太宽会显示在左上角不居中
        ProjectManagerWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        ProjectManagerWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Project Manage Window")
        self.setObjectName("ProjectManagerWindow")
        self.setWindowTitle(WidgetUtil.translate(text="项目管理"))
        self.resize(ProjectManagerWindow.WINDOW_WIDTH, ProjectManagerWindow.WINDOW_HEIGHT)

        self.isDebug = isDebug
        self.projectManager = ProjectManager(isDebug)
        self.projects = self.projectManager.projects
        if not self.projects:
            self.projects = {KEY_DEFAULT: -1, KEY_LIST: []}
        self.curProjectIndex = self.projects[KEY_DEFAULT]

        self.executor = ThreadPoolExecutor(thread_name_prefix="ProjectExecute_")
        self.futureList = []
        self.processManagers = []

        self.optionManagerWidget = OptionManagerWidget(projectManager=self.projectManager)
        self.cmdManagerWidget = CmdManagerWidget(projectManager=self.projectManager)
        self.moduleManagerWidget = ModuleManagerWidget(projectManager=self.projectManager,
                                                       getOptionGroupsFunc=lambda: self.optionManagerWidget.getProjectOptionGroups(),
                                                       getCmdGroupsFunc=lambda: self.cmdManagerWidget.getProjectCmdGroupList())
        self.loadingDialog = None
        self.lock = threading.RLock()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)

        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.projectManageGroupBox = self.createProjectManageGroupBox(self)
        hLayout.addWidget(self.projectManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.updateProjectComboBox()
        self.show()
        self.execUi.connect(self.updateUi)

    def updateUi(self, type):
        if type == TYPE_HIDE_LOADING_DIALOG and self.loadingDialog is not None:
            self.loadingDialog.hide()
        pass

    # 重写关闭事件，回到第一界面
    def closeEvent(self, event):
        if self.isDebug:
            return
        from widget.MainWidget import MainWidget
        window = MainWidget()
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        window.show()
        event.accept()
        pass

    def createProjectManageGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(self.createMainModuleGroupBox(box))

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(self.moduleManagerWidget, 1)
        optionLayout = WidgetUtil.createVBoxLayout()
        optionLayout.addWidget(self.optionManagerWidget, 2)
        optionLayout.addWidget(self.cmdManagerWidget, 1)
        hbox.addLayout(optionLayout, 2)
        vbox.addLayout(hbox, 5)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.startExecute))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def createMainModuleGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="工程配置")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择工程："))
        self.projectComboBox = WidgetUtil.createComboBox(box, activated=self.projectIndexChanged)
        hbox.addWidget(self.projectComboBox, 1)

        hbox.addWidget(WidgetUtil.createPushButton(box, text="Add", toolTip="添加新项目", onClicked=self.addProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Modify", toolTip="修改项目配置", onClicked=self.modifyProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Del", toolTip="删除项目", onClicked=self.delProject))
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="Save As", toolTip="导出该项目配置", onClicked=self.saveAsProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Import", toolTip="导入项目配置", onClicked=self.importProject))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box, text="项目配置信息："))

        self.projectConfigInfoTextEdit = WidgetUtil.createTextEdit(box, isReadOnly=True)
        vbox.addWidget(self.projectConfigInfoTextEdit)
        box.setFixedHeight(int(ProjectManagerWindow.WINDOW_HEIGHT * 0.2))
        return box

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
        self.moduleManagerWidget.setProjectInfo(projectInfo)
        self.optionManagerWidget.setProjectInfo(projectInfo)
        self.cmdManagerWidget.setProjectInfo(projectInfo)
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

    def startExecute(self):
        LogUtil.d(TAG, f"startExecute main pid: {os.getpid()} threadId: {threading.current_thread().ident}")
        projectInfo = self.getCurProjectInfo()
        if not projectInfo:
            WidgetUtil.showAboutDialog(text="请先添加/选择一个工程")
            return
        modules = self.moduleManagerWidget.getSelectedModules()
        if not modules:
            WidgetUtil.showAboutDialog(text="请先添加/选择一个模块")
            return
        self.consoleTextEdit.setText("")

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.executeModuleCmd, args=(projectInfo, modules)).start()
        if self.loadingDialog is None:
            self.loadingDialog = LoadingDialog(showText="正在执行。。。", btnText="终止",
                                               rejectedFunc=self.stopExecCmd, isDebug=self.isDebug)
        else:
            self.loadingDialog.show()
        pass

    def stopExecCmd(self):
        threading.Thread(target=self.stopRun).start()
        LogUtil.d(TAG, "stopExecCmd")
        pass

    def handleCmdArgs(self, cmdInfo, optionGroups):
        args = DictUtil.get(cmdInfo, KEY_ARGUMENTS)
        conditionInputs = []
        # 指令依赖的option选项群组
        dynArgs = DictUtil.get(cmdInfo, KEY_DYNAMIC_ARGUMENTS, None)
        if dynArgs:
            conditionInputs = ProjectManagerUtil.extractConditionInputs(dynParams=dynArgs,
                                                                        optionGroups=optionGroups)
            args = ProjectManagerUtil.transformCmdParams(params=args, dynParams=dynArgs,
                                                         optionGroups=optionGroups)
        return args, conditionInputs

    def handleCmdList(self, moduleDir, srcCmdList):
        cmdList = []
        for item in srcCmdList:
            projectCmdGroups = self.cmdManagerWidget.getProjectCmdGroupInfo()
            cmdGroups = DictUtil.get(item, KEY_CMD_GROUPS, [])
            needIgnore = len(cmdGroups) > 0
            for cmdGroupName in cmdGroups:
                if cmdGroupName in projectCmdGroups[KEY_LIST] and cmdGroupName in projectCmdGroups[KEY_DEFAULT]:
                    needIgnore = False
                    break
            if needIgnore:
                continue
            # 工程的所有option选项群组
            projectOptionGroups = self.optionManagerWidget.getProjectOptionGroups()
            if not ProjectManagerUtil.isPreconditionsMatch(
                    preconditionsLogic=DictUtil.get(item, KEY_PRECONDITIONS_LOGIC),
                    preconditions=DictUtil.get(item, KEY_PRECONDITIONS, []),
                    optionGroups=projectOptionGroups):
                continue
            cmdArgs, conditionInput = self.handleCmdArgs(cmdInfo=item, optionGroups=projectOptionGroups)

            cmdWorkingDir = DictUtil.get(item, KEY_WORKING_DIR, moduleDir)
            cmdWorkingDir = moduleDir + cmdWorkingDir if DictUtil.get(item, KEY_IS_RELATIVE_PATH,
                                                                      False) else cmdWorkingDir

            cmdList.append({
                KEY_PROGRAM: DictUtil.get(item, KEY_PROGRAM),
                KEY_ARGUMENTS: cmdArgs,
                KEY_CONDITION_INPUT: conditionInput,
                KEY_WORKING_DIR: cmdWorkingDir,
            })
        return cmdList

    @staticmethod
    def dependencyTasksAllFinished(dependencies, allExecuteModules, hasFinishedTasks):
        dependencyTasksAllFinished = True
        if dependencies:
            for dependency in dependencies:
                if dependency in allExecuteModules and dependency not in hasFinishedTasks:
                    dependencyTasksAllFinished = False
                    break
        return dependencyTasksAllFinished

    def executeModuleCmd(self, projectInfo, modules):
        if not self.lock.acquire(timeout=1):
            self.lock.release()
            LogUtil.d(TAG, "acquire lock failed.")
            return
        self.lock.release()

        self.futureList.clear()
        self.processManagers.clear()
        LogUtil.e(TAG, f"executeModuleCmd start. pid: {os.getpid()} threadId: {threading.current_thread().ident}")

        allTasks = copy.deepcopy(modules)
        allExecuteModules = [item[KEY_NAME] for item in modules]
        hasFinishedTasks = []
        for moduleInfo in modules:
            projectDir = DictUtil.get(projectInfo, KEY_PATH)
            workingDir = DictUtil.get(moduleInfo, KEY_PATH, projectDir)
            workingDir = projectDir + workingDir if DictUtil.get(moduleInfo, KEY_IS_RELATIVE_PATH,
                                                                 False) else workingDir

            cmdList = self.handleCmdList(workingDir, DictUtil.get(moduleInfo, KEY_CMD_LIST, []))
            LogUtil.d(TAG, f"executeModuleCmd cmdList {cmdList} module work dir: {workingDir}")
            processManager = ProcessManager(name=DictUtil.get(moduleInfo, KEY_NAME),
                                            cmdList=cmdList,
                                            workingDir=workingDir,
                                            processEnv=DictUtil.get(projectInfo, KEY_EVN_LIST, []),
                                            standardOutput=self.standardOutput,
                                            standardError=self.standardError)
            self.processManagers.append({KEY_NAME: DictUtil.get(moduleInfo, KEY_NAME), PROCESS_MANAGER: processManager})
            dependencies = DictUtil.get(moduleInfo, KEY_MODULE_DEPENDENCIES, [])
            dependencyTasksAllFinished = ProjectManagerWindow.dependencyTasksAllFinished(dependencies,
                                                                                         allExecuteModules,
                                                                                         hasFinishedTasks)
            if dependencyTasksAllFinished:
                future = self.executor.submit(processManager.run)
                self.futureList.append(future)
                allTasks.remove(ListUtil.find(allTasks, KEY_NAME, moduleInfo[KEY_NAME]))

        hasNewTaskAdd = True
        while len(self.futureList) < len(modules) or hasNewTaskAdd:
            hasNewTaskAdd = False
            for future in as_completed(self.futureList):
                try:
                    isSuccess, taskName = future.result()
                except CancelledError as err:
                    LogUtil.e(TAG, "CancelledError", err)
                    break
                if taskName in hasFinishedTasks:
                    continue
                hasFinishedTasks.append(taskName)
                LogUtil.d(TAG, future, isSuccess, taskName, "hasFinishedTasks", hasFinishedTasks)
                copyAllTasks = copy.deepcopy(allTasks)
                for moduleInfo in copyAllTasks:
                    dependencies = DictUtil.get(moduleInfo, KEY_MODULE_DEPENDENCIES, [])
                    dependencyTasksAllFinished = ProjectManagerWindow.dependencyTasksAllFinished(dependencies,
                                                                                                 allExecuteModules,
                                                                                                 hasFinishedTasks)
                    if dependencyTasksAllFinished:
                        future = self.executor.submit(
                            ListUtil.find(self.processManagers, KEY_NAME, moduleInfo[KEY_NAME])[PROCESS_MANAGER].run)
                        self.futureList.append(future)
                        hasNewTaskAdd = True
                        allTasks.remove(ListUtil.find(allTasks, KEY_NAME, moduleInfo[KEY_NAME]))

        LogUtil.e(TAG, f"executeModuleCmd all finished. pid: {os.getpid()}")
        self.execUi.emit(TYPE_HIDE_LOADING_DIALOG)
        pass

    def stopRun(self):
        self.lock.acquire()
        try:
            for item in self.processManagers:
                item[PROCESS_MANAGER].kill()
            self.processManagers.clear()

            for future in self.futureList:
                future.cancel()
            self.futureList.clear()
            self.executor.shutdown(wait=False, cancel_futures=True)
            self.executor = ThreadPoolExecutor(thread_name_prefix="ProjectExecute_")
        except Exception as err:
            LogUtil.e(TAG, err)
        self.lock.release()
        LogUtil.d(TAG, "stopRun")
        pass

    def standardOutput(self, log):
        if "开始执行" in log or "执行结束" in log:
            WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log, color='#000')
        else:
            WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log)
        pass

    def standardError(self, log):
        WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log, color='#f00')
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProjectManagerWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
