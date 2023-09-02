# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryConfigWidget.py
# 定义一个CategoryConfigWidget窗口类实现日志分析分类配置信息管理
import copy
import os

from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QFrame, QAbstractItemView
from constant import const
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.analysis.AddOrEditAnalysisCfgDialog import AddOrEditAnalysisCfgDialog
from widget.analysis.LogAnalysisManager import *

TAG = "CategoryConfigWidget"


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

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.addAnalysisCfgBtn = WidgetUtil.createPushButton(self, text="添加Log分析配置", onClicked=self.__addAnalysisCfg)
        hbox.addWidget(self.addAnalysisCfgBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.analysisRuleTableView = WidgetUtil.createTableView(self,
                                                                doubleClicked=self.__analysisCfgTableDoubleClicked)
        # 设为不可编辑
        self.analysisRuleTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.analysisRuleTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.analysisRuleTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.analysisRuleTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.analysisRuleTableView.customContextMenuRequested.connect(self.__analysisCfgCustomRightMenu)
        self.__updateRuleTableView()
        vbox.addWidget(self.analysisRuleTableView, 1)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryConfigWidget{border:1px solid rgb(0,0,255)}")
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

    def __addAnalysisCfg(self):
        LogUtil.d(TAG, "addAnalysisCfg")
        if not self.categoryInfo:
            WidgetUtil.showErrorDialog(message="请先选择或者添加Log分析配置")
            return
        AddOrEditAnalysisCfgDialog(callback=self.__addOrEditAnalysisCfgCallback,
                                   ruleList=self.ruleList)
        pass

    def __addOrEditAnalysisCfgCallback(self, info):
        LogUtil.d(TAG, "addOrEditAnalysisCfgCallback", info)
        if info:
            self.ruleList.append(info)
        self.__updateRuleTableView()
        pass

    def __analysisCfgTableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "dynParamsTableDoubleClicked：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditAnalysisCfgDialog(callback=self.__addOrEditAnalysisCfgCallback,
                                   default=self.ruleList[row],
                                   ruleList=self.ruleList)
        pass

    def __analysisCfgCustomRightMenu(self, pos):
        self.curRow = self.analysisRuleTableView.currentIndex().row()
        LogUtil.i(TAG, "analysisCfgCustomRightMenu", pos, ' row: ', self.curRow)
        menu = WidgetUtil.createMenu("删除", func1=self.__delRule)
        menu.exec(self.analysisRuleTableView.mapToGlobal(pos))
        pass

    def __delRule(self):
        ruleName = self.ruleList[self.curRow][KEY_NAME]
        LogUtil.i(TAG, f"delRule {ruleName}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{ruleName}</span> 吗？",
                                      acceptFunc=self.__delRuleTableItem)
        pass

    def __delRuleTableItem(self):
        LogUtil.i(TAG, "delRuleTableItem")
        self.ruleList.remove(self.ruleList[self.curRow])
        self.__updateRuleTableView()
        pass

    def __updateRuleTableView(self):
        tableData = []
        for rule in self.ruleList:
            tableData.append({
                KEY_NAME: DictUtil.get(rule, KEY_NAME, ''),
                KEY_DESC: DictUtil.get(rule, KEY_DESC, ""),
                KEY_LOG_KEYWORD: DictUtil.get(rule, KEY_LOG_KEYWORD, ""),
                KEY_NEED_COST_TIME: DictUtil.get(rule, KEY_NEED_COST_TIME, DEFAULT_VALUE_NEED_COST_TIME),
                KEY_START_LOG_KEYWORD: DictUtil.get(rule, KEY_START_LOG_KEYWORD, ""),
                KEY_END_LOG_KEYWORD: DictUtil.get(rule, KEY_END_LOG_KEYWORD, ""),
            })
        WidgetUtil.addTableViewData(self.analysisRuleTableView, tableData,
                                    headerLabels=["规则名", "规则描述", "日志关键字", "统计耗时", "开始日志关键字", "结束日志关键字"])
        pass
