# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryConfigWidget.py
# 定义一个CategoryConfigWidget窗口类实现日志分析分类配置信息管理
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
        self.categoryConfigInfo = None
        self.ruleList = []
        self.logFilePath = None
        self.isDebug = isDebug

        widgetLayout = WidgetUtil.createVBoxLayout()
        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)
        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="提取Log文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.extractLogFile)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(self, text="添加Log分析配置", onClicked=self.addAnalysisCfg))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.analysisRuleTableView = WidgetUtil.createTableView(self, doubleClicked=self.analysisCfgTableDoubleClicked)
        # 设为不可编辑
        self.analysisRuleTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.analysisRuleTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.analysisRuleTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.analysisRuleTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.analysisRuleTableView.customContextMenuRequested.connect(self.analysisCfgCustomRightMenu)
        self.updateRuleTableView()
        vbox.addWidget(self.analysisRuleTableView, 1)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryConfigWidget{border:1px solid rgb(0,0,255)}")
        pass

    def setCategoryInfo(self, categoryInfo):
        LogUtil.d(TAG, "setCategoryInfo", categoryInfo)
        categoryId = DictUtil.get(categoryInfo, KEY_ID)
        self.categoryConfigInfo = self.analysisManager.getCategoryInfoById(categoryId)
        pass

    def extractLogFile(self):
        from widget.analysis.ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog()
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

    def addAnalysisCfg(self):
        LogUtil.d(TAG, "addAnalysisCfg")
        AddOrEditAnalysisCfgDialog(callback=self.addOrEditAnalysisCfgCallback,
                                   ruleList=self.ruleList)
        pass

    def addOrEditAnalysisCfgCallback(self, info):
        LogUtil.d(TAG, "addOrEditAnalysisCfgCallback", info)
        if info:
            self.ruleList.append(info)
        self.updateRuleTableView()
        pass

    def analysisCfgTableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "dynParamsTableDoubleClicked：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditAnalysisCfgDialog(callback=self.addOrEditAnalysisCfgCallback,
                                   default=self.ruleList[row],
                                   ruleList=self.ruleList)
        pass

    def analysisCfgCustomRightMenu(self, pos):
        self.curRow = self.analysisRuleTableView.currentIndex().row()
        LogUtil.i(TAG, "analysisCfgCustomRightMenu", pos, ' row: ', self.curRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delRule)
        menu.exec(self.analysisRuleTableView.mapToGlobal(pos))
        pass

    def delRule(self):
        ruleName = self.ruleList[self.curRow][KEY_NAME]
        LogUtil.i(TAG, f"delRule {ruleName}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{ruleName}</span> 吗？",
                                      acceptFunc=self.delRuleTableItem)
        pass

    def delRuleTableItem(self):
        LogUtil.i(TAG, "delRuleTableItem")
        self.ruleList.remove(self.ruleList[self.curRow])
        self.updateRuleTableView()
        pass

    def updateRuleTableView(self):
        tableData = []
        for rule in self.ruleList:
            tableData.append({
                KEY_NAME: rule[KEY_NAME],
                KEY_DESC: DictUtil.get(rule, KEY_DESC, ""),
                KEY_NEED_COST_TIME: DictUtil.get(rule, KEY_NEED_COST_TIME, DEFAULT_VALUE_NEED_COST_TIME)
            })
        WidgetUtil.addTableViewData(self.analysisRuleTableView, tableData,
                                    headerLabels=["规则名", "规则描述", "统计耗时"])
        pass
