# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisManager.py
# 定义一个LogAnalysisManager类实现Log分析管理相关的功能
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil


KEY_SECTION = 'LogAnalysis'

# 分析分类
ITEM_KEY_CATEGORY = 'category'

# 唯一标识，区分条目的
KEY_ID = 'id'
KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_NAME = 'name'
KEY_DESC = 'desc'

KEY_FILE_PATH = 'filePath'


KEY_NEED_COST_TIME = "needCostTime"
DEFAULT_VALUE_HAS_COST_TIME = False


class LogAnalysisManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.configs = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_CATEGORY, KEY_SECTION))
    pass

    def saveConfigs(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_CATEGORY, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def saveCategoryInfoById(self, categoryId, info):
        self.operaIni.addItem(KEY_SECTION, categoryId, JsonUtil.encode(info, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def delCategoryInfoById(self, categoryId):
        self.operaIni.removeItem(KEY_SECTION, categoryId)
        self.operaIni.saveIni()
        pass

    def getCategoryInfoById(self, categoryId):
        return JsonUtil.decode(self.operaIni.getValue(categoryId, KEY_SECTION))
