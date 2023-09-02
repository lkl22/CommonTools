# -*- coding: utf-8 -*-
# python 3.x
# Filename: AccountManager.py
# 定义一个AccountManager类实现账户数据管理相关的功能
from Cryptodome.Cipher import DES, AES
import binascii
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'Accounts'
ITEM_KEY_FLAVOR = 'flavors'
ITEM_KEY_COUNTRY = 'countries'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_DESC = 'desc'
KEY_FLAVOR_NAME = 'flavorName'
KEY_COUNTRY_CODE = 'countryCode'

KEY_ACCOUNT = 'account'
KEY_NICKNAME = 'nickname'
KEY_PWD = 'pwd'


class AccountManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni()
        # {"default": {"desc": "镜像环境", "flavorName": "mirror"}, "list": [{"desc": "开发环境", "flavorName": "develop"},{"desc": "镜像环境", "flavorName": "mirror"}]}
        self.flavors = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_FLAVOR, KEY_SECTION))
        # {"default": {"countryCode": "MY", "desc": "马来"}, "list": [{"countryCode": "CN", "desc": "中国"}, {"countryCode": "MY", "desc": "马来"}]}
        self.countries = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_COUNTRY, KEY_SECTION))
    pass

    def saveFlavorInfos(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_FLAVOR, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def saveCountryInfos(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_COUNTRY, JsonUtil.encode(infos, ensureAscii=False))
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
    accountManager.saveFlavorInfos("[{'flavorName' : 'product', 'desc' : '现网环境'}]")
    accountManager.saveAccountInfos('product', "[{'flavorName' : 'product', 'desc' : '现网环境'}]")
    pass