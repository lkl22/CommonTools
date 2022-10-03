# -*- coding: utf-8 -*-
# python 3.x
# Filename: AccountManager.py
# 定义一个AccountManager类实现账户数据管理相关的功能
from Cryptodome.Cipher import DES, AES
import binascii
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'ProjectManager'

ITEM_KEY_PROJECT = 'projects'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_DESC = 'desc'

# 项目的唯一标识，通过projectName生成的MD5值，不限制projectName的输入字符
KEY_PROJECT_ID = 'projectId'
KEY_PROJECT_NAME = 'projectName'
KEY_PROJECT_PATH = 'projectPath'
KEY_PROJECT_ENV_LIST = 'projectEvnList'

KEY_EVN_NAME = 'evnName'
KEY_EVN_VALUE = 'evnValue'

KEY_MODULE_NAME = 'moduleName'


class AccountManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        # {"default": {"desc": "镜像环境", "flavorName": "mirror"}, "list": [{"desc": "开发环境", "flavorName": "develop"},{"desc": "镜像环境", "flavorName": "mirror"}]}
        self.projects = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_PROJECT, KEY_SECTION))
    pass

    def saveProjectInfos(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_PROJECT, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def saveCountryInfos(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_PROJECT, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def getAccountInfos(self, key):
        return JsonUtil.decode(self.operaIni.getValue(key, KEY_SECTION))

    def saveAccountInfos(self, key, infos):
        # [{'phoneNo' : '18589001736', 'pwd' : 'qwe123456'}, 'desc': '中国成人账号']
        self.operaIni.addItem(KEY_SECTION, key, JsonUtil.encode(infos, ensureAscii=False, sort_keys=False))
        self.operaIni.saveIni()
        pass


if __name__ == "__main__":
    accountManager = AccountManager(isDebug=True)
    accountManager.saveAccountInfos('product', "[{'flavorName' : 'product', 'desc' : '现网环境'}]")
    pass