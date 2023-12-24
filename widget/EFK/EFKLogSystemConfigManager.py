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


class EFKLogSystemConfigManager:
    def __init__(self):
        self.operaIni = OperaIni()
        self.configs = JsonUtil.decode(self.operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})
    pass

    def saveConfigs(self):
        self.operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(self.configs, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def isInit(self):
        return DictUtil.get(self.configs, KEY_IS_INIT, DEFAULT_VALUE_IS_INIT)

    def setInited(self):
        self.configs[KEY_IS_INIT] = True
        self.saveConfigs()


