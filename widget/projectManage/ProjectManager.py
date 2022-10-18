# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManager.py
# 定义一个ProjectManager类实现项目数据管理相关的功能
from util.DictUtil import DictUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from util.JsonUtil import JsonUtil
import networkx as nx

KEY_SECTION = 'ProjectManager'

ITEM_KEY_PROJECT = 'projects'

MACRO_REPEAT = "$repeat$"

KEY_DEFAULT_MODULES = 'defaultModules'
KEY_MODULES = 'modules'
KEY_OPTION_GROUPS = 'optionGroups'
KEY_CMD_GROUPS = 'cmdGroups'

KEY_DEFAULT = 'default'
KEY_LIST = 'list'
KEY_NAME = 'name'
KEY_DESC = 'desc'

KEY_MODULE_DEPENDENCIES = 'moduleDependencies'

# 唯一标识，区分条目的
KEY_ID = 'id'
KEY_PATH = 'path'
KEY_EVN_LIST = 'evnList'
KEY_VALUE = 'value'
KEY_PROGRAM = 'program'
KEY_ARGUMENTS = 'arguments'
KEY_CONDITION_INPUT = 'conditionInput'
KEY_WORKING_DIR = 'workingDir'
KEY_IGNORE_FAILED = 'ignoreFailed'
KEY_DYNAMIC_ARGUMENTS = 'dynamicArguments'
KEY_IS_DYNAMIC_ARGUMENTS = 'isDynamicArguments'
KEY_NEED_SPACE = 'needSpace'
KEY_OPTION_GROUP_ID = 'optionGroupId'
KEY_OPTION_NAMES = 'optionNames'
KEY_NEED_CAPITALIZE = 'needCapitalize'
# 是否是相对路径，主要用于模块路径
KEY_IS_RELATIVE_PATH = 'isRelativePath'

KEY_EVN_IS_PATH = 'isPath'

KEY_CMD_LIST = 'cmdList'

KEY_OPTIONS = 'options'
KEY_OPTION_VALUES = 'optionValues'

# 执行指令输出的询问文本，等待用户输入进行下一步操作
KEY_ECHO = 'echo'
# 模拟用户输入的文本，对应于echo
KEY_INPUT = 'input'

DEFAULT_VALUE_NEED_SPACE = True
DEFAULT_VALUE_NEED_CAPITALIZE = True
DEFAULT_VALUE_IS_DYN_ARGS = True


class ProjectManager:
    def __init__(self, isDebug=False):
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.projects = JsonUtil.decode(self.operaIni.getValue(ITEM_KEY_PROJECT, KEY_SECTION))
    pass

    def saveProjects(self, infos):
        self.operaIni.addItem(KEY_SECTION, ITEM_KEY_PROJECT, JsonUtil.encode(infos, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def saveProjectInfoById(self, projectId, info):
        self.operaIni.addItem(KEY_SECTION, projectId, JsonUtil.encode(info, ensureAscii=False))
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

    def saveProjectDefaultModules(self, projectId, defaultModules):
        projectInfo = self.getProjectInfoById(projectId)
        if projectInfo is None:
            projectInfo = {}
        projectInfo[KEY_DEFAULT_MODULES] = defaultModules
        self.operaIni.addItem(KEY_SECTION, projectId, JsonUtil.encode(projectInfo, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def getProjectDefaultModules(self, projectId):
        projectInfo = self.getProjectInfoById(projectId)
        return DictUtil.get(projectInfo, KEY_DEFAULT_MODULES, [])

    def saveProjectOptionGroups(self, projectId, optionGroups):
        projectInfo = self.getProjectInfoById(projectId)
        if projectInfo is None:
            projectInfo = {}
        projectInfo[KEY_OPTION_GROUPS] = optionGroups
        self.operaIni.addItem(KEY_SECTION, projectId, JsonUtil.encode(projectInfo, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def getProjectOptionGroups(self, projectId):
        projectInfo = self.getProjectInfoById(projectId)
        return DictUtil.get(projectInfo, KEY_OPTION_GROUPS, [])

    def saveProjectCmdGroups(self, projectId, cmdGroups):
        projectInfo = self.getProjectInfoById(projectId)
        if projectInfo is None:
            projectInfo = {}
        projectInfo[KEY_CMD_GROUPS] = cmdGroups
        self.operaIni.addItem(KEY_SECTION, projectId, JsonUtil.encode(projectInfo, ensureAscii=False))
        self.operaIni.saveIni()
        pass

    def getProjectCmdGroups(self, projectId):
        projectInfo = self.getProjectInfoById(projectId)
        return DictUtil.get(projectInfo, KEY_CMD_GROUPS, [])

    @staticmethod
    def generateDiGraph(moduleList, nodes=None):
        G = nx.DiGraph()
        if not nodes:
            nodes = [item[KEY_NAME] for item in moduleList]
        G.add_nodes_from(nodes)
        for moduleInfo in moduleList:
            dependencies = DictUtil.get(moduleInfo, KEY_MODULE_DEPENDENCIES, [])
            for dependency in dependencies:
                if dependency in nodes:
                    G.add_edge(DictUtil.get(moduleInfo, KEY_NAME, ""), dependency)
        return G
