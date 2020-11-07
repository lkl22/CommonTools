# -*- coding: utf-8 -*-
# python 3.x
# Filename: AutoTestUtil.py
# 定义一个AutoTestUtil工具类实现自动测试相关的功能

from util.LogUtil import *
from util.Uiautomator import *
from constant.TestStepConst import *


class AutoTestUtil:
    def __init__(self, u: Uiautomator = None):
        self.u = u
        if not self.u:
            self.u = Uiautomator()

    def startTestStep(self, stepType, params={}):
        LogUtil.i('startTestStep', stepType, params)
        if stepType // 10 == 0:
            self.startTestClickStep(stepType, params)
        elif stepType // 10 == 1:
            self.startTestSwipeStep(stepType, params)
        elif stepType // 10 == 2:
            self.startTestFindStep(stepType, params)


    def startTestClickStep(self, stepType, params={}):
        LogUtil.i('startTestClickStep', stepType, params)
        clickFunc = self.u.click
        if stepType % 10 == 0:
            clickFunc = self.u.click
        elif stepType % 10 == 1:
            clickFunc = self.u.doubleClick
        elif stepType % 10 == 2:
            clickFunc = self.u.longClick
        clickFunc(x=params['x'], y=params['y'], xpath=params['xpath'])

    def startTestSwipeStep(self, stepType, params={}):
        LogUtil.i('startTestSwipeStep', stepType, params)

    def startTestFindStep(self, stepType, params={}):
        LogUtil.i('startTestFindStep', stepType, params)


if __name__ == "__main__":
    t = AutoTestUtil()
