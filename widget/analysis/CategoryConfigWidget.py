# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryConfigWidget.py
# 定义一个CategoryConfigWidget窗口类实现日志分析分类配置信息管理
import copy
from PyQt5.QtWidgets import QFrame
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.analysis.AddOrEditAnalysisCfgDialog import AddOrEditAnalysisCfgDialog
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonDateTimeFormatEdit import CommonDateTimeFormatEdit
from widget.custom.CommonTableView import CommonTableView
from widget.custom.DragInputWidget import DragInputWidget

TAG = "CategoryConfigWidget"
HEADERS = {
    KEY_NAME: {KEY_TITLE: "规则名"}, KEY_DESC: {KEY_TITLE: "规则描述"}, KEY_LOG_KEYWORD: {KEY_TITLE: "日志关键字"},
    KEY_IS_ENABLE: {KEY_TITLE: "Enable", KEY_DEFAULT: DEFAULT_VALUE_IS_ENABLE},
    KEY_NEED_COST_TIME: {KEY_TITLE: "统计耗时", KEY_DEFAULT: DEFAULT_VALUE_NEED_COST_TIME},
    KEY_START_LOG_KEYWORD: {KEY_TITLE: "开始日志关键字"}, KEY_END_LOG_KEYWORD: {KEY_TITLE: "结束日志关键字"},
    KEY_NEED_LOG_MAP: {KEY_TITLE: "结果映射", KEY_DEFAULT: DEFAULT_VALUE_NEED_LOG_MAP}, KEY_RESULT_MAP: {KEY_TITLE: "映射规则"}
}


class CategoryConfigWidget(QFrame):
    def __init__(self, analysisManager: LogAnalysisManager, isDebug=False):
        super(CategoryConfigWidget, self).__init__()
        self.setObjectName(TAG)
        self.setToolTip("日志分析配置信息管理")

        self.__analysisManager = analysisManager
        self.__categoryInfo = None
        self.__categoryRuleInfo = None
        self.__ruleList = []
        self.__logFilePath = None
        self.__datetimeFormatRule = None
        self.__isDebug = isDebug

        widgetLayout = WidgetUtil.createVBoxLayout()
        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)

        labelMinSize = QSize(120, const.HEIGHT)
        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="筛选指定日期范围Log文件", minSize=labelMinSize,
                                    toolTip='从指定目录下筛选指定日期范围的Log压缩文件，解压并合并到一个文件中',
                                    onClicked=self.__extractMergeLogFile)
        WidgetUtil.createPushButton(splitter, text="提取Log日志到指定文件", minSize=labelMinSize,
                                    toolTip='从指定Log文件中提取指定日期范围到Log到目标文件',
                                    onClicked=self.__extractLogFile)
        vbox.addWidget(splitter)

        self.__logFilePathWidget = DragInputWidget(label='日志文件路径',
                                                   fileParam={KEY_CAPTION: '要分析的日志文件'},
                                                   labelMinSize=labelMinSize,
                                                   toolTip='选择要分析的日志文件')
        vbox.addWidget(self.__logFilePathWidget)

        self.__datetimeFormatEdit = CommonDateTimeFormatEdit(label='Log中日期格式规则', value=self.__datetimeFormatRule,
                                                             labelMinSize=labelMinSize,
                                                             toolTip="请输入匹配Log文件名里的日期格式（例如：MM-dd_HH:mm:ss.SSS）")
        vbox.addWidget(self.__datetimeFormatEdit)

        self.analysisRuleTableView = CommonTableView(addBtnTxt="添加Log分析配置", headers=HEADERS,
                                                     items=self.__ruleList,
                                                     addOrEditItemFunc=self.addOrEditItemFunc)
        self.__updateRuleTableView()
        vbox.addWidget(self.analysisRuleTableView, 1)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryConfigWidget{border:1px solid rgb(0,0,255)}")
        pass

    def __extractMergeLogFile(self):
        from widget.analysis.extract.ExtractMergeLogDialog import ExtractMergeLogDialog
        ExtractMergeLogDialog(callback=lambda fp: self.__logFilePathWidget.updateData(fp))
        pass

    def __extractLogFile(self):
        from widget.analysis.extract.ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog()
        pass

    def setCategoryInfo(self, categoryInfo):
        LogUtil.d(TAG, "setCategoryInfo", categoryInfo)
        self.__categoryInfo = categoryInfo
        categoryId = DictUtil.get(categoryInfo, KEY_ID)
        self.__categoryRuleInfo = self.__analysisManager.getCategoryRuleById(categoryId)

        self.__logFilePath = DictUtil.get(self.__categoryRuleInfo, KEY_FILE_PATH, '')
        self.__logFilePathWidget.updateData(self.__logFilePath)

        self.__datetimeFormatRule = DictUtil.get(self.__categoryRuleInfo, KEY_DATETIME_FORMAT_RULE, 0)
        self.__datetimeFormatEdit.updateData(self.__datetimeFormatRule)

        self.__ruleList = copy.deepcopy(DictUtil.get(self.__categoryRuleInfo, KEY_ANALYSIS_RULES, []))
        self.__updateRuleTableView()
        pass

    def getCategoryRule(self):
        logFilePath = self.__logFilePathWidget.getData()
        if not logFilePath:
            WidgetUtil.showErrorDialog(message="请选择要分析的日志文件")
            return None
        datetimeFormatRule = self.__datetimeFormatEdit.getData()
        if not DictUtil.get(datetimeFormatRule, KEY_DATETIME_FORMAT):
            WidgetUtil.showErrorDialog(message="请输入日志中的时间格式")
            return None
        if not self.__ruleList:
            WidgetUtil.showErrorDialog(message="请添加日志分析规则")
            return None
        self.__categoryRuleInfo[KEY_FILE_PATH] = logFilePath
        self.__categoryRuleInfo[KEY_DATETIME_FORMAT_RULE] = datetimeFormatRule
        self.__categoryRuleInfo[KEY_ANALYSIS_RULES] = self.__ruleList
        return self.__categoryRuleInfo

    def __updateRuleTableView(self):
        self.analysisRuleTableView.updateData(self.__ruleList)
        pass

    def addOrEditItemFunc(self, callback, default, items):
        if not default and not self.__categoryInfo:
            WidgetUtil.showErrorDialog(message="请先选择或者添加Log分析配置")
            return

        AddOrEditAnalysisCfgDialog(callback=callback, default=default, ruleList=items)
