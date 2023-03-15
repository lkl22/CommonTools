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
MACRO_DATE = "$date$"
MACRO_DATETIME = "$datetime$"

KEY_DEFAULT_MODULES = 'defaultModules'
KEY_MODULES = 'modules'
KEY_OPTION_GROUPS = 'optionGroups'
KEY_OPTION_GROUP = 'optionGroup'
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

# 选项值在作为该指令的动态参数时是否需要将首字母转换为大写 True 首字母转大写
KEY_NEED_CAPITALIZE = 'needCapitalize'
DEFAULT_VALUE_NEED_CAPITALIZE = False

# 指令执行前置条件列表
KEY_PRECONDITIONS = 'preconditions'
# 存储多个前置条件间的逻辑关系 key
KEY_PRECONDITIONS_LOGIC = 'preconditionsLogic'
# 多个前置条件间的逻辑关系 - 与 and
PRECONDITIONS_LOGIC_ALL = 'all'
# 多个前置条件间的逻辑关系 - 或 or
PRECONDITIONS_LOGIC_ANY = 'any'

# 存储前置条件判断逻辑 key
KEY_PRECONDITION_LOGIC = 'preconditionLogic'
# 前置条件判断逻辑 ==
PRECONDITION_LOGIC_EQ = 'eq'
# 前置条件判断逻辑 !=
PRECONDITION_LOGIC_NEQ = 'neq'

KEY_OPTION_GROUP_ID = 'optionGroupId'
KEY_OPTION_NAMES = 'optionNames'

# 是否是相对路径，主要用于模块路径
KEY_IS_RELATIVE_PATH = 'isRelativePath'

KEY_EVN_IS_PATH = 'isPath'

KEY_CMD_LIST = 'cmdList'

KEY_OPTIONS = 'options'
KEY_OPTION = 'option'
KEY_OPTION_VALUES = 'optionValues'
KEY_OPTION_VALUE = 'optionValue'

# 执行指令输出的询问文本，等待用户输入进行下一步操作
KEY_ECHO = 'echo'
# 模拟用户输入的文本，对应于echo
KEY_INPUT = 'input'

# 原有的值
KEY_OLD_VALUE = 'oldValue'
# 现在的值
KEY_NEW_VALUE = 'newValue'

KEY_ALL = "All"
STATUS_LOADING = "loading"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_HIDE = "hide"

KEY_IS_VISIBLE = "isVisible"
DEFAULT_VALUE_IS_VISIBLE = True
KEY_IS_SELECTED = "isSelected"
DEFAULT_VALUE_IS_SELECTED = False


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
        return DictUtil.get(projectInfo, KEY_CMD_GROUPS)

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
