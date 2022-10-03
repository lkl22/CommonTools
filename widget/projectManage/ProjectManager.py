# -*- coding: utf-8 -*-
# python 3.x
# Filename: AccountManager.py
# 定义一个AccountManager类实现账户数据管理相关的功能
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'ProjectManager'

ITEM_KEY_PROJECT = 'projects'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_NAME = 'name'
KEY_DESC = 'desc'

# 唯一标识，区分条目的
KEY_ID = 'id'
KEY_PATH = 'path'
KEY_ENV_LIST = 'evnList'
KEY_VALUE = 'value'

KEY_EVN_IS_PATH = 'isPath'


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