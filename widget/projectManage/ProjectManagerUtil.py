# -*- coding: utf-8 -*-
# python 3.x
# Filename: ProjectManagerUtil.py
# 定义一个ProjectManagerUtil类实现项目管理相关的工具方法
from util.DateUtil import DateUtil, DATE, DATE_TIME_COMPACT
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.StrUtil import StrUtil
from widget.projectManage.ProjectManager import *


class ProjectManagerUtil:
    @staticmethod
    def delInvalidDynParam(dynParams: [], optionGroups: [] = None):
        """
        删除无效的动态参数（选项列表中已经不存在了的）
        :param dynParams: 指令的动态参数列表
        :param optionGroups: 选项配置信息
        """
        if not dynParams:
            return
        if not optionGroups:
            dynParams.clear()
            return
        needDelDynParam = []
        for dynParam in dynParams:
            options = ListUtil.get(optionGroups, KEY_NAME, DictUtil.get(dynParam, KEY_OPTION_GROUP), KEY_OPTIONS)
            if options:
                if ListUtil.find(options, KEY_NAME, dynParam[KEY_OPTION]):
                    continue
            needDelDynParam.append(dynParam)
        if needDelDynParam:
            for item in needDelDynParam:
                ListUtil.remove(dynParams, item)
        pass

    @staticmethod
    def transformCmdParams(params: str, dynParams: [], optionGroups: [] = None):
        """
        动态参数值替换指令参数中的占位符
        :param params: 指令参数（包含动态参数占位符）
        :param dynParams: 动态参数列表
        :param optionGroups: 选项配置信息
        :return: 转换后的实际执行参数
        """
        realParams = params
        if not dynParams:
            return realParams
        if not optionGroups:
            dynParams.clear()
            return realParams

        for dynParam in dynParams:
            options = ListUtil.get(optionGroups, KEY_NAME, DictUtil.get(dynParam, KEY_OPTION_GROUP), KEY_OPTIONS)
            option = ListUtil.find(options, KEY_NAME, DictUtil.get(dynParam, KEY_OPTION))
            if option:
                value = option[KEY_OPTION_VALUES][option[KEY_DEFAULT]][KEY_VALUE]
                if value == MACRO_DATE:
                    value = DateUtil.nowTime(DATE)
                elif value == MACRO_DATETIME:
                    value = DateUtil.nowTime(DATE_TIME_COMPACT)
                if DictUtil.get(dynParam, KEY_NEED_CAPITALIZE, DEFAULT_VALUE_NEED_CAPITALIZE):
                    value = StrUtil.capitalize(value)
                realParams = realParams.replace(f"{{{dynParam[KEY_NAME]}}}", value)
        return realParams

    @staticmethod
    def extractConditionInputs(dynParams: [], optionGroups: [] = None):
        """
        从动态参数中提取上下文参数列表，用于自动识别输入指令
        :param dynParams: 动态参数列表
        :param optionGroups: 选项配置信息
        :return: 上下文参数列表
        """
        conditionInputs = []
        if not optionGroups:
            dynParams.clear()
            return conditionInputs
        ProjectManagerUtil.delInvalidDynParam(dynParams=dynParams, optionGroups=optionGroups)
        if not dynParams:
            return conditionInputs

        for dynParam in dynParams:
            options = ListUtil.get(optionGroups, KEY_NAME, DictUtil.get(dynParam, KEY_OPTION_GROUP), KEY_OPTIONS)
            option = ListUtil.find(options, KEY_NAME, DictUtil.get(dynParam, KEY_OPTION))
            if option:
                default = DictUtil.get(option, KEY_DEFAULT, -1)
                echo = DictUtil.get(option, KEY_ECHO, "")
                optionValues = DictUtil.get(option, KEY_OPTION_VALUES, [])
                if default == -1 or not optionValues:
                    continue
                # 选项的信息
                optionValue = optionValues[default]
                needCapitalize = DictUtil.get(dynParam, KEY_NEED_CAPITALIZE, DEFAULT_VALUE_NEED_CAPITALIZE)
                value = StrUtil.capitalize(optionValue[KEY_VALUE]) if needCapitalize else optionValue[KEY_VALUE]
                if value == MACRO_DATE:
                    value = DateUtil.nowTime(DATE)
                elif value == MACRO_DATETIME:
                    value = DateUtil.nowTime(DATE_TIME_COMPACT)
                if echo:
                    autoInput = DictUtil.get(optionValue, KEY_INPUT)
                    if not autoInput:
                        autoInput = value
                    conditionInput = ListUtil.findByKey(conditionInputs, echo)
                    if conditionInput:
                        conditionInput[echo] += conditionInput[echo] if autoInput == MACRO_REPEAT else autoInput
                    else:
                        conditionInputs.append({echo: autoInput})
        return conditionInputs

    @staticmethod
    def delInvalidPrecondition(preconditions: [], optionGroups: [] = None):
        """
        删除无效的前置条件（选项列表中已经不存在了的）
        :param preconditions: 指令的前置条件列表
        :param optionGroups: 选项配置信息
        """
        if not preconditions:
            return
        if not optionGroups:
            preconditions.clear()
            return
        needDelPreconditions = []
        for precondition in preconditions:
            options = ListUtil.get(optionGroups, KEY_NAME, DictUtil.get(precondition, KEY_OPTION_GROUP), KEY_OPTIONS)
            if options:
                if ListUtil.find(options, KEY_NAME, precondition[KEY_OPTION]):
                    continue
            needDelPreconditions.append(precondition)
        if needDelPreconditions:
            for item in needDelPreconditions:
                ListUtil.remove(preconditions, item)
        pass

    @staticmethod
    def transformPreconditionsTooltip(preconditionsLogic: str, preconditions: []):
        """
        转换前置条件tooltip显示
        :param preconditionsLogic: 前置条件间的逻辑关系
        :param preconditions: 指令的前置条件列表
        :return: 转换后的toolTip
        """
        toolTip = ""
        if not preconditions:
            return toolTip
        if preconditionsLogic == PRECONDITIONS_LOGIC_ALL:
            logic = "and"
        else:
            logic = "or"
        for index, precondition in enumerate(preconditions):
            if index == 0:
                toolTip += f"{precondition[KEY_OPTION_GROUP]}-{precondition[KEY_OPTION]} == {precondition[KEY_OPTION_VALUE]}"
            else:
                toolTip += f" {logic} {precondition[KEY_OPTION_GROUP]}-{precondition[KEY_OPTION]} == {precondition[KEY_OPTION_VALUE]}"
        return toolTip

    @staticmethod
    def isPreconditionsMatch(preconditionsLogic: str, preconditions: [], optionGroups: [] = None):
        """
        前置条件是否满足
        :param preconditionsLogic: 前置条件间的逻辑关系
        :param preconditions: 指令的前置条件列表
        :param optionGroups: 选项配置信息
        :return: True 执行该指令
        """
        match = True
        if not optionGroups:
            # 没有选项配置，前置条件无效
            preconditions.clear()
            return match
        # 删除已经失效的选项前置条件
        ProjectManagerUtil.delInvalidPrecondition(preconditions=preconditions, optionGroups=optionGroups)
        if not preconditions:
            return match

        matchResults = []
        for precondition in preconditions:
            options = ListUtil.get(optionGroups, KEY_NAME, DictUtil.get(precondition, KEY_OPTION_GROUP), KEY_OPTIONS)
            option = ListUtil.find(options, KEY_NAME, DictUtil.get(precondition, KEY_OPTION))
            if option:
                value = option[KEY_OPTION_VALUES][option[KEY_DEFAULT]][KEY_VALUE]
                matchResults.append(DictUtil.get(precondition, KEY_OPTION_VALUE, "") == value)
        if preconditionsLogic == PRECONDITIONS_LOGIC_ALL:
            match = True
        else:
            match = False
        for index, item in enumerate(matchResults):
            if preconditionsLogic == PRECONDITIONS_LOGIC_ALL:
                match = match and item
            else:
                match = match or item
        return match


