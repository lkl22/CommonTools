# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryManagerWidget.py
# 定义一个CategoryManagerWidget窗口类实现日志分析分类管理
import os
from PyQt5.QtWidgets import QFrame

from constant import const
from util.DateUtil import DateUtil
from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.ListUtil import ListUtil
from util.WidgetUtil import *
from widget.analysis.AddOrEditCategoryDialog import AddOrEditCategoryDialog
from widget.analysis.LogAnalysisManager import *

TAG = "CategoryManagerWidget"


class CategoryManagerWidget(QFrame):
    def __init__(self, analysisManager: LogAnalysisManager, modifyCallback):
        super(CategoryManagerWidget, self).__init__()

        self.analysisManager = analysisManager
        self.modifyCallback = modifyCallback
        self.configs = {KEY_DEFAULT: -1, KEY_LIST: []} | self.analysisManager.configs
        self.curCategoryIndex = self.configs[KEY_DEFAULT]
        self.categoryId = -1

        self.setObjectName(TAG)
        self.setToolTip("日志分析配置信息管理")
        widgetLayout = WidgetUtil.createVBoxLayout()

        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(self, text="请选择Log分析配置："))
        self.categoryComboBox = WidgetUtil.createComboBox(self, activated=self.__categoryIndexChanged,
                                                          sizePolicy=WidgetUtil.createSizePolicy())
        hbox.addWidget(self.categoryComboBox, 1)

        hbox.addWidget(WidgetUtil.createPushButton(self, text="Add", toolTip="添加新配置", onClicked=self.__addCategory))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Modify", toolTip="修改配置", onClicked=self.__modifyCategory))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Del", toolTip="删除配置", onClicked=self.__delCategory))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Save As", toolTip="导出该配置配置", onClicked=self.__saveAsCategory))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Import", toolTip="导入配置配置", onClicked=self.__importCategory))
        vbox.addLayout(hbox)

        splitter = WidgetUtil.createSplitter(self)
        WidgetUtil.createPushButton(splitter, text="筛选指定日期范围Log文件", minSize=QSize(120, const.HEIGHT),
                                    toolTip='从指定目录下筛选指定日期范围的Log压缩文件，解压并合并到一个文件中',
                                    onClicked=self.__extractMergeLogFile)
        WidgetUtil.createPushButton(splitter, text="提取Log日志到指定文件", minSize=QSize(120, const.HEIGHT),
                                    toolTip='从指定Log文件中提取指定日期范围到Log到目标文件',
                                    onClicked=self.__extractLogFile)
        vbox.addWidget(splitter)

        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryManagerWidget{border:1px solid rgb(0,0,255)}")
        self.modifyCallback(self.__getCurCategoryInfo())
        self.__updateCategoryComboBox()
        pass

    def __extractMergeLogFile(self):
        from widget.analysis.extract.ExtractMergeLogDialog import ExtractMergeLogDialog
        ExtractMergeLogDialog()
        pass

    def __extractLogFile(self):
        from widget.analysis.extract.ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog()
        pass

    def __updateCategoryComboBox(self):
        if self.configs and self.configs[KEY_LIST]:
            self.categoryComboBox.clear()
            for index, item in enumerate(self.configs[KEY_LIST]):
                self.categoryComboBox.addItem(f"{item[KEY_NAME]}（{item[KEY_DESC]}）", item)
            if self.curCategoryIndex < 0:
                self.curCategoryIndex = 0
            curCategoryInfo = self.configs[KEY_LIST][self.curCategoryIndex]
            self.categoryComboBox.setCurrentText(f"{curCategoryInfo[KEY_NAME]}（{curCategoryInfo[KEY_DESC]}）")
            LogUtil.d(TAG, 'updateFlavorComboBox setCurrentText', curCategoryInfo[KEY_NAME])
        else:
            self.categoryComboBox.clear()
            self.curCategoryIndex = -1
            LogUtil.d(TAG, "no category")
        pass

    def __categoryIndexChanged(self, index):
        LogUtil.d(TAG, 'categoryIndexChanged', index)
        self.curCategoryIndex = index
        self.__saveCategorys()
        pass

    def __saveCategorys(self):
        # 更新当前默认打开的配置信息
        self.configs[KEY_DEFAULT] = self.curCategoryIndex
        # 将配置配置保存到ini文件
        self.analysisManager.saveConfigs(self.configs)
        self.modifyCallback(self.__getCurCategoryInfo())
        pass

    def __getCurCategoryInfo(self):
        if self.curCategoryIndex >= 0:
            return self.configs[KEY_LIST][self.curCategoryIndex]
        else:
            return None

    def __addCategory(self):
        LogUtil.d(TAG, "addCategory")
        AddOrEditCategoryDialog(callback=self.__addOrEditCategoryCallback)
        pass

    def __modifyCategory(self):
        LogUtil.d(TAG, "modifyCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return
        curCategoryInfo = self.__getCurCategoryInfo()
        self.categoryId = curCategoryInfo[KEY_ID]
        AddOrEditCategoryDialog(callback=self.__addOrEditCategoryCallback, categoryInfo=curCategoryInfo,
                                categoryList=self.configs)
        pass

    def __addOrEditCategoryCallback(self, info):
        LogUtil.d(TAG, "addOrEditCategoryCallback", info)
        curCategoryInfo = self.__getCurCategoryInfo()
        categorys = self.configs[KEY_LIST]
        if info:
            categorys.append(info)
        # 按配置名称重新排序
        self.configs[KEY_LIST] = sorted(categorys, key=lambda x: x[KEY_NAME])
        if curCategoryInfo:
            for index, item in enumerate(self.configs[KEY_LIST]):
                if curCategoryInfo == item:
                    self.curCategoryIndex = index
                    break
        # 更新分类下拉选择框
        self.__updateCategoryComboBox()
        # 修改了分类，对应的分类信息也同步修改
        if curCategoryInfo[KEY_ID] != self.categoryId:
            categoryRule = self.analysisManager.getCategoryRuleById(self.categoryId)
            if categoryRule:
                self.analysisManager.saveCategoryRuleById(curCategoryInfo[KEY_ID], categoryRule)
        # 将分类信息保存到ini文件
        self.__saveCategorys()
        pass

    def __getCurCategoryInfo(self):
        if self.curCategoryIndex >= 0:
            return self.configs[KEY_LIST][self.curCategoryIndex]
        else:
            return None

    def __delCategory(self):
        LogUtil.d(TAG, "delCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return
        categoryInfo = self.__getCurCategoryInfo()
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{categoryInfo[KEY_NAME]}（{categoryInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=self.__delCategoryItem)
        pass

    def __delCategoryItem(self):
        LogUtil.i(TAG, "delCategoryItem")
        curCategoryInfo = self.__getCurCategoryInfo()
        self.configs[KEY_LIST].remove(curCategoryInfo)
        self.curCategoryIndex = -1
        self.__updateCategoryComboBox()
        self.analysisManager.delCategoryRuleById(curCategoryInfo[KEY_ID])
        self.__saveCategorys()
        pass

    def __saveAsCategory(self):
        LogUtil.d(TAG, "saveAsCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return

        curCategoryInfo = self.__getCurCategoryInfo()
        detailCategoryInfo = self.analysisManager.getCategoryRuleById(curCategoryInfo[KEY_ID])

        saveData = {"simpleInfo": curCategoryInfo, "detailInfo": detailCategoryInfo if detailCategoryInfo else {}}
        fp = WidgetUtil.getExistingDirectory(caption="请选择要备份保存的路径，不选的话默认使用当前工程路径。")
        if not fp:
            fp = "./"
        saveFile = os.path.join(fp,
                                f"{curCategoryInfo[KEY_NAME]}_{DateUtil.nowTime(timeFormat='%Y-%m-%d_%H:%M:%S')}.json")
        with open(saveFile, 'w', encoding="utf-8") as file:
            file.write(JsonUtil.encode(saveData, ensureAscii=False))
        WidgetUtil.showAboutDialog(
            text=f"你成功保存<span style='color:red;'>{curCategoryInfo[KEY_NAME]}</span>分类信息到<span style='color:red;'>{saveFile}</span>")
        pass

    def __importCategory(self):
        LogUtil.d(TAG, "importCategory")
        curCategoryInfo = self.__getCurCategoryInfo()
        fp = WidgetUtil.getOpenFileName(caption='选择备份的分类配置文件', filter='*.json', initialFilter='*.json')
        if not fp:
            WidgetUtil.showAboutDialog(text="您未选择配置文件，导入分类配置失败。")
            return

        fileContent = FileUtil.readFile(fp)
        if not fileContent:
            WidgetUtil.showAboutDialog(text="您选择的配置文件没有内容，导入分类配置失败。")
            return
        categoryInfo = JsonUtil.decode(fileContent)
        if not DictUtil.get(DictUtil.get(categoryInfo, "simpleInfo", {}), KEY_NAME):
            WidgetUtil.showAboutDialog(text="您选择的配置文件格式错误，导入分类配置失败。")
            return
        if ListUtil.contain(self.configs[KEY_LIST], KEY_NAME, categoryInfo["simpleInfo"][KEY_NAME]):
            WidgetUtil.showQuestionDialog(message=f"{categoryInfo['simpleInfo'][KEY_NAME]}已经存在，是否继续，继续将覆盖现有的配置。",
                                          acceptFunc=lambda: self.__startImportCategory(categoryInfo, True))
            return
        self.__startImportCategory(categoryInfo)
        pass

    def __startImportCategory(self, categoryInfo, has=False):
        LogUtil.d(TAG, "startImportCategory", has)
        categorys = self.configs[KEY_LIST]
        if has:
            categorys.remove(ListUtil.find(categorys, KEY_NAME, categoryInfo['simpleInfo'][KEY_NAME]))
        categorys.append(categoryInfo['simpleInfo'])
        # 按配置名称重新排序
        self.configs[KEY_LIST] = sorted(categorys, key=lambda x: x[KEY_NAME])
        self.analysisManager.saveCategoryRuleById(categoryInfo['simpleInfo'][KEY_ID], categoryInfo['detailInfo'])
        # 更新分类下拉选择框
        self.__updateCategoryComboBox()
        # 将分类信息保存到ini文件
        self.__saveCategorys()
        WidgetUtil.showAboutDialog(
            text=f"您成功导入<span style='color:red;'>{categoryInfo['simpleInfo'][KEY_NAME]}</span>分类信息")
        pass
