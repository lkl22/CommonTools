# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisWindow.py
# 定义一个LogAnalysisWindow类实现log分析相关功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from util.DialogUtil import *
from util.OperaIni import *
from widget.analysis.CategoryConfigWidget import CategoryConfigWidget
from widget.analysis.CategoryManagerWidget import CategoryManagerWidget
from widget.analysis.LogAnalysisManager import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "LogAnalysisWindow"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'LogAnalysis'
KEY_LOG_FILE_PATH = 'logFilePath'


class LogAnalysisWindow(QMainWindow):
    windowList = []
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        LogAnalysisWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        LogAnalysisWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init Log Analysis Window")
        self.setObjectName("LogAnalysisWindow")
        self.resize(LogAnalysisWindow.WINDOW_WIDTH, LogAnalysisWindow.WINDOW_HEIGHT)
        # self.setFixedSize(LogAnalysisWindow.WINDOW_WIDTH, LogAnalysisWindow.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Log分析工具"))

        self.isDebug = isDebug
        self.analysisManager = LogAnalysisManager(isDebug)
        self.loadingDialog = None

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.categoryManagerWidget = CategoryManagerWidget(analysisManager=self.analysisManager,
                                                           modifyCallback=self.categoryModify)

        self.categoryConfigWidget = CategoryConfigWidget(analysisManager=self.analysisManager,
                                                         isDebug=isDebug)

        self.categoryManageGroupBox = self.createCategoryManageGroupBox()
        hLayout.addWidget(self.categoryManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        self.hideLoadingSignal.connect(self.hideLoading)

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

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass

    def createCategoryManageGroupBox(self):
        box = WidgetUtil.createGroupBox(self, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(self.categoryManagerWidget)
        vbox.addWidget(self.categoryConfigWidget, 7)
        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.execBtn = WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.extractLog)
        hbox.addWidget(self.execBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def categoryModify(self):
        LogUtil.d(TAG, "categoryModify")

        pass

    def extractLog(self):
        self.logFilePath = self.logFilePathLineEdit.text().strip()
        if not self.logFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def execExtractLog(self):
        LogUtil.d(TAG, 'execExtractLog start.')

        self.hideLoadingSignal.emit()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
