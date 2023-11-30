# -*- coding: utf-8 -*-
# python 3.x
# Filename: TLVParseDialog.py
# 定义一个TLVParseDialog类实现TLV格式数据解析功能
import sys

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DictUtil import DictUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.MD5Util import MD5Util
from util.OperaIni import OperaIni
from util.TLV import TLV
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonTableView import CommonTableView
from widget.custom.CommonTextEdit import CommonTextEdit

TAG = "TLVParseDialog"
KEY_TAG = 'tag'
KEY_LENGTH_TAG = 'lengthTag'
KEY_CHAR_COUNT = 'charCount'
KEY_VALUE_PARSE_TAG = 'valueParseTag'
KEY_VALUE_PARSE_FUNC = 'valueParseFunc'
TAG_HEADERS = {KEY_TAG: {KEY_TITLE: "Tag名"}, KEY_DESC: {KEY_TITLE: "Tag描述"}}
LENGTH_HEADERS = {KEY_LENGTH_TAG: {KEY_TITLE: "Length Tag"}, KEY_CHAR_COUNT: {KEY_TITLE: "长度占用字符数"}}
VALUE_PARSE_HEADERS = {KEY_VALUE_PARSE_TAG: {KEY_TITLE: "Value Parse Tag"},
                       KEY_VALUE_PARSE_FUNC: {KEY_TITLE: "value解析处理函数"}}

KEY_SECTION = 'TLVParse'
KEY_CONFIGS = 'configs'
KEY_LIST = 'list'
KEY_DATAS = 'datas'
# tag标签
KEY_TAGS = 'tags'
# 长度映射
KEY_LENGTH_MAP = 'lengthMap'
# value解析函数映射
KEY_VALUE_PARSE_FUNC_MAP = 'valueParseFuncMap'


class TLVParseDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        TLVParseDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.85)
        TLVParseDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init TLV Parse Dialog")
        self.setObjectName("TLVParseDialog")
        self.resize(TLVParseDialog.WINDOW_WIDTH, TLVParseDialog.WINDOW_HEIGHT)
        # self.setFixedSize(TLVParseDialog.WINDOW_WIDTH, TLVParseDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="TLV数据格式解析"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__configs = JsonUtil.decode(self.__operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})
        self.__defaultConfigName = DictUtil.get(self.__configs, KEY_DEFAULT, '')
        self.__config = JsonUtil.decode(self.__operaIni.getValue(MD5Util.md5(self.__defaultConfigName), KEY_SECTION),
                                        {})

        self.__datas = DictUtil.get(self.__config, KEY_DATAS, [])
        self.__defaultData = DictUtil.get(self.__config, KEY_DEFAULT, '')
        self.__tags = DictUtil.get(self.__config, KEY_TAGS, [])
        self.__lengthMap = DictUtil.get(self.__config, KEY_LENGTH_MAP, [])
        self.__valueParseFuncMap = DictUtil.get(self.__config, KEY_VALUE_PARSE_FUNC_MAP, [])
        self.__asyncFuncManager = AsyncFuncManager()

        vbox = WidgetUtil.createVBoxLayout(spacing=10)
        self.__configComboBox = CommonComboBox(label='选择配置', default=self.__defaultConfigName,
                                               groupList=DictUtil.get(self.__configs, KEY_LIST, []),
                                               isEditable=True, maxWidth=int(WidgetUtil.getScreenWidth() * 0.3),
                                               dataChanged=self.__configChanged)
        vbox.addWidget(self.__configComboBox)
        self.__datasComboBox = CommonComboBox(label='需要解析的数据', default=self.__defaultData,
                                              groupList=self.__datas,
                                              isEditable=True, maxWidth=int(WidgetUtil.getScreenWidth() * 0.3))
        vbox.addWidget(self.__datasComboBox)
        self.__tagTableView = CommonTableView(addBtnTxt="添加Tag", headers=TAG_HEADERS,
                                              items=self.__tags,
                                              addOrEditItemFunc=self.__addOrEditTagFunc)

        vbox.addWidget(self.__tagTableView)

        self.__lengthTagTableView = CommonTableView(addBtnTxt="添加Length占用字符数映射关系", headers=LENGTH_HEADERS,
                                                    items=self.__lengthMap,
                                                    addOrEditItemFunc=self.__addOrEditLengthTagFunc,
                                                    toolTip='特殊字符代表长度占用字符数的映射关系表')

        vbox.addWidget(self.__lengthTagTableView)

        self.__valueParseTableView = CommonTableView(addBtnTxt="添加Value转换函数", headers=VALUE_PARSE_HEADERS,
                                                     items=self.__valueParseFuncMap,
                                                     addOrEditItemFunc=self.__addOrEditValueParseFunc,
                                                     toolTip='tag对应value转换函数，转换为便于识别的函数')

        vbox.addWidget(self.__valueParseTableView)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addWidget(WidgetUtil.createPushButton(self, text="解析TLV数据", onClicked=self.__parseTLVData))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox.addLayout(vbox, 1)
        self.__textEdit = CommonTextEdit()
        hbox.addWidget(self.__textEdit, 2)

        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __configChanged(self, config, deleteData):
        LogUtil.d(TAG, '__configChanged cur data', config, 'delete data', deleteData)
        if deleteData:
            self.__operaIni.removeItem(KEY_SECTION, MD5Util.md5(deleteData))
        self.__defaultConfigName = config
        self.__config = JsonUtil.decode(self.__operaIni.getValue(MD5Util.md5(config), KEY_SECTION), {})

        self.__datas = DictUtil.get(self.__config, KEY_DATAS, [])
        self.__defaultData = DictUtil.get(self.__config, KEY_DEFAULT, '')
        self.__tags = DictUtil.get(self.__config, KEY_TAGS, [])
        self.__lengthMap = DictUtil.get(self.__config, KEY_LENGTH_MAP, [])
        self.__valueParseFuncMap = DictUtil.get(self.__config, KEY_VALUE_PARSE_FUNC_MAP, [])

        self.__datasComboBox.updateData(self.__defaultData, self.__datas)
        self.__tagTableView.updateData(self.__tags)
        self.__lengthTagTableView.updateData(self.__lengthMap)
        self.__valueParseTableView.updateData(self.__valueParseFuncMap)
        self.__saveConfigs()
        pass

    def __saveConfigs(self):
        configDatas = {KEY_DEFAULT: self.__configComboBox.getData(), KEY_LIST: self.__configComboBox.getGroupList()}
        self.__operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(configDatas, ensureAscii=False))
        configData = {
            KEY_DEFAULT: self.__datasComboBox.getData(),
            KEY_DATAS: self.__datasComboBox.getGroupList(),
            KEY_TAGS: self.__tagTableView.getData(),
            KEY_LENGTH_MAP: self.__lengthTagTableView.getData(),
            KEY_VALUE_PARSE_FUNC_MAP: self.__valueParseTableView.getData(),
        }
        self.__operaIni.addItem(KEY_SECTION, MD5Util.md5(configDatas[KEY_DEFAULT]),
                                JsonUtil.encode(configData, ensureAscii=False))
        self.__operaIni.saveIni()
        pass

    def __addOrEditTagFunc(self, callback, default=None, items=None, isAdd=False):
        if not default and not self.__defaultConfigName:
            WidgetUtil.showErrorDialog(message="请先添加配置项")
            return
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑Tag',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_TAG,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: 'Tag名：',
                                           KEY_TOOL_TIP: '请输入Tag名',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_DESC,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '请输入Tag规则描述',
                                           KEY_IS_OPTIONAL: True
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isAdd=isAdd,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __addOrEditLengthTagFunc(self, callback, default=None, items=None, isAdd=False):
        if not default and not self.__defaultConfigName:
            WidgetUtil.showErrorDialog(message="请先添加配置项")
            return
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑Length字符数映射关系表',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_LENGTH_TAG,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: 'Length特殊字符：',
                                           KEY_TOOL_TIP: '请输入代表长度占用字符个数的特殊字符',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_CHAR_COUNT,
                                           KEY_ITEM_TYPE: TYPE_SPIN_BOX,
                                           KEY_ITEM_LABEL: '请输入占用字符数',
                                           KEY_MIN_VALUE: 2,
                                           KEY_MAX_VALUE: 10,
                                           KEY_STEP: 2,
                                           KEY_SUFFIX: ' chars'
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isAdd=isAdd,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __addOrEditValueParseFunc(self, callback, default=None, items=None, isAdd=False):
        if not default and not self.__defaultConfigName:
            WidgetUtil.showErrorDialog(message="请先添加配置项")
            return
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑Value转换函数',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_VALUE_PARSE_TAG,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: 'TAG名：',
                                           KEY_TOOL_TIP: '请输入Tag名',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_VALUE_PARSE_FUNC,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '请输入value转换函数',
                                           KEY_TOOL_TIP: '请输入value转换函数，输入参数value变量，输出结果到res变量'
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isAdd=isAdd,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __parseTLVData(self):
        tags = self.__tagTableView.getData()
        if not tags:
            WidgetUtil.showErrorDialog(message="请添加Tag标签")
            return
        data = self.__datasComboBox.getData()
        if not data:
            WidgetUtil.showErrorDialog(message="请添加需要解析的数据")
            return
        configData = {
            KEY_DEFAULT: data,
            KEY_DATAS: self.__datasComboBox.getGroupList(),
            KEY_TAGS: tags,
            KEY_LENGTH_MAP: self.__lengthTagTableView.getData(),
            KEY_VALUE_PARSE_FUNC_MAP: self.__valueParseTableView.getData(),
        }
        self.__saveConfigs()

        self.__textEdit.clear()
        self.__asyncFuncManager.asyncExec(target=self.__parseTLV, kwargs=configData)
        pass

    def __parseTLV(self, **configData):
        LogUtil.i(TAG, '__parseTLV', configData)
        parseData = configData[KEY_DEFAULT]
        tags = [item[KEY_TAG] for item in configData[KEY_TAGS]]
        lengthMap = {}
        for item in configData[KEY_LENGTH_MAP]:
            lengthMap[item[KEY_LENGTH_TAG]] = item[KEY_CHAR_COUNT]
        vPrintFuncs = {}
        for item in configData[KEY_VALUE_PARSE_FUNC_MAP]:
            vPrintFuncs[item[KEY_VALUE_PARSE_TAG]] = item[KEY_VALUE_PARSE_FUNC]
        LogUtil.i(TAG, '__parseTLV', parseData, tags, lengthMap, vPrintFuncs)
        tlv = TLV(tags=tags, LLengthMap=lengthMap, VPrintFuncs=vPrintFuncs)
        try:
            self.__textEdit.standardOutputOne(tlv.toString(tlv.parse(parseData)).replace(' ', '&nbsp;'),
                                              ColorEnum.BLUE.value)
        except Exception as err:
            self.__textEdit.standardOutputOne(str(err), ColorEnum.RED.value)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TLVParseDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
