# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelTransformDialog.py
# 定义一个ExcelTransformDialog类实现Excel转换功能
import os.path
import sys

from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.FileUtil import *
from util.JsonUtil import JsonUtil
from util.MD5Util import MD5Util
from util.OperaIni import OperaIni
from util.excel.ExcelOperator import *
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTableView import CommonTableView
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.ReadExcelWidget import ReadExcelWidget

TAG = "ExcelTransformDialog"

KEY_SECTION = 'ExcelTransform'
KEY_CONFIGS = 'configs'
KEY_SRC_EXCEL_CFG = 'srcExcelCfg'

# 目标Excel文件存储路径
KEY_DST_DP = 'dstDp'
KEY_DST_EXCEL_NAME = 'dstExcelName'
KEY_DST_SHEET_NAME = 'dstSheetName'
KEY_DST_COLS_INFO = 'dstColsInfo'

KEY_COL_TITLE = 'colTitle'
KEY_MAP_TITLE = 'mapTitle'
DST_COL_HEADERS = {KEY_COL_TITLE: {KEY_TITLE: "列Title"}, KEY_MAP_TITLE: {KEY_TITLE: "源Excel中的Title"},
                   KEY_DEFAULT: {KEY_TITLE: "默认值"}}


class ExcelTransformDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        ExcelTransformDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        ExcelTransformDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
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

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.__configComboBox = CommonComboBox(label='选择配置', default=self.__defaultConfigName,
                                               groupList=DictUtil.get(self.__configs, KEY_LIST, []),
                                               isEditable=True, dataChanged=self.__configChanged)
        vLayout.addWidget(self.__configComboBox)

        self.__srcExcelCfgWidget = ReadExcelWidget(label='源Excel相关配置',
                                                   data=DictUtil.get(self.__config, KEY_SRC_EXCEL_CFG))
        vLayout.addWidget(self.__srcExcelCfgWidget)

        labelMinSize = QSize(120, 0)
        box = WidgetUtil.createGroupBox(self, title="目标Excel相关配置")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10))
        self.__dstDpWidget = DragInputWidget(label='请选择目标Excel文件存放路径',
                                             dirParam={KEY_CAPTION: '请选择目标Excel文件存放路径'},
                                             labelMinSize=labelMinSize)
        vbox.addWidget(self.__dstDpWidget)

        splitter = WidgetUtil.createSplitter(self)
        self.__dstExcelNameWidget = CommonLineEdit(label='Excel文件名')
        splitter.addWidget(self.__dstExcelNameWidget)
        self.__dstSheetNameWidget = CommonLineEdit(label='表名')
        splitter.addWidget(self.__dstSheetNameWidget)
        vbox.addWidget(splitter)

        self.__dstColsInfoTableView = CommonTableView(addBtnTxt="添加表列信息", headers=DST_COL_HEADERS, items=[],
                                                      addOrEditItemFunc=self.__addOrEditDstCol,
                                                      toolTip='输出Excel中列信息，设置列Title，默认值，映射的源Excel内容')

        vbox.addWidget(self.__dstColsInfoTableView)
        vLayout.addWidget(box)

        vLayout.addItem(WidgetUtil.createVSpacerItem())
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addItem(WidgetUtil.createHSpacerItem())
        hbox.addWidget(WidgetUtil.createPushButton(self, text='转换', onClicked=self.__transformExcel))
        hbox.addItem(WidgetUtil.createHSpacerItem())
        vLayout.addLayout(hbox)
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
        dstDp = DictUtil.get(self.__config, KEY_DST_DP)
        dstExcelName = DictUtil.get(self.__config, KEY_DST_EXCEL_NAME)
        dstSheetName = DictUtil.get(self.__config, KEY_DST_SHEET_NAME)
        dstColsInfo = DictUtil.get(self.__config, KEY_DST_COLS_INFO)

        self.__srcExcelCfgWidget.updateData(DictUtil.get(self.__config, KEY_SRC_EXCEL_CFG))

        self.__dstDpWidget.updateData(dstDp)
        self.__dstExcelNameWidget.updateData(dstExcelName)
        self.__dstSheetNameWidget.updateData(dstSheetName)
        self.__dstColsInfoTableView.updateData(dstColsInfo)
        pass

    def __saveConfigs(self):
        configDatas = {KEY_DEFAULT: self.__configComboBox.getData(), KEY_LIST: self.__configComboBox.getGroupList()}
        self.__operaIni.addItem(KEY_SECTION, KEY_CONFIGS, JsonUtil.encode(configDatas, ensureAscii=False))
        self.__config = {
            KEY_SRC_EXCEL_CFG: self.__srcExcelCfgWidget.getData(),

            KEY_DST_DP: self.__dstDpWidget.getData(),
            KEY_DST_EXCEL_NAME: self.__dstExcelNameWidget.getData(),
            KEY_DST_SHEET_NAME: self.__dstSheetNameWidget.getData(),
            KEY_DST_COLS_INFO: self.__dstColsInfoTableView.getData(),
        }
        self.__operaIni.addItem(KEY_SECTION, MD5Util.md5(configDatas[KEY_DEFAULT]),
                                JsonUtil.encode(self.__config, ensureAscii=False))
        self.__operaIni.saveIni()
        pass

    def __addOrEditDstCol(self, callback, default=None, items=None, isAdd=False):
        if not default:
            config = self.__configComboBox.getData()
            if not config:
                WidgetUtil.showErrorDialog(message="请添加配置")
                return
            if not self.__srcExcelCfgWidget.getData():
                WidgetUtil.showErrorDialog(message="请设置源Excel配置")
                return False
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑列配置信息',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_COL_TITLE,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '列名：',
                                           KEY_TOOL_TIP: '请输入列名',
                                           KEY_IS_UNIQUE: True
                                       }, {
                                           KEY_ITEM_KEY: KEY_MAP_TITLE,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '对应的源Title',
                                           KEY_IS_OPTIONAL: True,
                                           KEY_TOOL_TIP: '与源Excel对应的Title，会将源列数据映射到该列'
                                       }, {
                                           KEY_ITEM_KEY: KEY_DEFAULT,
                                           KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                           KEY_ITEM_LABEL: '列数据默认值',
                                           KEY_IS_OPTIONAL: True,
                                           KEY_TOOL_TIP: '列数据默认值'
                                       }],
                                       callback=callback,
                                       default=default,
                                       items=items,
                                       isAdd=isAdd,
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __checkParams(self):
        if not DictUtil.get(self.__config, KEY_DST_DP):
            WidgetUtil.showErrorDialog(message="请选择目标Excel文件存放路径")
            return False
        if not DictUtil.get(self.__config, KEY_DST_EXCEL_NAME):
            WidgetUtil.showErrorDialog(message="请输入Excel文件名")
            return False
        if not DictUtil.get(self.__config, KEY_DST_SHEET_NAME):
            WidgetUtil.showErrorDialog(message="请输入表名")
            return False
        if not DictUtil.get(self.__config, KEY_DST_COLS_INFO):
            WidgetUtil.showErrorDialog(message="请输入目标表格列配置信息")
            return False
        return True

    def __transformExcel(self):
        config = self.__configComboBox.getData()
        if not config:
            WidgetUtil.showErrorDialog(message="请添加配置")
            return
        srcCfg = self.__srcExcelCfgWidget.getData()
        if not srcCfg:
            return
        if not self.__checkParams():
            return
        dstFp = os.path.join(self.__config[KEY_DST_DP], self.__config[KEY_DST_EXCEL_NAME])
        _, ext = os.path.splitext(dstFp)
        if ext != '.xls' and ext != '.xlsx':
            WidgetUtil.showErrorDialog(message="请输入正确的文件名，后缀为xls或xlsx")
            return
        self.__saveConfigs()
        if FileUtil.existsFile(dstFp):
            WidgetUtil.showQuestionDialog(
                message=f"目标文件 <span style='color:red;'>{dstFp}</span> 已经存在，你确定要覆盖吗？",
                acceptFunc=lambda: self.__asyncFuncManager.asyncExec(
                    target=self.__execTransform))
        else:
            self.__asyncFuncManager.asyncExec(target=self.__execTransform)
        pass

    def __execTransform(self):
        LogUtil.i(TAG, '__execTransform start: ', self.__config)
        srcDatas = self.__srcExcelCfgWidget.getExcelData()
        LogUtil.i(TAG, '__execTransform src data', srcDatas)

        dstFp = os.path.join(self.__config[KEY_DST_DP], self.__config[KEY_DST_EXCEL_NAME])
        dstColsInfo = self.__config[KEY_DST_COLS_INFO]
        dstTitles = [item[KEY_COL_TITLE] for item in dstColsInfo]
        dstDatas = []
        for item in srcDatas.values():
            dstRow = {}
            for colInfo in dstColsInfo:
                value = DictUtil.get(colInfo, KEY_DEFAULT, '')
                srcMap = DictUtil.get(colInfo, KEY_MAP_TITLE)
                if srcMap:
                    value = DictUtil.get(item, srcMap, value)
                dstRow[colInfo[KEY_COL_TITLE]] = {
                    KEY_VALUE: value
                }
            dstDatas.append(dstRow)
        LogUtil.i(TAG, '__execTransform dst', dstFp, dstTitles, dstDatas)
        ExcelOperator.saveToExcel(dstFp, self.__config[KEY_DST_SHEET_NAME], dstTitles, dstDatas)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExcelTransformDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
