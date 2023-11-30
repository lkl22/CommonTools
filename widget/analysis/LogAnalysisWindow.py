# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisWindow.py
# 定义一个LogAnalysisWindow类实现log分析相关功能
import threading
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from constant.ColorEnum import ColorEnum
from util.DateUtil import DateUtil
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.EvalUtil import EvalUtil
from util.ListUtil import ListUtil
from util.NetworkUtil import NetworkUtil
from util.OperaIni import *
from util.PlantUml import PlantUML
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
        self.spliceLogResult = {}
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

        self.consoleTextEdit = CommonTextEdit(linkClicked=self.__linkClicked)
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
            self.__appendLog(f'{self.categoryRule[KEY_FILE_PATH]} file not exist.', ColorEnum.RED)
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
                    self.__appendLog(line)
            self.__analysisLogTransform(line, rule)
            self.__analysisCostTime(line, rule, timeIndex, timeFormat)
            self.__spliceLog(line, rule, timeIndex, timeFormat)
        pass

    def __spliceLog(self, line, rule, timeIndex, timeFormat):
        if not DictUtil.get(rule, KEY_NEED_SPLICE_LOG, DEFAULT_VALUE_NEED_SPLICE_LOG):
            return
        spliceParams = DictUtil.get(rule, KEY_SPLICE_PARAMS)
        if not spliceParams:
            return
        startKeyword = DictUtil.get(spliceParams, KEY_START_LOG_KEYWORD)
        splitRe = DictUtil.get(spliceParams, KEY_SPLIT_RE)
        if not startKeyword or not splitRe:
            return
        endKeyword = DictUtil.get(spliceParams, KEY_END_LOG_KEYWORD)
        time = self.__getLogTime(line, timeIndex, timeFormat)
        if startKeyword in line:
            if endKeyword and endKeyword in line:
                self.spliceLogResult[rule[KEY_NAME]] = [
                    f"{line[line.index(startKeyword):line.index(endKeyword)]}{endKeyword}"]
                self.__handleSpliceLog(rule, spliceParams, time)
                return
            self.spliceLogResult[rule[KEY_NAME]] = [line[line.index(startKeyword):].rstrip()]
            return
        if not DictUtil.get(self.spliceLogResult, rule[KEY_NAME]):
            return
        if endKeyword and endKeyword in line:
            if ReUtil.match(line, f'.*{splitRe}.*'):
                log = re.split(splitRe, line)[1]
                if endKeyword in log:
                    log = log[:log.index(endKeyword)] + endKeyword
                self.__cacheSliceLog(rule, log)
            else:
                self.__cacheSliceLog(rule, line[:line.index(endKeyword)] + endKeyword)
            self.__handleSpliceLog(rule, spliceParams, time)
            return
        elif ReUtil.match(line, f'.*{splitRe}.*'):
            self.__cacheSliceLog(rule, re.split(splitRe, line)[1].rstrip())
        else:
            self.__handleSpliceLog(rule, spliceParams, time)
        pass

    def __cacheSliceLog(self, rule, log):
        self.spliceLogResult[rule[KEY_NAME]].append(log)
        pass

    def __handleSpliceLog(self, rule, spliceParams, time):
        log = ''.join([f"{item} " if item.endswith('state') else item for item in self.spliceLogResult[rule[KEY_NAME]]])
        func = DictUtil.get(spliceParams, KEY_FUNCTION)
        if func:
            log = EvalUtil.execFunc(func, log)
        enableUml = DictUtil.get(spliceParams, KEY_ENABLE_UML_TRANSFORM, False)
        if enableUml:
            timeStr = DateUtil.nowTime("%Y%m%d%H%M%S")
            if time:
                timeStr = f"{time[0].toString('MM-dd HH:mm:ss')}.{time[1]} "
            fp, err = PlantUML.jarProcesses(log,
                                            outfile=f'{timeStr.replace("-", "").replace(" ", "").replace(":", "")}',
                                            directory='outputPic')
            LogUtil.w(TAG, f'gen uml pic: {fp}')
            self.__appendLog(f"{rule[KEY_NAME]}: \n{log}", ColorEnum.BLUE)
            if fp:
                self.__appendLog(f'{timeStr}{rule[KEY_NAME]}: <a style="color: red" href="{fp}">{fp}</a>', ColorEnum.BLUE)
                self.__appendLog('\n')
            else:
                self.__appendLog(f"\n{rule[KEY_NAME]}: \n{err}\n", ColorEnum.RED)
        else:
            self.__appendLog(f"{rule[KEY_NAME]}: \n{log}\n", ColorEnum.BLUE)
        self.spliceLogResult[rule[KEY_NAME]] = []
        pass

    def __analysisLogTransform(self, line, rule):
        if not DictUtil.get(rule, KEY_NEED_LOG_TRANSFORM, DEFAULT_VALUE_NEED_LOG_TRANSFORM):
            return
        transformCfgs = DictUtil.get(rule, KEY_TRANSFORM_CFGS)
        if not transformCfgs:
            return
        keywords = DictUtil.get(transformCfgs, KEY_LOG_KEYWORD)
        function = DictUtil.get(transformCfgs, KEY_FUNCTION)
        if not keywords or not function:
            return
        keywordList = [item for item in keywords.split(';') if item and item in line]
        if not keywordList:
            return
        self.__appendLog(f"原始日志: {line}", ColorEnum.BLUE)
        dicRes = EvalUtil.execFunc(function, line)
        if type(dicRes) != dict:
            self.__appendLog(f"转换结果: {dicRes}\n", ColorEnum.OCEAN_BLUE)
            return
        funcs = DictUtil.get(transformCfgs, KEY_TRANSFORM_FUNCS)
        self.__appendLog(f"转换结果: {dicRes}", ColorEnum.OCEAN_BLUE)
        if not funcs:
            return
        for func in funcs:
            value = DictUtil.get(dicRes, func[KEY_ITEM_KEY])
            if value:
                execResult = EvalUtil.execFunc(func[KEY_FUNCTION], value)
                self.__appendLog(f"转换结果: {execResult}", ColorEnum.OCEAN_BLUE)
        pass

    def __appendLog(self, log: str, color: ColorEnum = ColorEnum.BLACK):
        self.execResult.append({KEY_LOG: log, KEY_COLOR: color.value})
        if len(self.execResult) > 50:
            res = self.execResult
            self.execResult = []
            self.consoleTextEdit.standardOutput(res)

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
            self.__appendLog(f"{startInfo[KEY_LOG]}{line[:MAX_BYTE]}")
            costTime = startTime[0].msecsTo(endTime[0]) + endTime[1] - startTime[1]
            self.__appendLog(f"\n耗时分析：{rule[KEY_NAME]}({DictUtil.get(rule, KEY_DESC, '')}) cost time: {costTime} ms\n",
                             ColorEnum.ORANGE)
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

    def __linkClicked(self, linkTxt):
        if NetworkUtil.isUrl(linkTxt):
            NetworkUtil.openWebBrowser(linkTxt)
        else:
            FileUtil.openFile(linkTxt)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