if __name__ == '__main__':
    srcOptionGroups = [
        {'desc': '构建参数', 'id': '25ce396132a320ac6fb53346ab7d450f',
         'name': 'buildParams',
         'options': [
             {'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType',
              'optionValues': [
                  {'desc': '支持动态模块的打包', 'input': '', 'value': 'bundle'},
                  {'desc': '正常打全量包', 'input': '', 'value': 'assemble'}]},
             {'default': 2, 'desc': '打包环境渠道', 'echo': '请输入环境渠道',
              'name': 'productFlavors',
              'optionValues': [{'desc': '测试环境', 'input': 'C', 'value': 'staging'},
                               {'desc': '现网环境', 'input': 'A', 'value': 'product'},
                               {'desc': '镜像环境', 'input': 'B', 'value': 'mirror'}]},
             {'default': 0, 'desc': '打包类型 - debug、release', 'echo': '请输入打包类型',
              'name': 'buildType',
              'optionValues': [{'desc': 'debug包', 'input': 'A', 'value': 'debug'},
                               {'desc': 'release包', 'input': 'B',
                                'value': 'release'}]}]},
        {'desc': '构建参数1', 'id': '25ce396132a320ac6fb53346ab7d4111',
         'name': 'buildParams1',
         'options': [
             {'default': 0, 'desc': '打包指令', 'echo': '', 'name': 'packageType1',
              'optionValues': [
                  {'desc': '支持动态模块的打包', 'input': '', 'value': 'bundle'},
                  {'desc': '正常打全量包', 'input': '', 'value': 'assemble'}]},
             {'default': 1, 'desc': '打包环境渠道', 'echo': '请输入环境渠道',
              'name': 'productFlavors1',
              'optionValues': [{'desc': '测试环境', 'input': 'C', 'value': 'staging'},
                               {'desc': '现网环境', 'input': 'A', 'value': 'product'},
                               {'desc': '镜像环境', 'input': 'B', 'value': 'mirror'}]},
             {'default': 0, 'desc': '打包类型 - debug、release', 'echo': '请输入打包类型',
              'name': 'buildType1',
              'optionValues': [{'desc': 'debug包', 'input': 'A', 'value': 'debug'},
                               {'desc': 'release包', 'input': 'B',
                                'value': 'release'}]}]},
    ]
    srcDynParams = [{"name": "11", "desc": "11", "optionGroup": "buildParams", "option": "packageType", "needCapitalize": False},
                    {"name": "12", "desc": "12", "optionGroup": "buildParams", "option": "productFlavors", "needCapitalize": True},
                    {"name": "13", "desc": "13", "optionGroup": "buildParams", "option": "buildType", "needCapitalize": True},
                    {"name": "22", "desc": "22", "optionGroup": "buildParams", "option": "buildType1"},
                    {"name": "33", "desc": "33", "optionGroup": "buildParams3", "option": "buildType1"}]

    ProjectManagerUtil.delInvalidDynParam(dynParams=srcDynParams, optionGroups=srcOptionGroups)

    print(srcDynParams)

    srcParam = "gradlew {11}{12}{13} {22} {33}"
    print(ProjectManagerUtil.transformCmdParams(params=srcParam, dynParams=srcDynParams, optionGroups=srcOptionGroups), srcParam)
    print(ProjectManagerUtil.extractConditionInputs(dynParams=srcDynParams, optionGroups=srcOptionGroups))
