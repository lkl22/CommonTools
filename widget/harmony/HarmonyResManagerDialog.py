# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyResManagerDialog.py
# 定义一个HarmonyResManagerDialog类实现Harmony资源管理，查找字串对应的模块，交换字串等
import sys

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.FileUtil import *
from util.JsonUtil import JsonUtil
from util.ListUtil import ListUtil
from util.LogUtil import *
from util.OperaIni import OperaIni
from widget.custom.CommonTextEdit import CommonTextEdit
from widget.custom.DragInputWidget import DragInputWidget

TAG = "HarmonyResManagerDialog"

KEY_SECTION = 'HarmonyResManager'
KEY_PROJECT_FILE_PATH = 'projectFilePath'
KEY_EXCEL_FILE_PATH = 'excelFilePath'


class HarmonyResManagerDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        HarmonyResManagerDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        HarmonyResManagerDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Init Harmony Res Manager Dialog")
        self.setObjectName("HarmonyResManagerDialog")
        self.resize(HarmonyResManagerDialog.WINDOW_WIDTH, HarmonyResManagerDialog.WINDOW_HEIGHT)
        # self.setFixedSize(HarmonyResManagerDialog.WINDOW_WIDTH, HarmonyResManagerDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony资源管理"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__projectFilePath = self.__operaIni.getValue(KEY_PROJECT_FILE_PATH, KEY_SECTION)
        self.__excelFilePath = self.__operaIni.getValue(KEY_EXCEL_FILE_PATH, KEY_SECTION)
        self.__asyncFuncManager = AsyncFuncManager()

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        groupBox = self.createGroupBox(self)

        vLayout.addWidget(groupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="资源管理")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        labelWidth = 120
        self.__projectFilePathWidget = DragInputWidget(label="工程路径",
                                                       text=self.__projectFilePath,
                                                       dirParam={KEY_CAPTION: '请选择Harmony工程代码路径'},
                                                       labelMinSize=QSize(labelWidth, 0),
                                                       toolTip='请选择Harmony工程代码路径',
                                                       required=True)
        vbox.addWidget(self.__projectFilePathWidget)

        self.__excelFilePathWidget = DragInputWidget(label="待处理字串excel文件",
                                                     text=self.__excelFilePath,
                                                     fileParam={KEY_CAPTION: '请选择待处理字串excel文件'},
                                                     labelMinSize=QSize(labelWidth, 0),
                                                     toolTip='请选择待处理字串excel文件')
        vbox.addWidget(self.__excelFilePathWidget)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="对比", onClicked=self.diffRes))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.__textEdit = CommonTextEdit()
        vbox.addWidget(self.__textEdit, 1)
        return box

    def diffRes(self):
        srcFileDirPath = self.__projectFilePathWidget.getData()
        if not srcFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择工程代码路径")
            return
        dstFileDirPath = self.__excelFilePathWidget.getData()
        if not dstFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择目标文件")
            return
        self.__operaIni.addItem(KEY_SECTION, KEY_PROJECT_FILE_PATH, srcFileDirPath)
        self.__operaIni.addItem(KEY_SECTION, KEY_EXCEL_FILE_PATH, dstFileDirPath)
        self.__operaIni.saveIni()

        self.__textEdit.clear()
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
            result = [
                {KEY_LOG: f'{dstFileDirPath} 总共缺失 {len(diff)} 条翻译，具体如下：\n', KEY_COLOR: ColorEnum.RED.value}]
            for index, name in enumerate(diff):
                result.append({KEY_LOG: f"{name}: {ListUtil.get(srcStrings, 'name', name, 'value', '')}\n",
                               KEY_COLOR: ColorEnum.BLUE.value if divmod(index, 2)[1] == 0 else ColorEnum.GREEN.value})
            self.__textEdit.standardOutput(result)
        except Exception as err:
            LogUtil.e(TAG, 'execDiff 错误信息：', err)
        self.__asyncFuncManager.hideLoading()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = HarmonyResManagerDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
