# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryConfigWidget.py
# 定义一个CategoryConfigWidget窗口类实现日志分析分类配置信息管理
import copy
import os

from PyQt5.QtWidgets import QFrame
from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.analysis.AddOrEditAnalysisCfgDialog import AddOrEditAnalysisCfgDialog
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonTableView import CommonTableView

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

        self.analysisManager = analysisManager
        self.categoryInfo = None
        self.categoryRuleInfo = None
        self.ruleList = []
        self.logFilePath = None
        self.logTimeIndex = None
        self.logTimeFormat = None
        self.isDebug = isDebug

        widgetLayout = WidgetUtil.createVBoxLayout()
        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="筛选指定日期范围Log文件", minSize=QSize(120, const.HEIGHT),
                                    toolTip='从指定目录下筛选指定日期范围的Log压缩文件，解压并合并到一个文件中',
                                    onClicked=self.__extractMergeLogFile)
        WidgetUtil.createPushButton(splitter, text="提取Log日志到指定文件", minSize=QSize(120, const.HEIGHT),
                                    toolTip='从指定Log文件中提取指定日期范围到Log到目标文件',
                                    onClicked=self.__extractLogFile)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.__getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createLabel(splitter, text="Log中日期格式规则：", minSize=QSize(120, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="日期起始位置", minSize=QSize(60, const.HEIGHT))
        self.logTimeIndexSpinBox = WidgetUtil.createSpinBox(splitter,
                                                            value=int(self.logTimeIndex) if self.logTimeIndex else 0,
                                                            step=1, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="日期格式", minSize=QSize(60, const.HEIGHT))
        self.logTimeFormatLE = WidgetUtil.createLineEdit(splitter,
                                                         text=self.logTimeFormat if self.logTimeFormat else '',
                                                         toolTip="请输入匹配Log文件名里的日期格式（例如：MM-dd_HH:mm:ss.SSS）",
                                                         sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        self.analysisRuleTableView = CommonTableView(addBtnTxt="添加Log分析配置", headers=HEADERS,
                                                     items=self.ruleList,
                                                     addOrEditItemFunc=self.addOrEditItemFunc)
        self.__updateRuleTableView()
        vbox.addWidget(self.analysisRuleTableView, 1)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryConfigWidget{border:1px solid rgb(0,0,255)}")
        pass

    def __extractMergeLogFile(self):
        from widget.analysis.extract.ExtractMergeLogDialog import ExtractMergeLogDialog
        ExtractMergeLogDialog(callback=lambda fp: self.logFilePathLineEdit.setText(fp))
        pass

    def __extractLogFile(self):
        from widget.analysis.extract.ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog()
        pass

    def setCategoryInfo(self, categoryInfo):
        LogUtil.d(TAG, "setCategoryInfo", categoryInfo)
        self.categoryInfo = categoryInfo
        categoryId = DictUtil.get(categoryInfo, KEY_ID)
        self.categoryRuleInfo = self.analysisManager.getCategoryRuleById(categoryId)

        self.logFilePath = DictUtil.get(self.categoryRuleInfo, KEY_FILE_PATH, '')
        self.logFilePathLineEdit.setText(self.logFilePath)

        self.logTimeIndex = DictUtil.get(self.categoryRuleInfo, KEY_LOG_TIME_INDEX, 0)
        self.logTimeIndexSpinBox.setValue(self.logTimeIndex)

        self.logTimeFormat = DictUtil.get(self.categoryRuleInfo, KEY_LOG_TIME_FORMAT, '')
        self.logTimeFormatLE.setText(self.logTimeFormat)

        self.ruleList = copy.deepcopy(DictUtil.get(self.categoryRuleInfo, KEY_ANALYSIS_RULES, []))
        self.__updateRuleTableView()
        pass

    def getCategoryRule(self):
        logFilePath = self.logFilePathLineEdit.text().strip()
        if not logFilePath:
            WidgetUtil.showErrorDialog(message="请选择要分析的日志文件")
            return None
        logTimeFormat = self.logTimeFormatLE.text().strip()
        if not logTimeFormat:
            WidgetUtil.showErrorDialog(message="请输入日志中的时间格式")
            return None
        if not self.ruleList:
            WidgetUtil.showErrorDialog(message="请添加日志分析规则")
            return None
        self.categoryRuleInfo[KEY_FILE_PATH] = logFilePath
        self.categoryRuleInfo[KEY_LOG_TIME_INDEX] = self.logTimeIndexSpinBox.value()
        self.categoryRuleInfo[KEY_LOG_TIME_FORMAT] = logTimeFormat
        self.categoryRuleInfo[KEY_ANALYSIS_RULES] = self.ruleList
        return self.categoryRuleInfo

    def __getLogFilePath(self):
        fp = ''
        if self.logFilePath:
            fp, _ = os.path.split(self.logFilePath)
        fp = WidgetUtil.getOpenFileName(caption='请选择要分析的Log文件',
                                        directory=fp)
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def __updateRuleTableView(self):
        self.analysisRuleTableView.updateData(self.ruleList)
        pass

    def addOrEditItemFunc(self, callback, default, items):
        if not default and not self.categoryInfo:
            WidgetUtil.showErrorDialog(message="请先选择或者添加Log分析配置")
            return

        AddOrEditAnalysisCfgDialog(callback=callback, default=default, ruleList=items)
