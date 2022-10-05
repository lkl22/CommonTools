# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManager.py
# 定义一个ProjectManager类实现项目数据管理相关的功能
from util.DictUtil import DictUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil

KEY_SECTION = 'ProjectManager'

ITEM_KEY_PROJECT = 'projects'

KEY_MODULES = 'modules'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_NAME = 'name'
KEY_DESC = 'desc'

# 唯一标识，区分条目的
KEY_ID = 'id'
KEY_PATH = 'path'
KEY_ENV_LIST = 'evnList'
KEY_VALUE = 'value'
KEY_PROGRAM = 'program'
KEY_ARGUMENTS = 'arguments'
KEY_WORKING_DIR = 'workingDir'
KEY_EVN_IS_PATH = 'isPath'

KEY_CMD_LIST = 'cmdList'


class ProjectManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.projects = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_PROJECT, KEY_SECTION))
    pass

    def saveProjects(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_PROJECT, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def delProjectInfoById(self, projectId):
        self.operaIni.removeItem(KEY_SECTION, projectId)
        self.operaIni.saveIni()
        pass

    def getProjectInfoById(self, projectId):
        return JsonUtil.decode(self.operaIni.getValue(projectId, KEY_SECTION))

    def saveProjectModulesInfo(self, projectId, modulesInfo):
        projectInfo = self.getProjectInfoById(projectId)
        if projectInfo is None:
            projectInfo = {}
        projectInfo[KEY_MODULES] = modulesInfo
        self.operaIni.addItem(KEY_SECTION, projectId, JsonUtil.encode(projectInfo, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def getProjectModules(self, projectId):
        projectInfo = self.getProjectInfoById(projectId)
        return DictUtil.get(projectInfo, KEY_MODULES, [])
