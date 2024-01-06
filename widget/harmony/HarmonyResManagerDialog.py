# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyResManagerDialog.py
# 定义一个HarmonyResManagerDialog类实现Harmony资源管理，查找字串对应的模块，交换字串等
import sys

from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.FileUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.ReadExcelWidget import ReadExcelWidget
from widget.custom.SwapTextWidget import SwapTextWidget, KEY_LEFT_TXT, KEY_RIGHT_TXT

TAG = "HarmonyResManagerDialog"
EXCLUDE_DIR_PATTERNS = ['.*/\.hvigor/.*', '.*/\.git/.*', '.*/\.idea/.*', '.*/\.cxx/.*', '.*/build/.*', '.*/libs/.*',
                        '.*/node_modules/.*', '.*/oh_modules/.*', '.*/cpp/.*', '.*/ets/.*', '.*/ohosTest/.*',
                        '.*/\.preview/.*']

KEY_SECTION = 'HarmonyResManager'
KEY_PROJECT_FILE_PATH = 'projectFilePath'
KEY_SWAP_DATA = 'swapData'
KEY_FIND_RES_INFO_CONFIG = 'findResInfoConfig'
KEY_SRC_EXCEL_CFG = 'srcExcelCfg'
KEY_LANGUAGE = 'language'


class HarmonyResManagerDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyResManagerDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        HarmonyResManagerDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Init Harmony Res Manager Dialog")
        self.setObjectName("HarmonyResManagerDialog")
        self.resize(HarmonyResManagerDialog.WINDOW_WIDTH, HarmonyResManagerDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyResManagerDialog.WINDOW_WIDTH, HarmonyResManagerDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony资源管理"))

        self.__strResInfos = {}
        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__projectFilePath = self.__operaIni.getValue(KEY_PROJECT_FILE_PATH, KEY_SECTION)
        self.__swapData = JsonUtil.decode(self.__operaIni.getValue(KEY_SWAP_DATA, KEY_SECTION), {})
        self.__findResInfoConfig = JsonUtil.decode(self.__operaIni.getValue(KEY_FIND_RES_INFO_CONFIG, KEY_SECTION))
        self.__asyncFuncManager = AsyncFuncManager()

        hLayout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)

        labelWidth = 150
        self.__projectFilePathWidget = DragInputWidget(label="工程路径",
                                                       text=self.__projectFilePath,
                                                       dirParam={KEY_CAPTION: '请选择Harmony工程代码路径'},
                                                       labelMinSize=QSize(labelWidth, 0),
                                                       toolTip='请选择Harmony工程代码路径',
                                                       required=True)
        vLayout.addWidget(self.__projectFilePathWidget)

        groupBox = self.__createSwapStrGroupBox(self)
        vLayout.addWidget(groupBox)

        groupBox = self.__createFindStrInfoGroupBox(self)
        vLayout.addWidget(groupBox)

        vLayout.addSpacerItem(WidgetUtil.createVSpacerItem())

        hLayout.addLayout(vLayout, 2)
        self.__textEdit = CommonTextEdit()
        hLayout.addWidget(self.__textEdit, 1)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __createSwapStrGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="交换字符资源")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.__swapTextWidget = SwapTextWidget(label='需要交换的资源目录', data=self.__swapData)
        vbox.addWidget(self.__swapTextWidget)
        hbox = WidgetUtil.createHBoxLayout()
        btn = WidgetUtil.createPushButton(box, text='交换', onClicked=self.__swapResEvent)
        hbox.addWidget(btn)
        hbox.addSpacerItem(WidgetUtil.createHSpacerItem())
        vbox.addLayout(hbox)
        return box

    def __createFindStrInfoGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="查找字串资源扩展信息")
        vbox = WidgetUtil.createVBoxLayout(box, spacing=10)

        self.__excelCfgWidget = ReadExcelWidget(label="待处理字串Excel文件信息",
                                                data=DictUtil.get(self.__findResInfoConfig, KEY_SRC_EXCEL_CFG),
                                                toolTip='请选择待处理字串Excel文件配置信息')
        vbox.addWidget(self.__excelCfgWidget)

        self.__languageLineEdit = CommonLineEdit(label='字符资源目录',
                                                 text=DictUtil.get(self.__findResInfoConfig, KEY_LANGUAGE, 'zh_CN'),
                                                 toolTip='字符资源所在的目录，选择一种作为基准，默认中文（zh_CN）',
                                                 required=True)
        vbox.addWidget(self.__languageLineEdit)
        hbox = WidgetUtil.createHBoxLayout()
        btn = WidgetUtil.createPushButton(box, text='获取信息', onClicked=self.__findStrResInfoEvent)
        hbox.addWidget(btn)
        hbox.addSpacerItem(WidgetUtil.createHSpacerItem())
        vbox.addLayout(hbox)
        return box

    def __checkProjectDir(self):
        projectFilePath = self.__projectFilePathWidget.getData()
        if not projectFilePath:
            WidgetUtil.showErrorDialog(message="请选择工程代码路径")
            return False
        self.__projectFilePath = projectFilePath
        self.__operaIni.addItem(KEY_SECTION, KEY_PROJECT_FILE_PATH, projectFilePath)
        self.__operaIni.saveIni()
        return True

    def __swapResEvent(self):
        if not self.__checkProjectDir():
            return
        swapData = self.__swapTextWidget.getData()
        leftTxt = DictUtil.get(swapData, KEY_LEFT_TXT)
        rightTxt = DictUtil.get(swapData, KEY_RIGHT_TXT)
        if not leftTxt or not rightTxt:
            WidgetUtil.showErrorDialog(message="请输入需要交换资源的目录")
            return
        self.__operaIni.addItem(KEY_SECTION, KEY_SWAP_DATA, JsonUtil.encode(swapData))
        self.__operaIni.saveIni()
        self.__textEdit.clear()
        self.__asyncFuncManager.asyncExec(target=self.__swapRes, args=(leftTxt, rightTxt))

    def __swapRes(self, leftDir, rightDir):
        LogUtil.i(TAG, f'[__swapRes] {leftDir} <--> {rightDir}')
        resourcesDirs = FileUtil.findDirPathList(self.__projectFilePath, findPatterns=['.*/resources'],
                                                 excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.i(TAG, f'[__swapRes] find dirs: {resourcesDirs}')
        for subDir in resourcesDirs:
            leftResDir = os.path.join(subDir, leftDir, 'element')
            rightResDir = os.path.join(subDir, rightDir, 'element')
            tmpResDir = os.path.join(subDir, 'tmp')
            FileUtil.modifyFilesPath(fnPatterns=['plural.json', 'string.json'], srcFp=leftResDir, dstFp=tmpResDir,
                                     isCopy=False)
            FileUtil.modifyFilesPath(fnPatterns=['plural.json', 'string.json'], srcFp=rightResDir, dstFp=leftResDir,
                                     isCopy=False)
            FileUtil.modifyFilesPath(fnPatterns=['plural.json', 'string.json'], srcFp=tmpResDir, dstFp=rightResDir,
                                     isCopy=False)
            FileUtil.removeDir(fp=tmpResDir)
        self.__asyncFuncManager.hideLoading()

    def __findStrResInfoEvent(self):
        if not self.__checkProjectDir():
            return
        excelCfg = self.__excelCfgWidget.getData()
        if not excelCfg:
            WidgetUtil.showErrorDialog(message="请设置待处理字串Excel文件配置信息")
            return False
        findResInfoConfig = {
            KEY_SRC_EXCEL_CFG: excelCfg,
            KEY_LANGUAGE: self.__languageLineEdit.getData(),
        }
        self.__operaIni.addItem(KEY_SECTION, KEY_FIND_RES_INFO_CONFIG, JsonUtil.encode(findResInfoConfig))
        self.__operaIni.saveIni()
        self.__asyncFuncManager.asyncExec(target=self.__findStrResInfo, args=(findResInfoConfig,))
        pass

    def __findStrResInfo(self, findResInfoConfig):
        LogUtil.i(TAG, f'__findStrResInfo {findResInfoConfig}')
        srcExcelData = self.__excelCfgWidget.getExcelData()
        language = self.__languageLineEdit.getData()
        LogUtil.i(TAG, f'__findStrResInfo language: {language} srcExcelData: {srcExcelData}')
        self.__getStrResInfo(language)
        self.__asyncFuncManager.hideLoading()
        pass

    def __getStrResInfo(self, language: str):
        LogUtil.i(TAG, f'__getStrResInfo {language}')
        resDirs = FileUtil.findDirPathList(self.__projectFilePath, findPatterns=[f'.*/resources/{language}'],
                                          excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.i(TAG, f'__getStrResInfo resDirs: {resDirs}')
        for resDir in resDirs:
            resFps = FileUtil.findFilePathList(resDir, findPatterns=['.*string\.json', '.*plural\.json'])
            LogUtil.i(TAG, f'__getStrResInfo resFps: {resFps}')
            for resFp in resFps:
                self.__getStrResInfoFromFp(resFp)
        pass

    def __getStrResInfoFromFp(self, fp: str):
        strRes = JsonUtil.load(fp)
        resDatas = DictUtil.get(strRes, 'string', DictUtil.get(strRes, 'plural'))
        LogUtil.i(TAG, f'__getStrResInfoFromFp resDatas: {resDatas}')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyResManagerDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
