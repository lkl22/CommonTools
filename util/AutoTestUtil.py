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

    def startTestStep(self, stepType: int, params: dict = {}, isRtl=False, logCallback=None):
        """
        开始测试
        :param stepType: 测试类型
        :param params: 执行参数
        :param isRtl: 是否rtl镜像
        :param logCallback: 执行过程log回调
        """
        LogUtil.i('startTestStep', stepType, params)
        if logCallback:
            logCallback('startTestStep')
        if stepType // 10 == 0:
            return self.startTestClickStep(stepType=stepType, params=params, isRtl=isRtl, logCallback=logCallback)
        elif stepType // 10 == 1:
            return self.startTestSwipeStep(stepType=stepType, params=params, isRtl=isRtl, logCallback=logCallback)
        elif stepType // 10 == 2:
            return self.startTestFindStep(stepType=stepType, params=params, logCallback=logCallback)
        return False

    def startTestClickStep(self, stepType, params={}, isRtl=False, logCallback=None):
        """
        开始测试点击事件
        :param stepType: 测试类型
        :param params: 执行参数
        :param isRtl: 是否rtl镜像
        :param logCallback: 执行过程log回调
        """
        log = 'startTestClickStep {} params: {}'.format(AutoTestUtil.stepName(stepType), params)
        self.print(log, logCallback)
        clickFunc = self.u.click
        if stepType % 10 == 0:
            clickFunc = self.u.click
        elif stepType % 10 == 1:
            clickFunc = self.u.doubleClick
        elif stepType % 10 == 2:
            clickFunc = self.u.longClick
        x = params[const.KEY_X]
        y = params[const.KEY_Y]

        if isRtl:
            size = self.u.windowSize()
            (w, h) = size
            x = self.posRtl(x, w)

        res = clickFunc(x=x, y=y, xpath=params[const.KEY_XPATH])
        log = 'result: {}\n'.format(res)
        self.print(log, logCallback)
        return res

    def startTestSwipeStep(self, stepType, params={}, isRtl=False, logCallback=None):
        """
        开始测试滑动事件
        :param stepType: 测试类型
        :param params: 执行参数
        :param isRtl: 是否rtl镜像
        :param logCallback: 执行过程log回调
        """
        log = 'startTestSwipeStep {} params: {}'.format(AutoTestUtil.stepName(stepType), params)
        self.print(log, logCallback)
        size = self.u.windowSize()
        if not size:
            return False
        (w, h) = size
        log = 'screen size w: {} h: {}'.format(w, h)
        self.print(log, logCallback)
        fx = params[const.KEY_X]
        fy = params[const.KEY_Y]
        distance = params[const.KEY_DISTANCE]
        duration = params[const.KEY_DURATION]
        fx = self.posRel2Abs(fx, w)
        fy = self.posRel2Abs(fy, h)
        if fx >= w or fy >= h:
            self.print('滑动起始坐标不在屏幕范围内请重新设置', logCallback)
            return False

        if isRtl:
            if stepType == const.STEP_TYPE_SWIPE_LEFT:
                stepType = const.STEP_TYPE_SWIPE_RIGHT
                fx = self.posRtl(fx, w)
            elif stepType == const.STEP_TYPE_SWIPE_RIGHT:
                stepType = const.STEP_TYPE_SWIPE_LEFT
                fx = self.posRtl(fx, w)

        tx = fx
        ty = fy
        if stepType % 10 // 2 == 0:
            # 上下
            distance = self.posRel2Abs(distance, h)
        else:
            # 左右
            distance = self.posRel2Abs(distance, w)
        log = 'start position ({}, {}) distance {} duration {} ms'.format(fx, fy, distance, duration * 1000)
        self.print(log, logCallback)

        if stepType % 10 == 0:
            # 上
            ty -= distance
            while ty < 0:
                self.startSwipe(fx, fy, tx, 0, duration, logCallback)
                offset = fy
                distance -= offset
                ty = fy - distance

            if ty > 0:
                self.startSwipe(fx, fy, tx, ty, duration, logCallback)
            return True
        elif stepType % 10 == 1:
            # 下
            ty += distance
            while ty > h:
                self.startSwipe(fx, fy, tx, h, duration, logCallback)
                offset = h - fy
                distance -= offset
                ty = fy + distance

            if ty > fy:
                self.startSwipe(fx, fy, tx, ty, duration, logCallback)
            return True
        elif stepType % 10 == 2:
            # 左
            tx -= distance
            while tx < 0:
                self.startSwipe(fx, fy, 0, ty, duration, logCallback)
                offset = fx
                distance -= offset
                tx = fx - distance

            if tx > 0:
                self.startSwipe(fx, fy, tx, ty, duration, logCallback)
            return True
        elif stepType % 10 == 3:
            # 右
            tx += distance
            while tx > w:
                self.startSwipe(fx, fy, w, ty, duration, logCallback)
                offset = w - fx
                distance -= offset
                tx = fx + distance

            if tx > fx:
                self.startSwipe(fx, fy, tx, ty, duration, logCallback)
            return True
        return False

    def startSwipe(self, fx, fy, tx, ty, duration, logCallback=None):
        """
        开始滑动
        :param fx: 起始x坐标
        :param fy: 起始y坐标
        :param tx: 终止x坐标
        :param ty: 终止y坐标
        :param duration: 滑动时长
        :param logCallback: 执行过程log回调
        """
        self.u.swipe(fx, fy, tx, ty, duration=duration)
        log = 'swipe from ({}, {}) to ({}, {})'.format(fx, fy, tx, ty)
        self.print(log, logCallback)

    def posRel2Abs(self, pos, size):
        """
        将百分比坐标转换为像素坐标
        :param pos: 坐标位置
        :param size: 宽度/高度
        :return: 像素坐标
        """
        assert pos >= 0

        if pos < 1:
            pos = int(size * pos)
        return pos

    def posRtl(self, pos, size):
        """
        将坐标转换为rtl镜像坐标
        :param pos: 坐标位置
        :param size: 宽度/高度
        :return: 镜像坐标
        """
        assert pos >= 0

        if pos < 1:
            pos = 1 - pos
        else:
            pos = size - pos
        return pos

    def startTestFindStep(self, stepType, params={}, logCallback=None):
        """
        开始测试查找事件
        :param stepType: 测试类型
        :param params: 执行参数
        :param logCallback: 执行过程log回调
        """
        log = 'startTestFindStep {} params: {}'.format(AutoTestUtil.stepName(stepType), params)
        self.print(log, logCallback)
        xpath = params[const.KEY_XPATH]
        exists = self.u.existsByXpath(xpath)
        intervalTime = params[const.KEY_INTERVAL_TIME]
        repeatNum = params[const.KEY_REPEAT_NUM]
        while not exists and repeatNum > 0:
            log = 'not find element: {} intervalTime: {} repeatNum: {}'.format(xpath, intervalTime, repeatNum)
            self.print(log, logCallback)
            repeatNum -= 1
            exists = self.u.existsByXpath(xpath)
            time.sleep(intervalTime)
        log = 'finished {}find element: {}\n'.format('' if exists else 'not ', xpath)
        self.print(log, logCallback)
        return exists

    def print(self, log: str, callback=None):
        """
        打印log并回调log结果
        :param log: log
        :param callback: 回调函数
        """
        LogUtil.d(log)
        if callback:
            callback(log)
        pass

    @staticmethod
    def stepName(stepType: int):
        """
        将步骤类型转换为步骤名称
        :param stepType: 步骤类型
        :return: 步骤名称
        """
        name = const.STEP_TYPE_NAMES[stepType // 10]
        if stepType // 10 == 0:
            name += '(' + const.CLICK_TYPES[stepType % 10] + ')'
        elif stepType // 10 == 1:
            name += '(' + const.SWIPE_TYPES[stepType % 10] + ')'
        return name


if __name__ == "__main__":
    t = AutoTestUtil()
