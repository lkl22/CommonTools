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
KEY_DEFAULT_TYPE = 'defaultType'
KEY_TYPE_LIST = 'typeList'
KEY_ANALYSIS_RULES = 'analysisRules'

KEY_LOG_KEYWORD = 'logKeyword'

# 结果映射，将不易理解的log映射为能理解的文字
KEY_RESULT_MAP = 'resultMap'
KEY_SRC_LOG = 'srcLog'
KEY_MAP_TXT = 'mapTxt'
# 结果转换配置
KEY_TRANSFORM_CFGS = 'transformCfgs'
# 结果转换列表
KEY_TRANSFORM_FUNCS = 'transformFuncs'

KEY_START_LOG_KEYWORD = 'startLogKeyword'
KEY_END_LOG_KEYWORD = 'endLogKeyword'

KEY_NEED_SPLICE_LOG = "needSpliceLog"
DEFAULT_VALUE_NEED_SPLICE_LOG = False

# 拼接日志相关参数
KEY_SPLICE_PARAMS = 'spliceLogParams'
# 拆分行日志正则表达式
KEY_SPLIT_RE = 'spliceLogParams'
# 处理函数
KEY_FUNCTION = 'function'
KEY_ENABLE_UML_TRANSFORM = 'enableUmlTransform'

KEY_IS_CONTAIN = "isContain"
DEFAULT_VALUE_IS_CONTAIN = True

KEY_IS_ENABLE = "isEnable"
DEFAULT_VALUE_IS_ENABLE = True

KEY_IS_FUNCTION = "isFunction"
DEFAULT_VALUE_IS_FUNCTION = False

KEY_NEED_COST_TIME = "needCostTime"
DEFAULT_VALUE_NEED_COST_TIME = False

KEY_NEED_LOG_TRANSFORM = "needLogTransform"
DEFAULT_VALUE_NEED_LOG_TRANSFORM = False


class LogAnalysisManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni()
        self.configs = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_CATEGORY, KEY_SECTION))

    pass

    def saveConfigs(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_CATEGORY, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def saveCategoryRuleById(self, categoryId, info):
        self.operaIni.addItem(KEY_SECTION, categoryId, JsonUtil.encode(info, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def delCategoryRuleById(self, categoryId):
        self.operaIni.removeItem(KEY_SECTION, categoryId)
        self.operaIni.saveIni()
        pass

    def getCategoryRuleById(self, categoryId):
        return JsonUtil.decode(self.operaIni.getValue(categoryId, KEY_SECTION), {})
