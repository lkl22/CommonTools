# -*- coding: utf-8 -*-
# python 3.x
# Filename: TextTransformDialog.py
# 定义一个TextTransformDialog类实现文本转换功能
import sys

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DictUtil import DictUtil
from util.EvalUtil import EvalUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.MD5Util import MD5Util
from util.OperaIni import OperaIni
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTextEdit import CommonTextEdit

TAG = "TextTransformDialog"

KEY_SECTION = 'TextTransform'
KEY_CONFIGS = 'configs'
KEY_LIST = 'list'
KEY_DATAS = 'datas'
# value解析函数映射
KEY_TRANSFORM_FUNC = 'transformFunc'


class TextTransformDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        TextTransformDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        TextTransformDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Init Text Transform Dialog")
        self.setObjectName("TextTransformDialog")
        self.resize(TextTransformDialog.WINDOW_WIDTH, TextTransformDialog.WINDOW_HEIGHT)
        # self.setFixedSize(TextTransformDialog.WINDOW_WIDTH, TextTransformDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="文本转换功能"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__configs = JsonUtil.decode(self.__operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})
        self.__defaultConfigName = DictUtil.get(self.__configs, KEY_DEFAULT, '')
        self.__config = JsonUtil.decode(self.__operaIni.getValue(MD5Util.md5(self.__defaultConfigName), KEY_SECTION),
                                        {})

        self.__datas = DictUtil.get(self.__config, KEY_DATAS, [])
        self.__defaultData = DictUtil.get(self.__config, KEY_DEFAULT, '')
        self.__transformFunc = DictUtil.get(self.__config, KEY_TRANSFORM_FUNC, '')

        self.__asyncFuncManager = AsyncFuncManager()

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.__configComboBox = CommonComboBox(label='选择配置', default=self.__defaultConfigName,
                                               groupList=DictUtil.get(self.__configs, KEY_LIST, []),
                                               isEditable=True, dataChanged=self.__configChanged)
        vbox.addWidget(self.__configComboBox)
        self.__datasComboBox = CommonComboBox(label='需要转换的数据', default=self.__defaultData,
                                              groupList=self.__datas,
                                              isEditable=True,
                                              maxWidth=int(WidgetUtil.getScreenWidth() * 0.6))
        vbox.addWidget(self.__datasComboBox)

        self.__transformFuncLineEdit = CommonLineEdit(label='请输入文本转换函数', text=self.__transformFunc,
                                                      toolTip='输入文本转换代码，输入参数text变量，输出结果到res变量')
        vbox.addWidget(self.__transformFuncLineEdit)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(self, text="转换数据", onClicked=self.__transformData))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.__textEdit = CommonTextEdit()
        vbox.addWidget(self.__textEdit, 1)

        # self.setWindowModality(Qt.ApplicationModal)
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
        self.__transformFunc = DictUtil.get(self.__config, KEY_TRANSFORM_FUNC, '')

        self.__datasComboBox.updateData(self.__defaultData, self.__datas)
        self.__transformFuncLineEdit.updateData(self.__transformFunc)

        self.__saveConfigs()
        pass

    def __saveConfigs(self):
        configDatas = {KEY_DEFAULT: self.__configComboBox.getData(), KEY_LIST: self.__configComboBox.getGroupList()}
        self.__operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(configDatas, ensureAscii=False))
        configData = {
            KEY_DEFAULT: self.__datasComboBox.getData(),
            KEY_DATAS: self.__datasComboBox.getGroupList(),
            KEY_TRANSFORM_FUNC: self.__transformFuncLineEdit.getData()
        }
        self.__operaIni.addItem(KEY_SECTION, MD5Util.md5(configDatas[KEY_DEFAULT]),
                                JsonUtil.encode(configData, ensureAscii=False))
        self.__operaIni.saveIni()
        pass

    def __transformData(self):
        config = self.__configComboBox.getData()
        if not config:
            WidgetUtil.showErrorDialog(message="请添加配置")
            return
        data = self.__datasComboBox.getData()
        if not data:
            WidgetUtil.showErrorDialog(message="请添加需要解析的数据")
            return
        transformFunc = self.__transformFuncLineEdit.getData()
        if not transformFunc:
            WidgetUtil.showErrorDialog(message="请添加文本转换函数代码")
            return
        configData = {
            KEY_DEFAULT: data,
            KEY_DATAS: self.__datasComboBox.getGroupList(),
            KEY_TRANSFORM_FUNC: transformFunc
        }
        self.__saveConfigs()

        self.__textEdit.clear()
        self.__asyncFuncManager.asyncExec(target=self.__transformText, kwargs=configData)
        pass

    def __transformText(self, **configData):
        LogUtil.i(TAG, '__transformText start: ', configData)
        parseData = configData[KEY_DEFAULT]
        transformFunc = configData[KEY_TRANSFORM_FUNC]
        myLocals = {'text': parseData, 'res': ''}
        execResult = EvalUtil.exec(transformFunc, locals=myLocals)
        res = myLocals.get('res') + (str(execResult) if execResult else '')
        LogUtil.i(TAG, '__transformText res: ', res)
        self.__textEdit.standardOutputOne(res, ColorEnum.Blue.value)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextTransformDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
