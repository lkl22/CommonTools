# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyMergeResDialog.py
# 定义一个HarmonyMergeResDialog类实现android xml资源文件移动合并的功能
import os.path
import sys

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *

RES_TYPE_LIST = ['all', 'string', 'color', 'media']
EXCLUDE_DIR_PATTERNS = ['.*/\.hvigor/.*', '.*/\.idea/.*', '.*/\.cxx/.*', '.*/build/.*', '.*/libs/.*',
                        '.*/node_modules/.*', '.*/cpp/.*', '.*/ets/.*', '.*/ohosTest/.*']
TAG = "HarmonyMergeResDialog"


def getLanguageStr(fp):
    startIndex = fp.index('resources')
    if startIndex >= 0:
        subStr = fp[startIndex + len('resources/'):]
        endIndex = subStr.index('/element')
        if endIndex >= 0:
            return subStr[:endIndex]
    return None


class HarmonyMergeResDialog(QtWidgets.QDialog):
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

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        androidResGroupBox = self.createXmlResGroupBox(self)

        vLayout.addWidget(androidResGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createXmlResGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="xml resource")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        vLayout = WidgetUtil.createVBoxLayout()
        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="源文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='/Users/likunlun/Android/Projects/DeveloperDocuments/HarmonyStudy',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="目标文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='/Users/likunlun/Android/Projects/DeveloperDocuments/',
                                                             sizePolicy=sizePolicy)
        vLayout.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout(spacing=20)
        hbox.addLayout(vLayout)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="选择资源类型：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(30, 0, 30, 0), spacing=10)
        vbox.addLayout(hbox)
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

        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[1]:
            self.mergeStringRes(srcFileDirPath, dstFileDirPath)
        if self.resType == RES_TYPE_LIST[0] or self.resType == RES_TYPE_LIST[2]:
            self.mergeColorRes(srcFileDirPath, dstFileDirPath)
        pass

    def mergeStringRes(self, srcFileDirPath, dstFileDirPath):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=['.*string\.json'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d('mergeStringRes find files: ', srcFiles)
        res = {}
        for fp in srcFiles:
            languageStr = getLanguageStr(fp)
            data = DictUtil.get(res, languageStr, [])
            jsonData = JsonUtil.load(fp)
            res[languageStr] = data + jsonData['string']
        for (key, value) in res.items():
            dstFp = os.path.join(dstFileDirPath, 'resources', key, 'element', 'string.json')
            FileUtil.mkFilePath(dstFp)
            JsonUtil.dump(dstFp, {'string': res[key]}, ensureAscii=False)
        pass

    def mergeColorRes(self, srcFileDirPath, dstFileDirPath):
        # 查找需要修改的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFileDirPath, findPatterns=['.*color\.json'],
                                             excludeDirPatterns=EXCLUDE_DIR_PATTERNS)
        LogUtil.d('mergeColorRes find files: ', srcFiles)
        res = {}
        for fp in srcFiles:
            languageStr = getLanguageStr(fp)
            data = DictUtil.get(res, languageStr, [])
            jsonData = JsonUtil.load(fp)
            res[languageStr] = data + jsonData['color']
        for (key, value) in res.items():
            dstFp = os.path.join(dstFileDirPath, 'resources', key, 'element', 'color.json')
            FileUtil.mkFilePath(dstFp)
            JsonUtil.dump(dstFp, {'color': res[key]}, ensureAscii=False)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyMergeResDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
