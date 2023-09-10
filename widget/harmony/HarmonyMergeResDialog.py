# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyMergeResDialog.py
# 定义一个HarmonyMergeResDialog类实现Harmony json资源文件移动合并的功能
import os.path
import sys
from manager.AsyncFuncManager import AsyncFuncManager
from util.DictUtil import DictUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.CommonRadioButtons import CommonRadioButtons
from widget.custom.DragInputWidget import DragInputWidget

RES_TYPE_LIST = ['all', 'string', 'color', 'float', 'media']
EXCLUDE_DIR_PATTERNS = ['.*/\.hvigor/.*', '.*/\.git/.*', '.*/\.idea/.*', '.*/\.cxx/.*', '.*/build/.*', '.*/libs/.*',
                        '.*/node_modules/.*', '.*/oh_modules/.*', '.*/cpp/.*', '.*/ets/.*', '.*/ohosTest/.*',
                        '.*/\.preview/.*']
EXCHANGE_KEY = {'zh_CN': 'en_US', 'en_US': 'zh_CN'}
TAG = "HarmonyMergeResDialog"

KEY_SECTION = 'HarmonyMergeRes'
KEY_SRC_FILE_PATH = 'srcFilePath'
KEY_DST_FILE_PATH = 'dstFilePath'


def getLanguageStr(fp, endStr='/element'):
    startIndex = fp.index('resources')
    if startIndex >= 0:
        subStr = fp[startIndex + len('resources/'):]
        endIndex = subStr.index(endStr)
        if endIndex >= 0:
            return subStr[:endIndex]
    return None


class HarmonyMergeResDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyMergeResDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        HarmonyMergeResDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Init Harmony Merge Res Dialog")
        self.setObjectName("HarmonyMergeResDialog")
        self.resize(HarmonyMergeResDialog.WINDOW_WIDTH, HarmonyMergeResDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyMergeResDialog.WINDOW_WIDTH, HarmonyMergeResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 合并资源文件处理"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__srcFilePath = self.__operaIni.getValue(KEY_SRC_FILE_PATH, KEY_SECTION)
        self.__dstFilePath = self.__operaIni.getValue(KEY_DST_FILE_PATH, KEY_SECTION)
        self.__asyncFuncManager = AsyncFuncManager()

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        groupBox = self.__createGroupBox(self)

        vLayout.addWidget(groupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __createGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title='')
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)

        labelWidth = 150
        self.__srcFilePathWidget = DragInputWidget(label='源资源文件所在的目录',
                                                   text=self.__srcFilePath,
                                                   dirParam={KEY_CAPTION: '源资源文件所在的目录'},
                                                   labelMinSize=QSize(labelWidth, 0),
                                                   toolTip='选择源资源文件所在的目录')
        vbox.addWidget(self.__srcFilePathWidget)

        self.__dstFilePathWidget = DragInputWidget(label='目标资源文件所在的目录',
                                                   text=self.__dstFilePath,
                                                   dirParam={KEY_CAPTION: '目标资源文件所在的目录'},
                                                   labelMinSize=QSize(labelWidth, 0),
                                                   toolTip='选择目标资源文件所在的目录，resource目录所需要存放的路径')
        vbox.addWidget(self.__dstFilePathWidget)

        self.__resTypeRadioButtons = CommonRadioButtons(label="选择资源类型：", groupList=RES_TYPE_LIST)
        vbox.addWidget(self.__resTypeRadioButtons)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="合并资源", onClicked=self.__mergeElements))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def __mergeElements(self):
        srcFileDirPath = self.__srcFilePathWidget.getData()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件目录")
            return
        dstFileDirPath = self.__dstFilePathWidget.getData()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件目录")
            return
        while dstFileDirPath.endswith("/") or dstFileDirPath.endswith("\\"):
            dstFileDirPath = dstFileDirPath[:len(dstFileDirPath) - 1]
        LogUtil.d(TAG, "目标目录：", dstFileDirPath)
        self.__operaIni.addItem(KEY_SECTION, KEY_SRC_FILE_PATH, srcFileDirPath)
        self.__operaIni.addItem(KEY_SECTION, KEY_DST_FILE_PATH, dstFileDirPath)
        self.__operaIni.saveIni()

        self.__asyncFuncManager.asyncExec(target=self.__mergeRes, args=(srcFileDirPath, dstFileDirPath))
        pass

    def __mergeRes(self, srcFileDirPath, dstFileDirPath):
        resType = self.__resTypeRadioButtons.getData()
        if resType == RES_TYPE_LIST[0] or resType == RES_TYPE_LIST[1]:
            self.__mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'string')
        if resType == RES_TYPE_LIST[0] or resType == RES_TYPE_LIST[2]:
            self.__mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'color')
        if resType == RES_TYPE_LIST[0] or resType == RES_TYPE_LIST[3]:
            self.__mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'float')
        if resType == RES_TYPE_LIST[0] or resType == RES_TYPE_LIST[4]:
            self.__mergeMediaRes(srcFileDirPath, dstFileDirPath)
        self.__asyncFuncManager.hideLoading()
        pass

    def __mergeHarmonyRes(self, srcFileDirPath, dstFileDirPath, resType):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=[f'.*{resType}\.json'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d(TAG, 'mergeHarmonyRes find files: ', srcFiles)
        res = {}
        for fp in srcFiles:
            languageStr = getLanguageStr(fp)
            data = DictUtil.get(res, languageStr, [])
            jsonData = JsonUtil.load(fp)
            res[languageStr] = data + jsonData[resType]
        for (key, value) in res.items():
            temp = {}
            for data in value:
                temp[data['name']] = data
            value = [item for item in temp.values()]
            dstFp = os.path.join(dstFileDirPath, 'resources', DictUtil.get(EXCHANGE_KEY, key, key), 'element',
                                 f'{resType}.json')
            FileUtil.mkFilePath(dstFp)
            JsonUtil.dump(dstFp, {resType: value}, ensureAscii=False)
        pass

    def __mergeMediaRes(self, srcFileDirPath, dstFileDirPath):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=['.*/media/.*'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d(TAG, 'mergeMediaRes find files: ', srcFiles)
        for fp in srcFiles:
            languageStr = getLanguageStr(fp, '/media')
            _, fn = os.path.split(fp)
            dstFp = os.path.join(dstFileDirPath, 'resources', languageStr, 'media', fn)
            FileUtil.mkFilePath(dstFp)
            FileUtil.modifyFilePath(fp, dstFp)
            LogUtil.d(TAG, 'mergeMediaRes', dstFp)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyMergeResDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
