# -*- coding: utf-8 -*-
# python 3.x
# Filename: FindFileContentWindow.py
# 定义一个FindFileContentWindow类实现批量查找文件内容功能
from PyQt5.QtCore import QModelIndex, pyqtSignal
from PyQt5.QtWidgets import QAbstractItemView, QMainWindow

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from util.ReUtil import ReUtil
from widget.custom.DragInputWidget import DragInputWidget
from widget.findFileContent.AddOrEditConfigDialog import AddOrEditConfigDialog
from widget.findFileContent.FindFileContentManager import *
from widget.findFileContent.FindFileContentUtil import FindFileContentUtil

TAG = "FindFileContentWindow"


class FindFileContentWindow(QMainWindow):
    windowList = []
    updateProgressSignal = pyqtSignal(str, str)
    updateStatusBarSignal = pyqtSignal(str)

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        FindFileContentWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        FindFileContentWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "FindFileContentWindow")
        self.setWindowTitle(WidgetUtil.translate(text="批量查找文件中包含的指定内容"))

        self.setObjectName("FindFileContentWindow")
        self.resize(FindFileContentWindow.WINDOW_WIDTH, FindFileContentWindow.WINDOW_HEIGHT)
        # self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)

        self.isDebug = isDebug
        self.manager = FindFileContentManager(isDebug=isDebug)
        self.configs = self.manager.configs
        self.path = self.manager.path
        if not self.configs:
            self.configs = {KEY_DEFAULT: None, KEY_LIST: []}
        self.defaultName = DictUtil.get(self.configs, KEY_DEFAULT, "")
        self.configList = DictUtil.get(self.configs, KEY_LIST, [])
        self.curConfigInfo = ListUtil.find(self.configList, KEY_NAME, self.defaultName)
        if not self.curConfigInfo:
            self.curConfigInfo = {}

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        vLayout = WidgetUtil.createVBoxLayout(layoutWidget, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setCentralWidget(layoutWidget)
        layoutWidget.setLayout(vLayout)

        self.managerGroupBox = self.createManagerGroupBox(self)
        vLayout.addWidget(self.managerGroupBox)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        vLayout.addWidget(self.consoleTextEdit, 1)
        self.statusBar().showMessage("状态栏")
        self.updateProgressSignal.connect(self.standardOutput)
        self.updateStatusBarSignal.connect(self.statusBarShowMessage)
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

    def createManagerGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        labelWidth = 120
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择配置：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.configsComboBox = WidgetUtil.createComboBox(box, activated=self.configIndexChanged)
        self.updateConfigComboBox()
        hbox.addWidget(self.configsComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Add", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.addConfig))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Edit", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.editConfig))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="del", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.delConfig))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="工程路径：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.pathInputWidget = DragInputWidget(
            text=self.path,
            dirParam=["请选择您的工作目录", "./"], isReadOnly=True,
            holderText="请拖动您的工作目录到此框或者点击右侧的按钮选择您的工作路径",
            textChanged=self.pathChanged)
        hbox.addWidget(self.pathInputWidget)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.startExec))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def updateConfigComboBox(self):
        self.configsComboBox.clear()
        if self.configList:
            for index, item in enumerate(self.configList):
                self.configsComboBox.addItem(f"{item[KEY_NAME]}（{item[KEY_DESC]}）", item)
            if not self.curConfigInfo:
                self.curConfigInfo = self.configList[0]
            self.configsComboBox.setCurrentText(f"{self.curConfigInfo[KEY_NAME]}（{self.curConfigInfo[KEY_DESC]}）")
            LogUtil.d(TAG, 'updateConfigComboBox setCurrentText', self.curConfigInfo)
        pass

    def configIndexChanged(self, index):
        configInfo = self.configsComboBox.currentData()
        if configInfo:
            self.curConfigInfo = configInfo
        LogUtil.d(TAG, 'configIndexChanged', index, self.curConfigInfo, configInfo)
        self.updateConfigInfo()
        pass

    def addConfig(self):
        LogUtil.d(TAG, "addConfig")
        AddOrEditConfigDialog(configList=self.configs[KEY_LIST], callback=self.addOrEditConfigCallback, isDebug=self.isDebug).show()
        pass

    def editConfig(self):
        LogUtil.d(TAG, "editConfig")
        AddOrEditConfigDialog(default=self.curConfigInfo, configList=self.configs[KEY_LIST],
                              callback=self.addOrEditConfigCallback, isDebug=self.isDebug).show()
        pass

    def delConfig(self):
        LogUtil.d(TAG, "delConfig")
        if not self.curConfigInfo:
            WidgetUtil.showErrorDialog(message=f"当前没有选中任何配置。")
            return
        name = self.curConfigInfo[KEY_NAME]
        LogUtil.i(TAG, f"delMatch {name}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{name}</span> 吗？",
                                      acceptFunc=self.delConfigItem)
        pass

    def delConfigItem(self):
        LogUtil.d(TAG, "delConfigItem")
        ListUtil.remove(self.configList, self.curConfigInfo)
        self.curConfigInfo = {}
        self.updateConfigComboBox()
        self.updateConfigInfo()
        pass

    def addOrEditConfigCallback(self, info):
        LogUtil.d(TAG, "addOrEditConfigCallback", info)
        if info:
            self.configList.append(info)
        self.configList = sorted(self.configList, key=lambda x: x[KEY_NAME])
        self.updateConfigComboBox()
        self.updateConfigInfo()
        pass

    def updateConfigInfo(self):
        self.configs[KEY_DEFAULT] = DictUtil.get(self.curConfigInfo, KEY_NAME)
        self.configs[KEY_LIST] = self.configList
        self.manager.saveConfigInfos(self.configs)
        pass

    def pathChanged(self, fp):
        LogUtil.d(TAG, "pathChanged", fp)
        self.path = fp
        self.manager.savePath(fp)
        pass

    def startExec(self):
        LogUtil.i(TAG, "startExec")
        if not self.path:
            WidgetUtil.showErrorDialog(message="请先选择您的工作目录。")
            return
        if not self.curConfigInfo:
            WidgetUtil.showErrorDialog(message="请先选择一个配置项。")
            return

        self.consoleTextEdit.clear()
        fileList = FindFileContentUtil.findFileList(fp=self.path, configInfo=self.curConfigInfo)
        LogUtil.d(TAG, "startExec fileList", fileList)

        patternList = FindFileContentUtil.getPatternList(configInfo=self.curConfigInfo)
        LogUtil.d(TAG, "startExec patternList", patternList)

        FindFileContentUtil.findFileContent(fileList=fileList, patternList=patternList,
                                            statusCallback=self.statusMsgCallback,
                                            resCallback=self.findResCallback)
        self.updateStatusBarSignal.emit("处理完成")
        pass

    def statusMsgCallback(self, msg):
        LogUtil.i(TAG, "statusMsgCallback", msg)
        self.updateStatusBarSignal.emit(msg)
        pass

    def findResCallback(self, fp, matchContents):
        LogUtil.i(TAG, "findResCallback", fp, matchContents)
        self.updateProgressSignal.emit(f"查找文件：{fp}", "#00F")
        self.updateProgressSignal.emit(f"包含的字符：", "#F0F")
        for matchContent in matchContents:
            self.updateProgressSignal.emit(f"{str(matchContent)}", "#F00")
        self.updateProgressSignal.emit(f"", "#F00")
        pass

    def statusBarShowMessage(self, msg):
        self.statusBar().showMessage(msg)

    def standardOutput(self, log, color):
        WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log, color=color)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FindFileContentWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
