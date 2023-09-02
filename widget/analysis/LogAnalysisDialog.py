# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisDialog.py
# 定义一个LogAnalysisDialog类实现log分析相关功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "LogAnalysisDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'LogAnalysis'
KEY_LOG_FILE_PATH = 'logFilePath'


class LogAnalysisDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        LogAnalysisDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        LogAnalysisDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.35)
        LogUtil.d(TAG, "Init Log Analysis Dialog")
        self.setObjectName("LogAnalysisDialog")
        self.resize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        # self.setFixedSize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Log分析工具"))

        self.isDebug = isDebug
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.logFilePath = self.operaIni.getValue(KEY_LOG_FILE_PATH, KEY_SECTION)

        self.loadingDialog = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        extractLogGroupBox = self.createExtractLogGroupBox(self)

        vLayout.addWidget(extractLogGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        self.hideLoadingSignal.connect(self.hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass

    def createExtractLogGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="日志分析")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="提取Log文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.extractLogFile)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.logFilePath if self.logFilePath else '',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="分析", onClicked=self.extractLog))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def extractLogFile(self):
        from ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog(self.isDebug)
        pass

    def getLogFilePath(self):
        fp = ''
        if self.logFilePath:
            fp, _ = os.path.split(self.logFilePath)

        fp = WidgetUtil.getOpenFileName(caption='请选择要分析的Log文件',
                                        directory=fp)
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def extractLog(self):
        self.logFilePath = self.logFilePathLineEdit.text().strip()
        if not self.logFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return

        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_PATH, self.logFilePath)
        self.operaIni.saveIni()

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
    window = LogAnalysisDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
