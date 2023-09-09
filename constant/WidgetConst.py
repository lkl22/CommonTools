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

# 通用弹框属性
# 存储数据的key
KEY_ITEM_KEY = 'key'
# 显示widget的label文案
KEY_ITEM_LABEL = 'label'
# 显示widget的类型
KEY_ITEM_TYPE = 'type'
# 数据是否时唯一的，默认False
KEY_IS_UNIQUE = 'isUnique'
# 数据是否可选的，默认False
KEY_IS_OPTIONAL = 'isOptional'
# 显示widget的toolTip
KEY_TOOL_TIP = 'toolTip'

KEY_FILE_PARAM = 'fileParam'
KEY_DIR_PARAM = 'dirParam'

TYPE_LINE_EDIT = 'lineEdit'
TYPE_SELECT_FILE = 'selectFile'
TYPE_SELECT_DIR = 'selectDir'
