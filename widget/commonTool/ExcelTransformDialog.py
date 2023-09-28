# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelTransformDialog.py
# 定义一个ExcelTransformDialog类实现Excel转换功能
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
from util.excel.ExcelOperator import ExcelOperator
from widget.custom.CommonCheckBoxs import CommonCheckBoxs
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.DragInputWidget import DragInputWidget

TAG = "ExcelTransformDialog"

KEY_SECTION = 'ExcelTransform'
KEY_CONFIGS = 'configs'
# 源Excel文件
KEY_SRC_FP = 'srcFp'
KEY_SRC_SHEET_NAME = 'srcSheetName'
# 表格header所在的行，默认从1开始
KEY_SRC_HEADER_ROW = 'srcHeaderRow'
# header数据
KEY_SRC_HEADERS = 'srcHeaders'
# 选择的header
KEY_SRC_SELECT_HEADER = 'srcSelectHeader'

# 目标Excel文件存储路径
KEY_DST_DP = 'dstDp'
KEY_DST_SHEET_NAME = 'dstSheetName'
KEY_DST_HEADER_ROW = 'dstHeaderRow'


class ExcelTransformDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        ExcelTransformDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        ExcelTransformDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Init Text Transform Dialog")
        self.setObjectName("ExcelTransformDialog")
        self.resize(ExcelTransformDialog.WINDOW_WIDTH, ExcelTransformDialog.WINDOW_HEIGHT)
        # self.setFixedSize(ExcelTransformDialog.WINDOW_WIDTH, ExcelTransformDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="文本转换功能"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__configs = JsonUtil.decode(self.__operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})
        self.__defaultConfigName = DictUtil.get(self.__configs, KEY_DEFAULT, '')
        self.__config = JsonUtil.decode(self.__operaIni.getValue(MD5Util.md5(self.__defaultConfigName), KEY_SECTION),
                                        {})

        self.__asyncFuncManager = AsyncFuncManager()

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.__configComboBox = CommonComboBox(label='选择配置', default=self.__defaultConfigName,
                                               groupList=DictUtil.get(self.__configs, KEY_LIST, []),
                                               isEditable=True, dataChanged=self.__configChanged)
        vbox.addWidget(self.__configComboBox)
        labelMinSize = QSize(120, 0)
        self.__srcFpWidget = DragInputWidget(label='请选择源Excel文件',
                                             fileParam={KEY_CAPTION: '选择源Excel文件', KEY_FILTER: '*.xls;*.xlsx'},
                                             labelMinSize=labelMinSize)
        vbox.addWidget(self.__srcFpWidget)

        splitter = WidgetUtil.createSplitter(self)
        self.__srcSheetNameWidget = CommonLineEdit(label='表名')
        splitter.addWidget(self.__srcSheetNameWidget)
        self.__srcHeaderRowWidget = CommonSpinBox(label='Title行', minValue=1, maxValue=10, prefix='第 ', suffix=' 行')
        splitter.addWidget(self.__srcHeaderRowWidget)
        splitter.addWidget(WidgetUtil.createPushButton(self, text='Get', toolTip='获取Title信息，展示在下方，可以选择需要提取出来的数据列',
                                                       onClicked=self.__getSrcHeader))
        vbox.addWidget(splitter)

        self.__srcSelectHeaderCheckBoxs = CommonCheckBoxs(label='选择需要提取数据的Title',
                                                          buttonClicked=self.__srcSelectHeaderChanged)
        vbox.addWidget(self.__srcSelectHeaderCheckBoxs)

        vbox.addItem(WidgetUtil.createVSpacerItem())
        self.__updateUi()
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

        self.__updateUi()
        self.__saveConfigs()
        pass

    def __updateUi(self):
        srcFp = DictUtil.get(self.__config, KEY_SRC_FP)
        srcSheetName = DictUtil.get(self.__config, KEY_SRC_SHEET_NAME)
        srcHeaderRow = DictUtil.get(self.__config, KEY_SRC_HEADER_ROW, 1)
        srcHeaders = DictUtil.get(self.__config, KEY_SRC_HEADERS, [])
        srcSelectHeader = DictUtil.get(self.__config, KEY_SRC_SELECT_HEADER, [])

        dstDp = DictUtil.get(self.__config, KEY_DST_DP)
        dstSheetName = DictUtil.get(self.__config, KEY_DST_SHEET_NAME)
        dstHeaderRow = DictUtil.get(self.__config, KEY_DST_HEADER_ROW)

        self.__srcFpWidget.updateData(srcFp)
        self.__srcSheetNameWidget.updateData(srcSheetName)
        self.__srcHeaderRowWidget.updateData(srcHeaderRow)
        self.__srcSelectHeaderCheckBoxs.updateData(groupList=srcHeaders, defaultValue=srcSelectHeader)
        pass

    def __getSrcHeader(self):
        srcFp, srcSheetName, srcHeaderRow = self.__checkSrcConfig()
        if not srcFp:
            return
        LogUtil.d(TAG, '__getSrcHeader', srcFp, 'sheetName', srcSheetName, 'titleRow', srcHeaderRow)
        res = ExcelOperator.getExcelHeaderData(srcFp, srcSheetName, srcHeaderRow - 1)
        if type(res) == str:
            WidgetUtil.showErrorDialog(message=f"配置不正确。（{res}）")
            return
        LogUtil.d(TAG, '__getSrcHeader', res)
        srcSelectHeader = DictUtil.get(self.__config, KEY_SRC_SELECT_HEADER, [])
        self.__config[KEY_SRC_HEADERS] = res
        self.__srcSelectHeaderCheckBoxs.updateData(groupList=res, defaultValue=srcSelectHeader)
        pass

    def __srcSelectHeaderChanged(self, data):
        self.__config[KEY_SRC_SELECT_HEADER] = data
        self.__saveConfigs()
        pass

    def __checkSrcConfig(self):
        config = self.__configComboBox.getData()
        if not config:
            WidgetUtil.showErrorDialog(message="请选择配置")
            return None, None, None
        srcFp = self.__srcFpWidget.getData()
        if not srcFp:
            WidgetUtil.showErrorDialog(message="请选择源Excel文件")
            return None, None, None
        srcSheetName = self.__srcSheetNameWidget.getData()
        if not srcSheetName:
            WidgetUtil.showErrorDialog(message="请输入源Excel文件里要处理的表名")
            return None, None, None
        srcHeaderRow = self.__srcHeaderRowWidget.getData()
        self.__saveConfigs()
        return srcFp, srcSheetName, srcHeaderRow

    def __saveConfigs(self):
        configDatas = {KEY_DEFAULT: self.__configComboBox.getData(), KEY_LIST: self.__configComboBox.getGroupList()}
        self.__operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(configDatas, ensureAscii=False))
        configData = {
            KEY_SRC_FP: self.__srcFpWidget.getData(),
            KEY_SRC_SHEET_NAME: self.__srcSheetNameWidget.getData(),
            KEY_SRC_HEADER_ROW: self.__srcHeaderRowWidget.getData(),
            KEY_SRC_HEADERS: self.__srcSelectHeaderCheckBoxs.getGroupData(),
            KEY_SRC_SELECT_HEADER: self.__srcSelectHeaderCheckBoxs.getData()
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
            # KEY_DATAS: self.__datasComboBox.getGroupList(),
            # KEY_TRANSFORM_FUNC: transformFunc
        }
        self.__saveConfigs()

        self.__asyncFuncManager.asyncExec(target=self.__transformText, kwargs=configData)
        pass

    def __transformText(self, **configData):
        LogUtil.i(TAG, '__transformText start: ', configData)
        # LogUtil.i(TAG, '__transformText res: ', res)
        # self.__textEdit.standardOutputOne(res, ColorEnum.Blue.value)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExcelTransformDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
