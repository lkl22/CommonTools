# -*- coding: utf-8 -*-
# python 3.x
# Filename: EFKLogSystemConfigManager.py
# 定义一个EFKLogSystemConfigManager类实现EFK日志系统管理相关的功能
from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'EFKLogSystem'

# 系统是否已经初始化过，替换了配置可以直接使用，默认False
KEY_IS_INIT = 'isInit'
DEFAULT_VALUE_IS_INIT = False
KEY_EFK_SOFTWARE_PATH = 'efkSoftwarePath'
KEY_LOG_DIR_PATH = 'logDirPath'
KEY_CONFIG_DIR_PATH = 'configDirPath'


class EFKLogSystemConfigManager:
    def __init__(self):
        self.operaIni = OperaIni()
        self.configs = JsonUtil.decode(self.operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})

    def saveConfigs(self):
        self.operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(self.configs, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def isInit(self):
        return DictUtil.get(self.configs, KEY_IS_INIT, DEFAULT_VALUE_IS_INIT)

    def setInited(self):
        self.configs[KEY_IS_INIT] = True
        self.saveConfigs()

    def getEFKSoftwarePath(self):
        return DictUtil.get(self.configs, KEY_EFK_SOFTWARE_PATH, '')

    def setEFKSoftwarePath(self, path):
        if path:
            self.configs[KEY_EFK_SOFTWARE_PATH] = path

    def getLogDirPath(self):
        return DictUtil.get(self.configs, KEY_LOG_DIR_PATH, 'D:/log')

    def setLogDirPath(self, path):
        if path:
            self.configs[KEY_LOG_DIR_PATH] = path

    def getConfigDirPath(self):
        return DictUtil.get(self.configs, KEY_CONFIG_DIR_PATH, '')

    def setConfigDirPath(self, path):
        if path:
            self.configs[KEY_CONFIG_DIR_PATH] = path
