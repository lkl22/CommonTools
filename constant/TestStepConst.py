# -*- coding: utf-8 -*-
# python 3.x
# Filename: TestStepConst.py
# 定义一个TestStepConst常量类实现自动化测试相关常量的功能
import constant.const as const

const.STEP_TYPE_SINGLE_CLICK = 0
const.STEP_TYPE_DOUBLE_CLICK = 1
const.STEP_TYPE_LONG_CLICK = 2

const.STEP_TYPE_SWIPE_UP = 10
const.STEP_TYPE_SWIPE_DOWN = 11
const.STEP_TYPE_SWIPE_LEFT = 12
const.STEP_TYPE_SWIPE_RIGHT = 13

const.STEP_TYPE_FIND_ELEMENT = 20

const.STEP_TYPE_NAMES = ['click', 'swipe', 'find']
const.CLICK_TYPES = ['单击', '双击', '长按']
const.SWIPE_TYPES = ['上', '下', '左', '右']

const.KEY_XPATH = 'xpath'
const.KEY_X = 'x'
const.KEY_Y = 'y'
# 间隔时长
const.KEY_INTERVAL_TIME = 'intervalTime'
# 重复次数
const.KEY_REPEAT_NUM = 'repeatNum'

const.KEY_STEP_TYPE = 'type'
const.KEY_STEP_PARAMS = 'params'
