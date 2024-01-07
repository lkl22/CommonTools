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
from util.ListUtil import ListUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.SwapTextWidget import SwapTextWidget, KEY_LEFT_TXT, KEY_RIGHT_TXT
from widget.custom.UpdateExcelWidget import UpdateExcelWidget

TAG = "HarmonyResManagerDialog"
EXCLUDE_DIR_PATTERNS = ['.*/\.hvigor/.*', '.*/\.git/.*', '.*/\.idea/.*', '.*/\.cxx/.*', '.*/build/.*', '.*/libs/.*',
                        '.*/node_modules/.*', '.*/oh_modules/.*', '.*/cpp/.*', '.*/ets/.*', '.*/ohosTest/.*',
                        '.*/\.preview/.*']

KEY_SECTION = 'HarmonyResManager'
KEY_PROJECT_FILE_PATH = 'projectFilePath'
KEY_SWAP_DATA = 'swapData'
KEY_FIND_RES_INFO_CONFIG = 'findResInfoConfig'
KEY_UPDATE_EXCEL_CFG = 'updateExcelCfg'
KEY_LANGUAGE = 'language'
KEY_EXCLUDE_AUTHOR = 'excludeAuthor'


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

        self.__excelCfgWidget = UpdateExcelWidget(label="待处理字串Excel文件信息",
                                                  data=DictUtil.get(self.__findResInfoConfig, KEY_UPDATE_EXCEL_CFG),
                                                  toolTip='请设置待处理字串Excel文件配置信息')
        vbox.addWidget(self.__excelCfgWidget)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__languageLineEdit = CommonLineEdit(label='字符资源目录',
                                                 text=DictUtil.get(self.__findResInfoConfig, KEY_LANGUAGE, 'zh_CN'),
                                                 toolTip='字符资源所在的目录，选择一种作为基准，默认中文（zh_CN）',
                                                 required=True)
        hbox.addWidget(self.__languageLineEdit)

        self.__excludeAuthorLineEdit = CommonLineEdit(label='需要排除的Author',
                                                      text=DictUtil.get(self.__findResInfoConfig, KEY_EXCLUDE_AUTHOR),
                                                      toolTip='需要排除的Author，多个Author之间使用;间隔',
                                                      required=True)
        hbox.addWidget(self.__excludeAuthorLineEdit)
        vbox.addLayout(hbox)
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
            KEY_UPDATE_EXCEL_CFG: excelCfg,
            KEY_LANGUAGE: self.__languageLineEdit.getData(),
            KEY_EXCLUDE_AUTHOR: self.__excludeAuthorLineEdit.getData(),
        }
        self.__operaIni.addItem(KEY_SECTION, KEY_FIND_RES_INFO_CONFIG, JsonUtil.encode(findResInfoConfig))
        self.__operaIni.saveIni()
        self.__asyncFuncManager.asyncExec(target=self.__findStrResInfo, args=(findResInfoConfig,))
        pass

    def __findStrResInfo(self, findResInfoConfig):
        LogUtil.i(TAG, f'__findStrResInfo {findResInfoConfig}')
        language = self.__languageLineEdit.getData()
        excludeAuthor = self.__excludeAuthorLineEdit.getData()
        LogUtil.i(TAG,
                  f'__findStrResInfo language: {language} excludeAuthor {excludeAuthor}')
        self.__strResInfos.clear()
        self.__getStrResInfo(language, excludeAuthor)
        LogUtil.i(TAG, f'__findStrResInfo strResInfos: {self.__strResInfos}')
        self.__excelCfgWidget.updateExcel(self.__strResInfos)
        self.__asyncFuncManager.hideLoading()
        pass

    def __getStrResInfo(self, language: str, excludeAuthor: str):
        LogUtil.i(TAG, f'__getStrResInfo {language}')
        resDirs = FileUtil.findDirPathList(self.__projectFilePath, findPatterns=[f'.*/resources/{language}'],
                                           excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.i(TAG, f'__getStrResInfo resDirs: {resDirs}')
        for resDir in resDirs:
            resFps = FileUtil.findFilePathList(resDir, findPatterns=['.*string\.json', '.*plural\.json'])
            LogUtil.i(TAG, f'__getStrResInfo resFps: {resFps}')
            for resFp in resFps:
                self.__getStrResInfoFromFp(resFp, excludeAuthor)
        pass

    def __getStrResInfoFromFp(self, fp: str, excludeAuthor: str):
        strRes = JsonUtil.load(fp)
        resDatas = DictUtil.get(strRes, 'string', [])
        resDatas += DictUtil.get(strRes, 'plural', [])
        match = ReUtil.match(f'{self.__projectFilePath}/*(.*)/resources/.*', fp)
        module = match.group(1).replace('/src/main', '')
        LogUtil.i(TAG, f'__getStrResInfoFromFp module: {module}')
        for item in resDatas:
            key = item['name']
            value = item['value']
            data = self.__strResInfos.get(key)
            resInfo = {KEY_MODULE_NAME: module, KEY_VALUE: value, KEY_FILE_PATH: fp}
            if not data:
                data = [resInfo]
                self.__strResInfos[key] = data
            else:
                data.append(resInfo)
        self.__getGitInfoByFp(fp, excludeAuthor)
        pass

    def __getGitInfoByFp(self, fp: str, excludeAuthor: str):
        out, err = ShellUtil.exec(f'cd {self.__projectFilePath} && git annotate {fp} | findstr "name"')
        if err:
            LogUtil.e(TAG, f'__getGitInfoByFp parse author failed: {err}')
            return
        excludeAuthors = [item for item in excludeAuthor.split(';') if item]
        lines = out.split('\n')
        lines = [line for line in lines if line]
        for line in lines:
            gitInfos = ReUtil.match('.*\(\s*(.*)\s+(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}).*"name":\s*"(.*)".*', line)
            if gitInfos:
                data = ListUtil.find(self.__strResInfos[gitInfos.group(3)], KEY_FILE_PATH, fp)
                data[KEY_AUTHOR] = gitInfos.group(1)
                data[KEY_DATETIME] = gitInfos.group(2)
                if excludeAuthors and data[KEY_AUTHOR] in excludeAuthors:
                    author, datetime = self.__getCodeAuthor(fp, gitInfos.group(3), excludeAuthors)
                    if author:
                        data[KEY_AUTHOR] = author
                        data[KEY_DATETIME] = datetime
        pass

    def __getCodeAuthor(self, fp, resName, excludeAuthors, num=1):
        out, err = ShellUtil.exec(
            f'cd {self.__projectFilePath} && git annotate {fp} -s HEAD~{num} | findstr "{resName}"')
        if not out:
            return None, None
        lines = [line for line in out.split('\n') if line]
        if not lines:
            return None, None
        gitInfos = ReUtil.match('.*\(\s*(.*)\s+(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}:\d{2}).*"name":\s*"(.*)".*', lines[0])
        if not gitInfos:
            return None, None
        if gitInfos.group(1) in excludeAuthors:
            # 还是excludeAuthor继续往前查找
            return self.__getCodeAuthor(fp, resName, excludeAuthors, num + 1)
        return gitInfos.group(1), gitInfos.group(2)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyResManagerDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
