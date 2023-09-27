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
# 颜色
KEY_COLOR = 'color'
# item显示描述文案
KEY_DESC = 'desc'
# 主键，唯一
KEY_PRIMARY = 'primary'
# 默认值
KEY_DEFAULT = 'default'
# 数据列表
KEY_LIST = 'list'
# tableView title
KEY_TITLE = 'title'
KEY_NAME = 'name'

# 打开文件/目录属性key
KEY_CAPTION = 'caption'
KEY_DIRECTORY = 'directory'
KEY_FILTER = 'filter'
KEY_INITIAL_FILTER = 'initialFilter'

KEY_LOG = 'log'
KEY_TIME = 'time'

# 通用时间段控件属性
KEY_DATETIME_RANGE = 'datetimeRange'
# 当前日期时间格式
DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'
# 当前日期时间
KEY_DATETIME = 'datetime'
# 相对当前日期前多少s
KEY_BEFORE = 'before'
# 相对当前日期后多少s
KEY_AFTER = 'after'

# 通用时间格式控件属性
KEY_DATETIME_FORMAT_RULE = 'datetimeFormatRule'
# 文本中代表日期的起始位置，从下标0开始
KEY_START_INDEX = 'startIndex'
# 日期格式
KEY_DATETIME_FORMAT = 'datetimeFormat'

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

# QSpinBox相关属性key
KEY_MIN_VALUE = 'minValue'
KEY_MAX_VALUE = 'maxValue'
KEY_STEP = 'step'
KEY_PREFIX = 'prefix'
KEY_SUFFIX = 'suffix'
KEY_INT_BASE = 'intBase'

# 打开文件弹框参数
KEY_FILE_PARAM = 'fileParam'
# 打开目录弹框参数
KEY_DIR_PARAM = 'dirParam'

# widget类型 - 输入文本框
TYPE_LINE_EDIT = 'lineEdit'
# widget类型 - 计数器控件 - 用于整数的显示和输入，一般显示十进制数，也可以显示二进制、十六进制的数，而且可以在显示框中增加前缀或后缀
TYPE_SPIN_BOX = 'SpinBox'
# widget类型 - 选择文件
TYPE_SELECT_FILE = 'selectFile'
# widget类型 - 选择目录
TYPE_SELECT_DIR = 'selectDir'
# widget类型 - tableView
TYPE_TABLE_VIEW = 'tableView'
