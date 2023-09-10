# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyStrResDiffDialog.py
# 定义一个HarmonyStrResDiffDialog类实现Harmony string资源差异化对比，找出缺失的多语言翻译
import sys
from manager.AsyncFuncManager import AsyncFuncManager
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.DragInputWidget import DragInputWidget

TAG = "HarmonyStrResDiffDialog"

KEY_SECTION = 'HarmonyStrResDiff'
KEY_SRC_FILE_PATH = 'srcFilePath'
KEY_DST_FILE_PATH = 'dstFilePath'


class HarmonyStrResDiffDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyStrResDiffDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        HarmonyStrResDiffDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Init Harmony String Res Diff Dialog")
        self.setObjectName("HarmonyStrResDiffDialog")
        self.resize(HarmonyStrResDiffDialog.WINDOW_WIDTH, HarmonyStrResDiffDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyStrResDiffDialog.WINDOW_WIDTH, HarmonyStrResDiffDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 查找缺失的多语言翻译"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__srcFilePath = self.__operaIni.getValue(KEY_SRC_FILE_PATH, KEY_SECTION)
        self.__dstFilePath = self.__operaIni.getValue(KEY_DST_FILE_PATH, KEY_SECTION)
        self.__asyncFuncManager = AsyncFuncManager()

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        groupBox = self.createGroupBox(self)

        vLayout.addWidget(groupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="查找缺失的多语言翻译")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        labelWidth = 120
        self.srcFilePathWidget = DragInputWidget(label="源文件路径",
                                                 text=self.__srcFilePath,
                                                 fileParam={KEY_CAPTION: '请选择Harmony字符串资源文件路径'},
                                                 labelMinSize=QSize(labelWidth, 0),
                                                 toolTip='请选择Harmony字符串资源文件路径')
        vbox.addWidget(self.srcFilePathWidget)

        self.dstFilePathWidget = DragInputWidget(label="目标文件路径",
                                                 text=self.__dstFilePath,
                                                 fileParam={KEY_CAPTION: '请选择Harmony字符串资源文件路径'},
                                                 labelMinSize=QSize(labelWidth, 0),
                                                 toolTip='请选择Harmony字符串资源文件路径')
        vbox.addWidget(self.dstFilePathWidget)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="对比", onClicked=self.diffRes))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def diffRes(self):
        srcFileDirPath = self.srcFilePathWidget.getData()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择源文件")
            return
        dstFileDirPath = self.dstFilePathWidget.getData()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件")
            return
        self.__operaIni.addItem(KEY_SECTION, KEY_SRC_FILE_PATH, srcFileDirPath)
        self.__operaIni.addItem(KEY_SECTION, KEY_DST_FILE_PATH, dstFileDirPath)
        self.__operaIni.saveIni()

        self.__asyncFuncManager.asyncExec(target=self.execDiff, args=(srcFileDirPath, dstFileDirPath))
        pass

    def execDiff(self, srcFileDirPath, dstFileDirPath):
        LogUtil.i(TAG, 'execDiff', srcFileDirPath, dstFileDirPath)
        try:
            srcStrings = JsonUtil.load(srcFileDirPath)['string']
            srcNames = set([item['name'] for item in srcStrings])
            dstStrings = JsonUtil.load(dstFileDirPath)['string']
            dstNames = set([item['name'] for item in dstStrings])
            diff = srcNames - dstNames
            LogUtil.d(TAG, len(diff), diff)
        except Exception as err:
            LogUtil.e(TAG, 'execDiff 错误信息：', err)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyStrResDiffDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
