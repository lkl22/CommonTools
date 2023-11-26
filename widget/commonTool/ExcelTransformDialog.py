# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExcelTransformDialog.py
# 定义一个ExcelTransformDialog类实现Excel转换功能
import os.path
import sys
from manager.AsyncFuncManager import AsyncFuncManager
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.MD5Util import MD5Util
from util.OperaIni import OperaIni
from util.excel.ExcelOperator import *
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonCheckBoxs import CommonCheckBoxs
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.CommonTableView import CommonTableView
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
# 过滤规则
KEY_SRC_FILTER_RULES = 'srcFilterRules'

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
        labelMinSize = QSize(120, 0)

        box = WidgetUtil.createGroupBox(self, title="源Excel相关配置")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10))
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

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__primaryKeyComboBox = CommonComboBox(label='选择主键', dataChanged=self.__primaryKeyChanged)
        hbox.addWidget(self.__primaryKeyComboBox)

        self.__srcFilterRulesEdit = CommonLineEdit(label='过滤规则',
                                                   toolTip='输入Excel过滤规则。格式如下：{"title1": [value1, value2, value3], "title2": [value1, value2, value3]}')
        hbox.addWidget(self.__srcFilterRulesEdit, 1)
        vbox.addLayout(hbox)
        vLayout.addWidget(box)

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
        srcFp = DictUtil.get(self.__config, KEY_SRC_FP)
        srcSheetName = DictUtil.get(self.__config, KEY_SRC_SHEET_NAME)
        srcHeaderRow = DictUtil.get(self.__config, KEY_SRC_HEADER_ROW, 1)
        srcHeaders = DictUtil.get(self.__config, KEY_SRC_HEADERS, [])
        srcSelectHeader = DictUtil.get(self.__config, KEY_SRC_SELECT_HEADER, [])
        srcPrimaryKey = DictUtil.get(self.__config, KEY_PRIMARY, '')
        srcFilterRules = DictUtil.get(self.__config, KEY_SRC_FILTER_RULES, {})

        dstDp = DictUtil.get(self.__config, KEY_DST_DP)
        dstExcelName = DictUtil.get(self.__config, KEY_DST_EXCEL_NAME)
        dstSheetName = DictUtil.get(self.__config, KEY_DST_SHEET_NAME)
        dstColsInfo = DictUtil.get(self.__config, KEY_DST_COLS_INFO)

        self.__srcFpWidget.updateData(srcFp)
        self.__srcSheetNameWidget.updateData(srcSheetName)
        self.__srcHeaderRowWidget.updateData(srcHeaderRow)
        self.__srcSelectHeaderCheckBoxs.updateData(groupList=srcHeaders, defaultValue=srcSelectHeader)
        self.__primaryKeyComboBox.updateData(default=srcPrimaryKey, groupList=['', *srcHeaders])
        self.__srcFilterRulesEdit.updateData(JsonUtil.encode(srcFilterRules, ensureAscii=False, indent=0))

        self.__dstDpWidget.updateData(dstDp)
        self.__dstExcelNameWidget.updateData(dstExcelName)
        self.__dstSheetNameWidget.updateData(dstSheetName)
        self.__dstColsInfoTableView.updateData(dstColsInfo)
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
        primaryKey = DictUtil.get(self.__config, KEY_PRIMARY, '')
        self.__config[KEY_SRC_HEADERS] = res
        self.__srcSelectHeaderCheckBoxs.updateData(groupList=res, defaultValue=srcSelectHeader)
        self.__primaryKeyComboBox.updateData(default=primaryKey, groupList=['', *res])
        pass

    def __srcSelectHeaderChanged(self, data):
        self.__config[KEY_SRC_SELECT_HEADER] = data
        self.__saveConfigs()
        pass

    def __primaryKeyChanged(self, curData, deleteData):
        self.__config[KEY_PRIMARY] = curData
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
        self.__config = {
            KEY_SRC_FP: self.__srcFpWidget.getData(),
            KEY_SRC_SHEET_NAME: self.__srcSheetNameWidget.getData(),
            KEY_SRC_HEADER_ROW: self.__srcHeaderRowWidget.getData(),
            KEY_SRC_HEADERS: self.__srcSelectHeaderCheckBoxs.getGroupData(),
            KEY_SRC_SELECT_HEADER: self.__srcSelectHeaderCheckBoxs.getData(),
            KEY_PRIMARY: self.__primaryKeyComboBox.getData(),
            KEY_SRC_FILTER_RULES: JsonUtil.decode(self.__srcFilterRulesEdit.getData()),

            KEY_DST_DP: self.__dstDpWidget.getData(),
            KEY_DST_EXCEL_NAME: self.__dstExcelNameWidget.getData(),
            KEY_DST_SHEET_NAME: self.__dstSheetNameWidget.getData(),
            KEY_DST_COLS_INFO: self.__dstColsInfoTableView.getData(),
        }
        self.__operaIni.addItem(KEY_SECTION, MD5Util.md5(configDatas[KEY_DEFAULT]),
                                JsonUtil.encode(self.__config, ensureAscii=False))
        self.__operaIni.saveIni()
        pass

    def __addOrEditDstCol(self, callback, default=None, items=None):
        if not default:
            config = self.__configComboBox.getData()
            if not config:
                WidgetUtil.showErrorDialog(message="请添加配置")
                return
            if not DictUtil.get(self.__config, KEY_SRC_SELECT_HEADER):
                WidgetUtil.showErrorDialog(message="请选择需要提取数据的Title")
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
                                       isDebug=self.__isDebug)
        if self.__isDebug:
            dialog.show()
        pass

    def __checkParams(self):
        if not DictUtil.get(self.__config, KEY_SRC_SELECT_HEADER):
            WidgetUtil.showErrorDialog(message="请选择需要提取数据的Title")
            return False
        if not DictUtil.get(self.__config, KEY_PRIMARY):
            WidgetUtil.showErrorDialog(message="请选择源Excel主键")
            return False
        if not DictUtil.get(self.__config, KEY_SRC_FILTER_RULES):
            WidgetUtil.showErrorDialog(message="请输入源Excel数据过滤规则")
            return False

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
        srcFp, srcSheetName, srcHeaderRow = self.__checkSrcConfig()
        if not srcFp:
            return
        if not FileUtil.existsFile(srcFp):
            WidgetUtil.showErrorDialog(message="选择的Excel文件已经不存在了，请重新选择")
            return
        if not self.__checkParams():
            return
        dstFp = os.path.join(self.__config[KEY_DST_DP], self.__config[KEY_DST_EXCEL_NAME])
        _, ext = os.path.splitext(dstFp)
        if ext != '.xls' and ext != '.xlsx':
            WidgetUtil.showErrorDialog(message="请输入正确的文件名，后缀为xls或xlsx")
            return
        if FileUtil.existsFile(dstFp):
            WidgetUtil.showQuestionDialog(message=f"目标文件 <span style='color:red;'>{dstFp}</span> 已经存在，你确定要覆盖吗？",
                                          acceptFunc=lambda: self.__asyncFuncManager.asyncExec(
                                              target=self.__execTransform))
        else:
            self.__asyncFuncManager.asyncExec(target=self.__execTransform)
        pass

    def __execTransform(self):
        LogUtil.i(TAG, '__execTransform start: ', self.__config)
        srcFp = os.path.join(self.__config[KEY_SRC_FP])
        srcDatas = ExcelOperator.getExcelData(srcFp, self.__config[KEY_SRC_SHEET_NAME], {
            KEY_PRIMARY_KEY: self.__config[KEY_PRIMARY],
            KEY_TITLE_INDEX: self.__config[KEY_SRC_HEADER_ROW] - 1,
            KEY_COL_KEYS: self.__config[KEY_SRC_SELECT_HEADER],
            KEY_FILTER_RULES: self.__config[KEY_SRC_FILTER_RULES],
        })
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
