# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyMergeResDialog.py
# 定义一个HarmonyMergeResDialog类实现android xml资源文件移动合并的功能
import os.path
import sys
import threading

from PyQt5.QtCore import pyqtSignal
from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.LoadingDialog import LoadingDialog

RES_TYPE_LIST = ['all', 'string', 'color', 'float', 'media']
EXCLUDE_DIR_PATTERNS = ['.*/\.hvigor/.*', '.*/\.idea/.*', '.*/\.cxx/.*', '.*/build/.*', '.*/libs/.*',
                        '.*/node_modules/.*', '.*/cpp/.*', '.*/ets/.*', '.*/ohosTest/.*']
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
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyMergeResDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        HarmonyMergeResDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.35)
        LogUtil.d(TAG, "Init Harmony Merge Res Dialog")
        self.setObjectName("HarmonyMergeResDialog")
        self.resize(HarmonyMergeResDialog.WINDOW_WIDTH, HarmonyMergeResDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyMergeResDialog.WINDOW_WIDTH, HarmonyMergeResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 合并资源文件处理"))

        self.resType = RES_TYPE_LIST[0]
        self.isDebug = isDebug
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.srcFilePath = self.operaIni.getValue(KEY_SRC_FILE_PATH, KEY_SECTION)
        self.dstFilePath = self.operaIni.getValue(KEY_DST_FILE_PATH, KEY_SECTION)
        self.loadingDialog = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        androidResGroupBox = self.createXmlResGroupBox(self)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        self.hideLoadingSignal.connect(self.hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createXmlResGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="xml resource")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.srcFilePath if self.srcFilePath else '',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="目标文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.dstFilePath if self.dstFilePath else '',
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="选择资源类型：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(30, 0, 30, 0), spacing=10)
        self.resTypeBg = WidgetUtil.createButtonGroup(onToggled=self.resTypeToggled)
        for i in range(len(RES_TYPE_LIST)):
            if i == 12:
                hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
                hbox = WidgetUtil.createHBoxLayout(margins=QMargins(30, 0, 30, 0), spacing=10)
            radioButton = WidgetUtil.createRadioButton(box, text=RES_TYPE_LIST[i] + "  ", isChecked=i == 0)
            self.resTypeBg.addButton(radioButton, i)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="合并资源", onClicked=self.mergeElements))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def getSrcFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.srcFilePathLineEdit.setText(fp)
        pass

    def getDstFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.dstFilePathLineEdit.setText(fp)
        pass

    def resTypeToggled(self, radioButton):
        self.resType = RES_TYPE_LIST[self.resTypeBg.checkedId()]
        LogUtil.i(TAG, "选择的资源类型：", self.resType)
        pass

    def mergeElements(self):
        srcFileDirPath = self.srcFilePathLineEdit.text().strip()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件目录")
            return
        dstFileDirPath = self.dstFilePathLineEdit.text().strip()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件目录")
            return
        while dstFileDirPath.endswith("/") or dstFileDirPath.endswith("\\"):
            dstFileDirPath = dstFileDirPath[:len(dstFileDirPath) - 1]
        LogUtil.d(TAG, "目标目录：", dstFileDirPath)
        self.operaIni.addItem(KEY_SECTION, KEY_SRC_FILE_PATH, srcFileDirPath)
        self.operaIni.addItem(KEY_SECTION, KEY_DST_FILE_PATH, dstFileDirPath)
        self.operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.mergeRes, args=(srcFileDirPath, dstFileDirPath)).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def mergeRes(self, srcFileDirPath, dstFileDirPath):
        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[1]:
            self.mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'string')
        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[2]:
            self.mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'color')
        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[3]:
            self.mergeHarmonyRes(srcFileDirPath, dstFileDirPath, 'float')
        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[4]:
            self.mergeMediaRes(srcFileDirPath, dstFileDirPath)
        self.hideLoadingSignal.emit()
        pass

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass

    def mergeHarmonyRes(self, srcFileDirPath, dstFileDirPath, resType):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=[f'.*{resType}\.json'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d('mergeHarmonyRes find files: ', srcFiles)
        res = {}
        for fp in srcFiles:
            languageStr = getLanguageStr(fp)
            data = DictUtil.get(res, languageStr, [])
            jsonData = JsonUtil.load(fp)
            res[languageStr] = data + jsonData[resType]
        for (key, value) in res.items():
            dstFp = os.path.join(dstFileDirPath, 'resources', DictUtil.get(EXCHANGE_KEY, key, key), 'element', f'{resType}.json')
            FileUtil.mkFilePath(dstFp)
            JsonUtil.dump(dstFp, {resType: res[key]}, ensureAscii=False)
        pass

    def mergeMediaRes(self, srcFileDirPath, dstFileDirPath):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=['.*/media/.*'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d('mergeMediaRes find files: ', srcFiles)
        for fp in srcFiles:
            languageStr = getLanguageStr(fp, '/media')
            _, fn = os.path.split(fp)
            dstFp = os.path.join(dstFileDirPath, 'resources', languageStr, 'media', fn)
            FileUtil.mkFilePath(dstFp)
            FileUtil.modifyFilePath(fp, dstFp)
            LogUtil.d('mergeMediaRes', dstFp)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyMergeResDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
