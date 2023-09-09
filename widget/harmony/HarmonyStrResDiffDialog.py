# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyStrResDiffDialog.py
# 定义一个HarmonyStrResDiffDialog类实现Harmony string资源差异化对比，找出缺失的多语言翻译
import sys
import threading

from PyQt5.QtCore import pyqtSignal
from constant.WidgetConst import *
from util.FileUtil import *
from util.DialogUtil import *
from util.JsonUtil import JsonUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.LoadingDialog import LoadingDialog

TAG = "HarmonyStrResDiffDialog"

KEY_SECTION = 'HarmonyStrResDiff'
KEY_SRC_FILE_PATH = 'srcFilePath'
KEY_DST_FILE_PATH = 'dstFilePath'


class HarmonyStrResDiffDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyStrResDiffDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        HarmonyStrResDiffDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Harmony String Res Diff Dialog")
        self.setObjectName("HarmonyStrResDiffDialog")
        self.resize(HarmonyStrResDiffDialog.WINDOW_WIDTH, HarmonyStrResDiffDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyStrResDiffDialog.WINDOW_WIDTH, HarmonyStrResDiffDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 查找缺失的多语言翻译"))

        self.isDebug = isDebug
        self.operaIni = OperaIni()
        self.srcFilePath = self.operaIni.getValue(KEY_SRC_FILE_PATH, KEY_SECTION)
        self.dstFilePath = self.operaIni.getValue(KEY_DST_FILE_PATH, KEY_SECTION)
        self.loadingDialog = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        groupBox = self.createGroupBox(self)

        vLayout.addWidget(groupBox)

        self.setWindowModality(Qt.ApplicationModal)
        self.hideLoadingSignal.connect(self.hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="查找缺失的多语言翻译")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        labelWidth = 120
        self.srcFilePathWidget = DragInputWidget(label="源文件路径",
                                                 text=self.srcFilePath,
                                                 fileParam={KEY_CAPTION: '请选择Harmony字符串资源文件路径'},
                                                 labelMinSize=QSize(labelWidth, 0),
                                                 toolTip='请选择Harmony字符串资源文件路径')
        vbox.addWidget(self.srcFilePathWidget)

        self.dstFilePathWidget = DragInputWidget(label="目标文件路径",
                                                 text=self.dstFilePath,
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
        self.operaIni.addItem(KEY_SECTION, KEY_SRC_FILE_PATH, srcFileDirPath)
        self.operaIni.addItem(KEY_SECTION, KEY_DST_FILE_PATH, dstFileDirPath)
        self.operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execDiff, args=(srcFileDirPath, dstFileDirPath)).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
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
        self.hideLoadingSignal.emit()
        pass

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyStrResDiffDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
