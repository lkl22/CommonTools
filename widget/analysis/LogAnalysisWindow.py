# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisWindow.py
# 定义一个LogAnalysisWindow类实现log分析相关功能
import threading
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.EvalUtil import EvalUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from util.StrUtil import StrUtil
from widget.analysis.CategoryConfigWidget import CategoryConfigWidget
from widget.analysis.CategoryManagerWidget import CategoryManagerWidget
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.LoadingDialog import LoadingDialog

TAG = "LogAnalysisWindow"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'
MAX_BYTE = 200


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
        self.categoryInfo = None
        self.costTimeResult = {}
        self.execResult = []

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

        self.consoleTextEdit = CommonTextEdit()
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
        self.costTimeResult.clear()
        self.execResult.clear()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.__execAnalysisLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog()
        pass

    def __execAnalysisLog(self):
        LogUtil.d(TAG, '__execAnalysisLog start', self.categoryRule)
        if FileUtil.existsFile(self.categoryRule[KEY_FILE_PATH]):
            srcFile = open(self.categoryRule[KEY_FILE_PATH], 'rb')
            timeIndex = self.categoryRule[KEY_DATETIME_FORMAT_RULE][KEY_START_INDEX]
            timeFormat = self.categoryRule[KEY_DATETIME_FORMAT_RULE][KEY_DATETIME_FORMAT]
            typeInfo = ListUtil.find(self.categoryRule[KEY_TYPE_LIST], KEY_NAME, self.categoryRule[KEY_DEFAULT_TYPE])
            ruleList = ListUtil.filter(typeInfo[KEY_ANALYSIS_RULES], KEY_IS_ENABLE, True,
                                       DEFAULT_VALUE_IS_ENABLE)
            line = StrUtil.decode(srcFile.readline())
            while line:
                self.__analysisLogByLine(line, ruleList, timeIndex, timeFormat)
                line = StrUtil.decode(srcFile.readline())
            srcFile.close()
        else:
            self.execResult.append({KEY_LOG: f'{self.categoryRule[KEY_FILE_PATH]} file not exist.', KEY_COLOR: '#f00'})
        self.consoleTextEdit.standardOutput(self.execResult)
        self.hideLoadingSignal.emit()
        pass

    def __analysisLogByLine(self, line, ruleList, timeIndex, timeFormat):
        hasPrintLine = False
        for rule in ruleList:
            logKeyword = DictUtil.get(rule, KEY_LOG_KEYWORD, '')
            if logKeyword and logKeyword in line:
                if not hasPrintLine:
                    hasPrintLine = True
                    self.execResult.append({KEY_LOG: line, KEY_COLOR: '#000'})
                self.__analysisLogMap(line, rule)
                self.execResult.append({KEY_LOG: '\n', KEY_COLOR: '#000'})
            self.__analysisCostTime(line, rule, timeIndex, timeFormat)
        pass

    def __analysisLogMap(self, line, rule):
        if not DictUtil.get(rule, KEY_NEED_LOG_MAP, DEFAULT_VALUE_NEED_LOG_MAP):
            return
        logMapRules = ListUtil.filter(DictUtil.get(rule, KEY_RESULT_MAP), KEY_IS_ENABLE, True, DEFAULT_VALUE_IS_ENABLE)
        for rule in logMapRules:
            if DictUtil.get(rule, KEY_IS_FUNCTION, DEFAULT_VALUE_IS_FUNCTION):
                myLocals = {'text': line, 'res': ''}
                execResult = EvalUtil.exec(rule[KEY_MAP_TXT], locals=myLocals)
                res = myLocals['res'] + (str(execResult) if execResult else '')
                self.execResult.append({KEY_LOG: f"mapResult: {res}\n", KEY_COLOR: '#f0f'})
            elif rule[KEY_SRC_LOG] in line:
                self.execResult.append({KEY_LOG: f"mapResult: {rule[KEY_MAP_TXT]}\n", KEY_COLOR: '#f0f'})
        pass

    def __analysisCostTime(self, line, rule, timeIndex, timeFormat):
        if not DictUtil.get(rule, KEY_NEED_COST_TIME, DEFAULT_VALUE_NEED_COST_TIME):
            return
        startKeyword = DictUtil.get(rule, KEY_START_LOG_KEYWORD, '')
        endKeyword = DictUtil.get(rule, KEY_END_LOG_KEYWORD, '')
        if startKeyword in line:
            startTime = self.__getLogTime(line, timeIndex, timeFormat)
            self.costTimeResult[rule[KEY_NAME]] = {KEY_TIME: startTime, KEY_LOG: line}
        elif endKeyword in line:
            startInfo = DictUtil.get(self.costTimeResult, rule[KEY_NAME], None)
            if not startInfo:
                return
            startTime = startInfo[KEY_TIME]
            if not startTime:
                return
            endTime = self.__getLogTime(line, timeIndex, timeFormat)
            if not endTime:
                return
            self.execResult.append({KEY_LOG: f"{startInfo[KEY_LOG]}{line[:MAX_BYTE]}", KEY_COLOR: '#000'})
            costTime = startTime[0].msecsTo(endTime[0]) + endTime[1] - startTime[1]
            self.execResult.append(
                {KEY_LOG: f"\n耗时分析：{rule[KEY_NAME]}({DictUtil.get(rule, KEY_DESC, '')}) cost time: {costTime} ms\n\n",
                 KEY_COLOR: '#f00'})
        pass

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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
