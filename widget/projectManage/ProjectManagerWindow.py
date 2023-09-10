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
from util.ListUtil import ListUtil
from util.OperaIni import *
from util.ProcessManager import ProcessManager
from util.WidgetUtil import *
from PyQt5.QtWidgets import *
from widget.projectManage.CmdManagerWidget import CmdManagerWidget
from widget.projectManage.ModuleManagerWidget import ModuleManagerWidget
from widget.projectManage.OptionManagerWidget import OptionManagerWidget
from widget.projectManage.ProjectManager import *
from widget.projectManage.ProjectManagerUtil import ProjectManagerUtil
from widget.projectManage.ProjectManagerWidget import ProjectManagerWidget

TYPE_HIDE_LOADING_DIALOG = 1

TAG = "ProjectManagerWindow"
PROCESS_MANAGER = "processManager"


class ProjectManagerWindow(QMainWindow):
    windowList = []
    updateModuleStatusSignal = pyqtSignal(str, str)
    standardOutputSignal = pyqtSignal(str)

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
        self.projectManager = ProjectManager()

        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="ProjectExecute_")
        self.futureList = []
        self.processManagers = []

        self.optionManagerWidget = OptionManagerWidget(projectManager=self.projectManager,
                                                       modifyCallback=self.optionGroupModify)
        self.cmdManagerWidget = CmdManagerWidget(projectManager=self.projectManager, modifyCallback=self.cmdGroupModify)
        self.moduleManagerWidget = ModuleManagerWidget(projectManager=self.projectManager,
                                                       getOptionGroupsFunc=lambda: self.optionManagerWidget.getProjectOptionGroups(),
                                                       getCmdGroupsFunc=lambda: self.cmdManagerWidget.getProjectCmdGroupList(),
                                                       autoSelectedModulesFunc=self.autoSelectedModulesFunc,
                                                       isDebug=self.isDebug)
        self.projectManagerWidget = ProjectManagerWidget(projectManager=self.projectManager,
                                                         modifyCallback=self.projectModify)
        self.lock = threading.RLock()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)

        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.projectManageGroupBox = self.createProjectManageGroupBox()
        hLayout.addWidget(self.projectManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)
        QtCore.QMetaObject.connectSlotsByName(self)

        self.show()
        self.updateModuleStatusSignal.connect(self.updateModuleExecStatus)
        self.standardOutputSignal.connect(self.standardOutput)

    def updateModuleExecStatus(self, moduleName, status):
        self.moduleManagerWidget.updateModuleExecStatus(moduleName=moduleName, status=status)
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

    def projectModify(self, projectInfo):
        LogUtil.d(TAG, "projectModify")
        self.moduleManagerWidget.setProjectInfo(projectInfo)
        self.optionManagerWidget.setProjectInfo(projectInfo)
        self.cmdManagerWidget.setProjectInfo(projectInfo)
        pass

    def getCurProjectInfo(self):
        return self.projectManagerWidget.getCurProjectInfo()

    def optionGroupModify(self, modifyOptionGroupInfo):
        LogUtil.i(TAG, "optionGroupModify", modifyOptionGroupInfo)
        if not modifyOptionGroupInfo:
            return
        projectInfo = self.getCurProjectInfo()
        projectId = DictUtil.get(projectInfo, KEY_ID)
        modules = self.projectManager.getProjectModules(projectId)
        ProjectManagerUtil.updateModulesInfoByOptionGroup(modifyOptionGroup=modifyOptionGroupInfo, modules=modules)
        self.projectManager.saveProjectModulesInfo(projectId, modules)
        self.moduleManagerWidget.setProjectInfo(projectInfo)
        pass

    def cmdGroupModify(self, modifyCmdGroupInfo):
        LogUtil.i(TAG, "cmdGroupModify", modifyCmdGroupInfo)
        if not modifyCmdGroupInfo:
            return
        projectInfo = self.getCurProjectInfo()
        projectId = DictUtil.get(projectInfo, KEY_ID)
        modules = self.projectManager.getProjectModules(projectId)
        ProjectManagerUtil.updateModulesInfoByCmdGroup(cmdOptionGroup=modifyCmdGroupInfo, modules=modules)
        self.projectManager.saveProjectModulesInfo(projectId, modules)
        self.moduleManagerWidget.setProjectInfo(projectInfo)
        pass

    def autoSelectedModulesFunc(self):
        LogUtil.i(TAG, "autoSelectedModulesFunc")

        pass

    def createProjectManageGroupBox(self):
        box = WidgetUtil.createGroupBox(self, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(self.projectManagerWidget, 2)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(self.moduleManagerWidget, 1)
        optionLayout = WidgetUtil.createVBoxLayout()
        optionLayout.addWidget(self.optionManagerWidget, 2)
        optionLayout.addWidget(self.cmdManagerWidget, 1)
        hbox.addLayout(optionLayout, 2)
        vbox.addLayout(hbox, 7)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.execBtn = WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.toggleExecute)
        hbox.addWidget(self.execBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def toggleExecute(self):
        execBtnTxt = self.execBtn.text().strip()
        if execBtnTxt == "开始执行":
            self.startExecute()
        else:
            self.stopExecCmd()
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
        self.execBtn.setText("停止执行")
        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.executeModuleCmd, args=(projectInfo, modules)).start()
        pass

    def stopExecCmd(self):
        threading.Thread(target=self.stopRun).start()
        LogUtil.d(TAG, "stopExecCmd")
        self.execBtn.setText("开始执行")
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
        self.updateModuleStatusSignal.emit(KEY_ALL, STATUS_HIDE)

        startTime = DateUtil.nowTimestamp(isMilliSecond=True)
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
                self.updateModuleStatusSignal.emit(processManager.getName(), STATUS_LOADING)
                self.futureList.append(future)
                allTasks.remove(ListUtil.find(allTasks, KEY_NAME, moduleInfo[KEY_NAME]))

        hasNewTaskAdd = True
        while len(self.futureList) < len(modules) or hasNewTaskAdd:
            hasNewTaskAdd = False
            for future in as_completed(self.futureList):
                try:
                    isSuccess, taskName, resultData = future.result()
                except CancelledError as err:
                    LogUtil.e(TAG, "CancelledError", err)
                    self.updateModuleStatusSignal.emit(KEY_ALL, STATUS_HIDE)
                    break
                if taskName in hasFinishedTasks:
                    continue
                self.updateModuleStatusSignal.emit(taskName, STATUS_SUCCESS if isSuccess else STATUS_FAILED)
                hasFinishedTasks.append(taskName)
                LogUtil.d(TAG, future, isSuccess, taskName, "hasFinishedTasks", hasFinishedTasks)
                copyAllTasks = copy.deepcopy(allTasks)
                for moduleInfo in copyAllTasks:
                    dependencies = DictUtil.get(moduleInfo, KEY_MODULE_DEPENDENCIES, [])
                    dependencyTasksAllFinished = ProjectManagerWindow.dependencyTasksAllFinished(dependencies,
                                                                                                 allExecuteModules,
                                                                                                 hasFinishedTasks)
                    if dependencyTasksAllFinished:
                        processManager = ListUtil.find(self.processManagers, KEY_NAME, moduleInfo[KEY_NAME])[
                            PROCESS_MANAGER]
                        future = self.executor.submit(processManager.run)
                        self.updateModuleStatusSignal.emit(processManager.getName(), STATUS_LOADING)
                        self.futureList.append(future)
                        hasNewTaskAdd = True
                        allTasks.remove(ListUtil.find(allTasks, KEY_NAME, moduleInfo[KEY_NAME]))

        allExecFinishedMsg = f"executeModuleCmd all finished. pid: {os.getpid()} costTime:{DateUtil.nowTimestamp(isMilliSecond=True) - startTime} ms\n"
        LogUtil.e(TAG, allExecFinishedMsg)
        self.standardOutputSignal.emit(allExecFinishedMsg)
        self.execBtn.setText("开始执行")
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
            self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="ProjectExecute_")
        except Exception as err:
            LogUtil.e(TAG, err)
        self.lock.release()
        LogUtil.d(TAG, "stopRun")
        pass

    def standardOutput(self, log):
        if "开始执行" in log or "执行结束" in log:
            WidgetUtil.textEditAppendMessage(self.consoleTextEdit, text=log, color='#000')
        else:
            WidgetUtil.textEditAppendMessage(self.consoleTextEdit, text=log)
        pass

    def standardError(self, log):
        WidgetUtil.textEditAppendMessage(self.consoleTextEdit, text=log, color='#f00')
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProjectManagerWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
