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
    const.GROUP_BOX_MARGIN_TOP = 20

# widget需要显示的文案
KEY_SHOW_TEXT = 'showText'
# widget关联的数据
KEY_DATA = 'data'
# icon颜色
KEY_COLOR = 'color'
# item显示描述文案
KEY_DESC = 'desc'
# 主键，唯一
KEY_PRIMARY = 'primary'
# 默认值
KEY_DEFAULT = 'default'
# tableView title
KEY_TITLE = 'title'

# 打开文件/目录属性key
KEY_CAPTION = 'caption'
KEY_DIRECTORY = 'directory'
KEY_FILTER = 'filter'
KEY_INITIAL_FILTER = 'initialFilter'
