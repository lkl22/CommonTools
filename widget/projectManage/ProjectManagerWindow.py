# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManagerDialog.py
# 定义一个ProjectManagerDialog类实现项目管理功能
from util.DialogUtil import *
from util.OperaIni import *
from util.PlatformUtil import PlatformUtil
from util.WidgetUtil import *
from PyQt5.QtWidgets import *
from widget.projectManage.AddOrEditProjectDialog import AddOrEditProjectDialog


class ProjectManagerWindow(QMainWindow):
    windowList = []

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

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)

        hLayout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.projectManageGroupBox = self.createProjectManageGroupBox(self)
        hLayout.addWidget(self.projectManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

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
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / (3 if PlatformUtil.isMac() else 2))
        pass

    def createProjectManageGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        vbox.addWidget(self.createMainModuleGroupBox(box))

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def createMainModuleGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="主工程配置")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择工程："))
        self.projectComboBox = WidgetUtil.createComboBox(box, activated=self.projectIndexChanged)
        hbox.addWidget(self.projectComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Add", toolTip="添加新项目", onClicked=self.addProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Modify", toolTip="修改项目配置", onClicked=self.modifyProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Del", toolTip="删除项目", onClicked=self.delProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Save As", toolTip="导出该项目配置", onClicked=self.saveAsProject))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Import", toolTip="导入项目配置", onClicked=self.importProject))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box, text="项目配置信息："))

        self.projectConfigInfo = WidgetUtil.createTextEdit(box, isReadOnly=True)
        vbox.addWidget(self.projectConfigInfo)

        box.setFixedHeight(int(ProjectManagerWindow.WINDOW_HEIGHT * 0.2))
        return box

    def projectIndexChanged(self):
        LogUtil.d("projectIndexChanged")
        pass

    def addProject(self):
        LogUtil.d("addProject")
        AddOrEditProjectDialog()
        pass

    def modifyProject(self):
        LogUtil.d("modifyProject")
        pass

    def delProject(self):
        LogUtil.d("delProject")
        pass

    def saveAsProject(self):
        LogUtil.d("saveAsProject")
        pass

    def importProject(self):
        LogUtil.d("importProject")
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProjectManagerWindow(isDebug=True)
    window.center()
    window.show()
    sys.exit(app.exec_())
