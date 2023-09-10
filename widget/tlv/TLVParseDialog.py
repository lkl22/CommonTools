# -*- coding: utf-8 -*-
# python 3.x
# Filename: TLVParseDialog.py
# 定义一个TLVParseDialog类实现TLV格式数据解析功能
import sys

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.ListUtil import ListUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.CommonAddOrEditDialog import CommonAddOrEditDialog
from widget.custom.CommonTableView import CommonTableView
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.DragInputWidget import DragInputWidget

TAG = "TLVParseDialog"

TAG_HEADERS = {KEY_NAME: {KEY_TITLE: "Tag名"}, KEY_DESC: {KEY_TITLE: "Tag描述"}}

KEY_SECTION = 'TLVParse'
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
        TLVParseDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        TLVParseDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Init TLV Parse Dialog")
        self.setObjectName("TLVParseDialog")
        self.resize(TLVParseDialog.WINDOW_WIDTH, TLVParseDialog.WINDOW_HEIGHT)
        # self.setFixedSize(TLVParseDialog.WINDOW_WIDTH, TLVParseDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="TLV数据格式解析"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__tags = self.__operaIni.getValue(KEY_TAGS, KEY_SECTION)
        self.__lengthMap = self.__operaIni.getValue(KEY_LENGTH_MAP, KEY_SECTION)
        self.__valueParseFuncMap = self.__operaIni.getValue(KEY_VALUE_PARSE_FUNC_MAP, KEY_SECTION)
        self.__asyncFuncManager = AsyncFuncManager()

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        labelWidth = 120
        self.__tagTableView = CommonTableView(addBtnTxt="添加Tag", headers=TAG_HEADERS,
                                                     items=self.__tags,
                                                     addOrEditItemFunc=self.__addOrEditTagFunc)

        vbox.addWidget(self.__tagTableView)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(self, text="对比", onClicked=self.diffRes))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        self.__textEdit = CommonTextEdit()
        vbox.addWidget(self.__textEdit, 1)

        # self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __addOrEditTagFunc(self, callback, default=None, items=None):
        dialog = CommonAddOrEditDialog(windowTitle='添加/编辑Tag',
                                       optionInfos=[{
                                           KEY_ITEM_KEY: KEY_NAME,
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
                                       isDebug=self.__isDebug)
        dialog.show()
        pass

    def diffRes(self):
        srcFileDirPath = self.__srcFilePathWidget.getData()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件")
            return
        dstFileDirPath = self.__dstFilePathWidget.getData()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件")
            return
        # self.__operaIni.addItem(KEY_SECTION, KEY_SRC_FILE_PATH, srcFileDirPath)
        # self.__operaIni.addItem(KEY_SECTION, KEY_DST_FILE_PATH, dstFileDirPath)
        self.__operaIni.saveIni()

        self.__textEdit.clear()
        self.__asyncFuncManager.asyncExec(target=self.execDiff, args=(srcFileDirPath, dstFileDirPath))
        pass

    def execDiff(self, srcFileDirPath, dstFileDirPath):
        LogUtil.i(TAG, 'execDiff', srcFileDirPath, dstFileDirPath)

        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TLVParseDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
