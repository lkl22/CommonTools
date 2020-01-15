# -*- coding: utf-8 -*-
# python 3.x
# Filename: WidgetConst.py
# 定义一个Widget常量类实现Widget常量的功能
from util.PlatformUtil import *
import constant.const as const

const.PADDING = 10
const.HEIGHT = 25
const.HEIGHT_OFFSET = const.PADDING + const.HEIGHT
if PlatformUtil.isMac():
    const.GROUP_BOX_MARGIN_TOP = 30
else:
    const.GROUP_BOX_MARGIN_TOP = 10
