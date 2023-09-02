# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisWindow.py
# 定义一个LogAnalysisWindow类实现log分析相关功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from util.DialogUtil import *
from util.DictUtil import DictUtil
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
    standardOutputSignal = pyqtSignal(str)

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
        self.categoryInfo = None
        self.analysisResult = {}

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.categoryConfigWidget = CategoryConfigWidget(analysisManager=self.analysisManager,
                                                         isDebug=isDebug)

        self.categoryManagerWidget = CategoryManagerWidget(analysisManager=self.analysisManager,
                                                           modifyCallback=self.__categoryModify)

        self.categoryManageGroupBox = self.createCategoryManageGroupBox()
        hLayout.addWidget(self.categoryManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        self.hideLoadingSignal.connect(self.hideLoading)
        self.standardOutputSignal.connect(self.__standardOutput)

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
        self.execBtn = WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.__analysisLog)
        hbox.addWidget(self.execBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def __categoryModify(self, categoryInfo):
        LogUtil.d(TAG, "__categoryModify", categoryInfo)
        self.categoryInfo = categoryInfo
        self.categoryConfigWidget.setCategoryInfo(categoryInfo)
        pass

    def __analysisLog(self):
        if not self.categoryInfo:
            WidgetUtil.showErrorDialog(message="请先选择或者添加Log分析配置")
            return
        self.categoryRule = self.categoryConfigWidget.getCategoryRule()
        if not self.categoryRule:
            return

        categoryId = DictUtil.get(self.categoryInfo, KEY_ID)
        self.analysisManager.saveCategoryRuleById(categoryId, self.categoryRule)

        self.consoleTextEdit.clear()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.__execAnalysisLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def __execAnalysisLog(self):
        LogUtil.d(TAG, '__execAnalysisLog start', self.categoryRule)
        srcFile = open(self.categoryRule[KEY_FILE_PATH], 'r')
        ruleList = self.categoryRule[KEY_ANALYSIS_RULES]
        timeIndex = self.categoryRule[KEY_LOG_TIME_INDEX]
        timeFormat = self.categoryRule[KEY_LOG_TIME_FORMAT]
        ruleList = self.categoryRule[KEY_ANALYSIS_RULES]
        # keywords = list(rule[KEY_LOG_KEYWORD] for rule in ruleList)
        line = srcFile.readline()
        while line:
            self.__analysisLogByLine(line, ruleList, timeIndex, timeFormat)
            try:
                line = srcFile.readline()
            except Exception as ex:
                LogUtil.e("invalid line：{} \nex: {}".format(line, ex))

        srcFile.close()
        self.hideLoadingSignal.emit()
        pass

    def __analysisLogByLine(self, line, ruleList, timeIndex, timeFormat):
        for rule in ruleList:
            logKeyword = DictUtil.get(rule, KEY_LOG_KEYWORD, '')
            if logKeyword and logKeyword in line:
                self.__standardOutput(line)
            if DictUtil.get(rule, KEY_NEED_COST_TIME, DEFAULT_VALUE_NEED_COST_TIME):
                startKeyword = DictUtil.get(rule, KEY_START_LOG_KEYWORD, '')
                endKeyword = DictUtil.get(rule, KEY_END_LOG_KEYWORD, '')
                if startKeyword in line:
                    startTime = self.__getLogTime(line, timeIndex, timeFormat)
                    self.analysisResult[rule[KEY_NAME]] = {'time': startTime, 'log': line}
                elif endKeyword in line:
                    startInfo = DictUtil.get(self.analysisResult, rule[KEY_NAME], None)
                    if not startInfo:
                        continue
                    startTime = startInfo['time']
                    if startTime:
                        endTime = self.__getLogTime(line, timeIndex, timeFormat)
                        if not endTime:
                            continue
                        self.__standardOutput(
                            f"{startInfo['log']}{line}cost time: {endTime[0].msecsTo(startTime[0]) * 1000 + endTime[1] - startTime[1]} ms\n",
                            '#f00')

    def __getLogTime(self, line, timeIndex, timeFormat: str):
        try:
            if 'SSS' in timeFormat:
                endIndex = timeIndex + len(timeFormat)
                time = QDateTime.fromString(line[timeIndex:endIndex - 3], timeFormat.replace('SSS', ''))
                return time, int(line[endIndex - 3: endIndex])
            else:
                return QDateTime.fromString(line[timeIndex:timeIndex + len(timeFormat)], timeFormat), 0
        except Exception as e:
            LogUtil.e(TAG, '__getLogTime 错误信息：', e)
            return None

    def __standardOutput(self, log, color='#00f'):
        WidgetUtil.appendTextEdit(self.consoleTextEdit, text=log, color=color)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
