# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManagerDialog.py
# 定义一个ProjectManagerDialog类实现项目管理功能
import threading
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtCore import pyqtSignal
from util.DictUtil import DictUtil
from util.OperaIni import *
from util.PlatformUtil import PlatformUtil
from util.ProcessManager import ProcessManager
from util.WidgetUtil import *
from PyQt5.QtWidgets import *

from widget.custom.LoadingDialog import LoadingDialog
from widget.projectManage.AddOrEditProjectDialog import AddOrEditProjectDialog
from widget.projectManage.ModuleManagerWidget import ModuleManagerWidget
from widget.projectManage.OptionManagerWidget import OptionManagerWidget
from widget.projectManage.ProjectManager import *

TYPE_HIDE_LOADING_DIALOG = 1


class ProjectManagerWindow(QMainWindow):
    windowList = []
    execUi = pyqtSignal(int)

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        ProjectManagerWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.9)
        ProjectManagerWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.8)
        LogUtil.d("Project Manage Window")
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

        self.moduleManagerWidget = ModuleManagerWidget(projectManager=self.projectManager)
        self.optionManagerWidget = OptionManagerWidget(projectManager=self.projectManager)
        self.loadingDialog = LoadingDialog(showText="正在执行。。。", btnText="终止",
                                           rejectedFunc=lambda: LogUtil.d("close loading"), isDebug=self.isDebug)
        self.loadingDialog.hide()

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
        if type == TYPE_HIDE_LOADING_DIALOG:
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

    def center(self):  # 主窗口居中显示函数
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2),
                  int((screen.height() - size.height()) / (3 if PlatformUtil.isMac() else 2)))
        pass

    def createProjectManageGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(self.createMainModuleGroupBox(box))

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(self.moduleManagerWidget, 1)
        hbox.addWidget(self.optionManagerWidget, 2)
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
            evnDesc = "<span style='color:green;'>环境变量：</span><br/>"
            for item in evnList:
                evnDesc += f"<span style='color:red;'>变量名：{item[KEY_NAME]}<br/>变量值：{item[KEY_VALUE]}</span><br/>" \
                           f"是否是Path环境变量：{item[KEY_EVN_IS_PATH]}<br/>描述：{item[KEY_DESC]}<br/><br/>"

        desc = f"<span style='color:green;'>工程路径：<br/></span><span style='color:red;'>{projectInfo[KEY_PATH]}</span>" \
               f"<br/><br/>{evnDesc}"
        return desc

    def updateProjectDesc(self):
        projectInfo = self.getCurProjectInfo()
        self.moduleManagerWidget.setProjectInfo(projectInfo)
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
            LogUtil.d('updateFlavorComboBox setCurrentText', curProjectInfo[KEY_NAME])
        else:
            self.projectComboBox.clear()
            self.curProjectIndex = -1
            self.updateProjectDesc()
            LogUtil.d("no project")
        pass

    def projectIndexChanged(self, index):
        LogUtil.d('projectIndexChanged', index)
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
        LogUtil.d("addProject")
        AddOrEditProjectDialog(callback=self.addOrEditProjectCallback)
        pass

    def modifyProject(self):
        LogUtil.d("modifyProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return
        AddOrEditProjectDialog(callback=self.addOrEditProjectCallback,
                               projectInfo=self.projects[KEY_LIST][self.curProjectIndex], projectList=self.projects)
        pass

    def addOrEditProjectCallback(self, info):
        LogUtil.d("addOrEditProjectCallback", info)
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
        LogUtil.d("delProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return
        projectInfo = self.getCurProjectInfo()
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{projectInfo[KEY_NAME]}（{projectInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=self.delProjectItem)
        pass

    def delProjectItem(self):
        LogUtil.i("delProjectItem")
        curProjectInfo = self.getCurProjectInfo()
        self.projects[KEY_LIST].remove(curProjectInfo)
        self.curProjectIndex = -1
        self.updateProjectComboBox()
        self.projectManager.delProjectInfoById(curProjectInfo[KEY_ID])
        self.saveProjects()
        pass

    def saveAsProject(self):
        LogUtil.d("saveAsProject")
        if self.curProjectIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个工程")
            return
        pass

    def importProject(self):
        LogUtil.d("importProject")
        pass

    def startExecute(self):
        LogUtil.d(f"startExecute main pid: {os.getpid()} threadId: {threading.currentThread().ident}")
        projectInfo = self.getCurProjectInfo()
        if not projectInfo:
            WidgetUtil.showAboutDialog(text="请先添加/选择一个工程")
            return
        modules = self.moduleManagerWidget.getSelectedModules()
        if not modules:
            WidgetUtil.showAboutDialog(text="请先添加/选择一个模块")
            return
        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.executeModuleCmd, args=(projectInfo, modules)).start()
        self.loadingDialog.show()
        pass

    def executeModuleCmd(self, projectInfo, modules):
        self.futureList.clear()
        self.processManagers.clear()
        LogUtil.e(f"executeModuleCmd start. pid: {os.getpid()} threadId: {threading.currentThread().ident}")
        for moduleInfo in modules:
            processManager = ProcessManager(name=DictUtil.get(moduleInfo, KEY_NAME),
                                            cmdList=DictUtil.get(moduleInfo, KEY_CMD_LIST, []),
                                            workingDir=DictUtil.get(moduleInfo, KEY_PATH,
                                                                    DictUtil.get(projectInfo, KEY_PATH)),
                                            standardOutput=self.standardOutput,
                                            standardError=self.standardError)
            self.processManagers.append(processManager)
            future = self.executor.submit(processManager.run)
            self.futureList.append(future)

        for future in as_completed(self.futureList):
            data = future.result()
            LogUtil.d(future, data)
        LogUtil.e(f"executeModuleCmd all finished. pid: {os.getpid()}")
        self.execUi.emit(TYPE_HIDE_LOADING_DIALOG)
        pass

    def standardOutput(self, log):
        WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log)
        pass

    def standardError(self, log):
        WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log, color='#f00')
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProjectManagerWindow(isDebug=True)
    window.center()
    window.show()
    sys.exit(app.exec_())
