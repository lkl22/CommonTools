# -*- coding: utf-8 -*-
# python 3.x
# Filename: CategoryManagerWidget.py
# 定义一个CategoryManagerWidget窗口类实现日志分析分类管理
import os
from PyQt5.QtWidgets import QFrame
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
        self.configs = self.analysisManager.configs
        if not self.configs:
            self.configs = {KEY_DEFAULT: -1, KEY_LIST: []}
        self.curCategoryIndex = self.configs[KEY_DEFAULT]

        self.setObjectName(TAG)
        self.setToolTip("日志分析配置信息管理")
        widgetLayout = WidgetUtil.createVBoxLayout()

        widgetLayout.addWidget(self)
        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(self, text="请选择Log分析配置："))
        self.categoryComboBox = WidgetUtil.createComboBox(self, activated=self.categoryIndexChanged,
                                                          sizePolicy=WidgetUtil.createSizePolicy())
        hbox.addWidget(self.categoryComboBox, 1)

        hbox.addWidget(WidgetUtil.createPushButton(self, text="Add", toolTip="添加新配置", onClicked=self.addCategory))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Modify", toolTip="修改配置", onClicked=self.modifyCategory))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="Del", toolTip="删除配置", onClicked=self.delCategory))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Save As", toolTip="导出该配置配置", onClicked=self.saveAsCategory))
        hbox.addWidget(
            WidgetUtil.createPushButton(self, text="Import", toolTip="导入配置配置", onClicked=self.importCategory))
        vbox.addLayout(hbox)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("CategoryManagerWidget{border:1px solid rgb(0,0,255)}")
        self.updateCategoryComboBox()
        pass

    def updateCategoryComboBox(self):
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

    def categoryIndexChanged(self, index):
        LogUtil.d(TAG, 'categoryIndexChanged', index)
        self.curCategoryIndex = index
        self.saveCategorys()
        pass

    def saveCategorys(self):
        # 更新当前默认打开的配置信息
        self.configs[KEY_DEFAULT] = self.curCategoryIndex
        # 将配置配置保存到ini文件
        self.analysisManager.saveConfigs(self.configs)
        pass

    def addCategory(self):
        LogUtil.d(TAG, "addCategory")
        AddOrEditCategoryDialog(callback=self.addOrEditCategoryCallback)
        pass

    def modifyCategory(self):
        LogUtil.d(TAG, "modifyCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return
        AddOrEditCategoryDialog(callback=self.addOrEditCategoryCallback,
                                categoryInfo=self.configs[KEY_LIST][self.curCategoryIndex], categoryList=self.configs)
        pass

    def addOrEditCategoryCallback(self, info):
        LogUtil.d(TAG, "addOrEditCategoryCallback", info)
        categorys = self.configs[KEY_LIST]
        if info:
            categorys.append(info)
        curCategoryInfo = self.getCurCategoryInfo()
        # 按配置名称重新排序
        self.configs[KEY_LIST] = sorted(categorys, key=lambda x: x[KEY_NAME])
        if curCategoryInfo:
            for index, item in enumerate(self.configs[KEY_LIST]):
                if curCategoryInfo == item:
                    self.curCategoryIndex = index
                    break
        # 更新分类下拉选择框
        self.updateCategoryComboBox()
        # 将分类信息保存到ini文件
        self.saveCategorys()
        pass

    def getCurCategoryInfo(self):
        if self.curCategoryIndex >= 0:
            return self.configs[KEY_LIST][self.curCategoryIndex]
        else:
            return None

    def delCategory(self):
        LogUtil.d(TAG, "delCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return
        categoryInfo = self.getCurCategoryInfo()
        WidgetUtil.showQuestionDialog(
            message=f"你确定需要删除 <span style='color:red;'>{categoryInfo[KEY_NAME]}（{categoryInfo[KEY_DESC]}）</span> 吗？",
            acceptFunc=self.delCategoryItem)
        pass

    def delCategoryItem(self):
        LogUtil.i(TAG, "delCategoryItem")
        curCategoryInfo = self.getCurCategoryInfo()
        self.configs[KEY_LIST].remove(curCategoryInfo)
        self.curCategoryIndex = -1
        self.updateCategoryComboBox()
        self.analysisManager.delCategoryInfoById(curCategoryInfo[KEY_ID])
        self.saveCategorys()
        pass

    def saveAsCategory(self):
        LogUtil.d(TAG, "saveAsCategory")
        if self.curCategoryIndex < 0:
            WidgetUtil.showAboutDialog(text="请先选择一个分类")
            return

        curCategoryInfo = self.getCurCategoryInfo()
        detailCategoryInfo = self.analysisManager.getCategoryInfoById(curCategoryInfo[KEY_ID])

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

    def importCategory(self):
        LogUtil.d(TAG, "importCategory")
        curCategoryInfo = self.getCurCategoryInfo()
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
                                          acceptFunc=lambda: self.startImportCategory(categoryInfo, True))
            return
        self.startImportCategory(categoryInfo)
        pass

    def startImportCategory(self, categoryInfo, has=False):
        LogUtil.d(TAG, "startImportCategory", has)
        categorys = self.configs[KEY_LIST]
        if has:
            categorys.remove(ListUtil.find(categorys, KEY_NAME, categoryInfo['simpleInfo'][KEY_NAME]))
        categorys.append(categoryInfo['simpleInfo'])
        # 按配置名称重新排序
        self.configs[KEY_LIST] = sorted(categorys, key=lambda x: x[KEY_NAME])
        self.analysisManager.saveCategoryInfoById(categoryInfo['simpleInfo'][KEY_ID], categoryInfo['detailInfo'])
        # 更新分类下拉选择框
        self.updateCategoryComboBox()
        # 将分类信息保存到ini文件
        self.saveCategorys()
        WidgetUtil.showAboutDialog(
            text=f"您成功导入<span style='color:red;'>{categoryInfo['simpleInfo'][KEY_NAME]}</span>分类信息")
        pass