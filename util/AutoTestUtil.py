# -*- coding: utf-8 -*-
# python 3.x
# Filename: AutoTestUtil.py
# 定义一个AutoTestUtil工具类实现自动测试相关的功能
import time

from util.LogUtil import *
from util.Uiautomator import *
from constant.TestStepConst import *


class AutoTestUtil:
    def __init__(self, u: Uiautomator = None):
        self.u = u
        if not self.u:
            self.u = Uiautomator()

    def startTestStep(self, stepType: int, params: dict = {}, logCallback=None):
        """
        开始测试
        :param stepType: 测试类型
        :param params: 执行参数
        :param logCallback: 执行过程log回调
        """
        LogUtil.i('startTestStep', stepType, params)
        if logCallback:
            logCallback('startTestStep')
        if stepType // 10 == 0:
            self.startTestClickStep(stepType, params, logCallback)
        elif stepType // 10 == 1:
            self.startTestSwipeStep(stepType, params, logCallback)
        elif stepType // 10 == 2:
            self.startTestFindStep(stepType, params, logCallback)


    def startTestClickStep(self, stepType, params={}, logCallback=None):
        LogUtil.i('startTestClickStep', stepType, params)
        if logCallback:
            logCallback('startTestClickStep ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        clickFunc = self.u.click
        if stepType % 10 == 0:
            clickFunc = self.u.click
        elif stepType % 10 == 1:
            clickFunc = self.u.doubleClick
        elif stepType % 10 == 2:
            clickFunc = self.u.longClick
        res = clickFunc(x=params[const.KEY_X], y=params[const.KEY_Y], xpath=params[const.KEY_XPATH])
        if logCallback:
            logCallback(str.format('result: %s\n', str(res)))

    def startTestSwipeStep(self, stepType, params={}, logCallback=None):
        LogUtil.i('startTestSwipeStep', stepType, params)
        if logCallback:
            logCallback('startTestSwipeStep ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))

    def startTestFindStep(self, stepType, params={}, logCallback=None):
        LogUtil.i('startTestFindStep', stepType, params)
        if logCallback:
            logCallback('startTestFindStep ' + AutoTestUtil.stepName(stepType) + ' params: ' + str(params))
        xpath = params[const.KEY_XPATH]
        exists = self.u.existsByXpath(xpath)
        intervalTime = params[const.KEY_INTERVAL_TIME]
        repeatNum = params[const.KEY_REPEAT_NUM]
        LogUtil.i('startTestFindStep', stepType, params)
        while not exists and repeatNum > 0:
            if logCallback:
                logCallback('not find element: {} intervalTime: {} repeatNum: {}'.format(xpath, intervalTime, repeatNum))
            repeatNum -= 1
            exists = self.u.existsByXpath(xpath)
            time.sleep(intervalTime)
        if logCallback:
            logCallback('finished {}find element: {}\n'.format('' if exists else 'not ', xpath))
        LogUtil.i('startTestFindStep finished')

    @staticmethod
    def stepName(stepType: int):
        name = const.STEP_TYPE_NAMES[stepType // 10]
        if stepType // 10 == 0:
            name += '(' + const.CLICK_TYPES[stepType % 10] + ')'
        elif stepType // 10 == 1:
            name += '(' + const.SWIPE_TYPES[stepType % 10] + ')'
        return name


if __name__ == "__main__":
    t = AutoTestUtil()
