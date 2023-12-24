# -*- coding: utf-8 -*-
# python 3.x
# Filename: EFKLogSystemWindow.py
# 定义一个EFKLogSystemWindow类实现EFK日志分析系统管理相关功能
from PyQt5.QtWidgets import QMainWindow

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.NetworkUtil import NetworkUtil
from util.OperaIni import *
from widget.EFK.EFKLogSystemConfigManager import EFKLogSystemConfigManager
from widget.custom.CommonTextEdit import CommonTextEdit

TAG = "EFKLogSystemWindow"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'
MAX_BYTE = 200
download_urls = [
    'https://artifacts.elastic.co/downloads/kibana/kibana-8.11.3-windows-x86_64.zip',
    'https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.3-windows-x86_64.zip',
    'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.3-windows-x86_64.zip'
]


class EFKLogSystemWindow(QMainWindow):
    windowList = []

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        EFKLogSystemWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        EFKLogSystemWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init EFK Log System Window")
        self.setObjectName("EFKLogSystemWindow")
        self.resize(EFKLogSystemWindow.WINDOW_WIDTH, EFKLogSystemWindow.WINDOW_HEIGHT)
        # self.setFixedSize(EFKLogSystemWindow.WINDOW_WIDTH, EFKLogSystemWindow.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="EFK日志系统管理工具"))

        self.__isDebug = isDebug
        self.__configManager = EFKLogSystemConfigManager()
        self.__asyncFuncManager = AsyncFuncManager()
        self.execResult = []

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.categoryManageGroupBox = self.createManageGroupBox()
        hLayout.addWidget(self.categoryManageGroupBox, 3)

        self.consoleTextEdit = CommonTextEdit(linkClicked=self.__linkClicked)
        hLayout.addWidget(self.consoleTextEdit, 2)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    # 重写关闭事件，回到第一界面
    def closeEvent(self, event):
        if self.__isDebug:
            return
        from widget.MainWidget import MainWidget
        window = MainWidget()
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        window.show()
        event.accept()
        pass

    def createManageGroupBox(self):
        box = WidgetUtil.createGroupBox(self, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        # vbox.addWidget(self.categoryManagerWidget)
        # vbox.addWidget(self.categoryConfigWidget, 7)
        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))

        return box

    def __cacheSliceLog(self, rule, log):
        # self.spliceLogResult[rule[KEY_NAME]][KEY_LOG].append(log)
        pass

    def __linkClicked(self, linkTxt):
        if NetworkUtil.isUrl(linkTxt):
            NetworkUtil.openWebBrowser(linkTxt)
        else:
            FileUtil.openFile(linkTxt)
        pass

    def __appendLog(self, log: str, color: ColorEnum = ColorEnum.BLACK):
        self.execResult.append({KEY_LOG: log, KEY_COLOR: color.value})
        if len(self.execResult) > 18:
            res = self.execResult
            self.execResult = []
            self.consoleTextEdit.standardOutput(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EFKLogSystemWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
