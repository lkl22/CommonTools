# -*- coding: utf-8 -*-
# python 3.x
# Filename: FindFileContentManager.py
# 定义一个AccountManager类实现账户数据管理相关的功能
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'FindFileConfig'
ITEM_KEY_CONFIGS = 'configs'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_DESC = 'desc'
KEY_NAME = 'name'
KEY_PATH = 'path'
KEY_IS_REG = 'isReg'
KEY_PATTERN = 'pattern'

KEY_MATCH_TYPE = 'matchType'
MATCH_TYPE_INCLUDE = 'include'
MATCH_TYPE_EXCLUDE = 'exclude'

KEY_INCLUDE_PATTERN = 'includePattern'
KEY_EXCLUDE_EXT = 'excludeExt'
KEY_EXCLUDE_DIR = 'excludeDir'

DEFAULT_VALUE_IS_REG = False


class FindFileContentManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.configs = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_CONFIGS, KEY_SECTION))
        self.path = self.operaIni.getValue(KEY_PATH, KEY_SECTION)
    pass

    def saveConfigInfos(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_CONFIGS, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def savePath(self, path):
        self.operaIni.addItem(KEY_SECTION, KEY_PATH, path)
        self.operaIni.saveIni()
        pass
