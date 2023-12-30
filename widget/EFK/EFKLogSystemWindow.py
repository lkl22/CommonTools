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
from widget.custom.DragInputWidget import DragInputWidget

TAG = "EFKLogSystemWindow"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'
MAX_BYTE = 200
DOWNLOAD_URLS = [
    'https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.3-windows-x86_64.zip',
    'https://artifacts.elastic.co/downloads/kibana/kibana-8.11.3-windows-x86_64.zip',
    'https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.3-windows-x86_64.zip',
]
SOFTWARE_NAME_ELASTICSEARCH = 'elasticsearch'
SOFTWARE_NAME_KIBANA = 'kibana'
SOFTWARE_NAME_FILEBEAT = 'filebeat'


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
        self.__esSoftwarePath = None
        self.__kibanaSoftwarePath = None
        self.__filebeatSoftwarePath = None

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
        vBox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=5)
        labelMinSize = QSize(130, 0)
        self.__efkSoftwarePathWidget = DragInputWidget(label='EFK软件路径',
                                                       text=self.__configManager.getEFKSoftwarePath(),
                                                       dirParam={KEY_CAPTION: 'EFK软件所在路径'},
                                                       labelMinSize=labelMinSize,
                                                       toolTip='EFK软件所在路径')
        vBox.addWidget(self.__efkSoftwarePathWidget)
        self.__logDirPathWidget = DragInputWidget(label='Log文件路径',
                                                  text=self.__configManager.getLogDirPath(),
                                                  dirParam={KEY_CAPTION: '日志文件所在路径'},
                                                  labelMinSize=labelMinSize,
                                                  toolTip='日志文件所在路径，待分析日志的根路径，默认：D:/log/，根路径下分Harmony|Android/group/[subDir/]日志格式')
        vBox.addWidget(self.__logDirPathWidget)
        self.__configDirPathWidget = DragInputWidget(label='config文件路径',
                                                     text=self.__configManager.getConfigDirPath(),
                                                     dirParam={KEY_CAPTION: 'filebeat config文件所在路径'},
                                                     labelMinSize=labelMinSize,
                                                     toolTip='filebeat配置文件存放路径，不配默认filebeat软件安装路径下')
        vBox.addWidget(self.__configDirPathWidget)
        hBox = WidgetUtil.createHBoxLayout()
        self.__startSystemBtn = WidgetUtil.createPushButton(box, text='启动EFK系统', onClicked=self.__startSystem)
        hBox.addWidget(self.__startSystemBtn)
        self.__stopSystemBtn = WidgetUtil.createPushButton(box, text='停止EFK系统', isEnable=False)
        hBox.addWidget(self.__stopSystemBtn)
        self.__restartSystemBtn = WidgetUtil.createPushButton(box, text='重启EFK系统', isEnable=False)
        hBox.addWidget(self.__restartSystemBtn)
        self.__openSystemBtn = WidgetUtil.createPushButton(box, text='打开EFK系统', isEnable=False)
        hBox.addWidget(self.__openSystemBtn)
        vBox.addLayout(hBox)
        vBox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def __startSystem(self):
        LogUtil.i(TAG, '[__startSystem]')
        self.consoleTextEdit.clear()
        softwarePath = self.__efkSoftwarePathWidget.getData()
        if not softwarePath:
            WidgetUtil.showErrorDialog(message="请输入软件安装路径")
            return
        self.__configManager.setEFKSoftwarePath(softwarePath)
        self.__configManager.saveConfigs()

        self.__parseEFKSoftwarePath(softwarePath)
        pass

    def __parseEFKSoftwarePath(self, softwarePath):
        fileNames = os.listdir(softwarePath)
        for fn in fileNames:
            if os.path.isfile(fn):
                continue
            parent, fp = os.path.split(fn)
            if fp.startswith(SOFTWARE_NAME_ELASTICSEARCH):
                self.__esSoftwarePath = fn
            elif fp.startswith(SOFTWARE_NAME_KIBANA):
                self.__kibanaSoftwarePath = fn
            elif fp.startswith(SOFTWARE_NAME_FILEBEAT):
                self.__filebeatSoftwarePath = fn
        isSuccess = True
        if not self.__esSoftwarePath:
            self.__showDownloadInfo(softwarePath, SOFTWARE_NAME_ELASTICSEARCH, DOWNLOAD_URLS[0])
            isSuccess = False
        if not self.__kibanaSoftwarePath:
            self.__showDownloadInfo(softwarePath, SOFTWARE_NAME_KIBANA, DOWNLOAD_URLS[1])
            isSuccess = False
        if not self.__filebeatSoftwarePath:
            self.__showDownloadInfo(softwarePath, SOFTWARE_NAME_FILEBEAT, DOWNLOAD_URLS[2])
            isSuccess = False
        return isSuccess

    def __showDownloadInfo(self, softwarePath, softwareName, downloadUrl):
        self.__appendLog(
            f'{softwarePath} 目录下没有找到 {softwareName} 软件，请点击链接下载安装 <a style=\"color: red\" ' \
            f'href=\"{downloadUrl}\">{downloadUrl}</a>',
            color=ColorEnum.PURPLE)

    def __cacheSliceLog(self, rule, log):
        # self.spliceLogResult[rule[KEY_NAME]][KEY_LOG].append(log)
        pass

    def __linkClicked(self, linkTxt):
        if NetworkUtil.isUrl(linkTxt):
            NetworkUtil.openWebBrowser(linkTxt)
        else:
            FileUtil.openFile(linkTxt)
        pass

    def __appendLog(self, log: str, color: ColorEnum = ColorEnum.BLACK, limitLine=0):
        self.execResult.append({KEY_LOG: log, KEY_COLOR: color.value})
        if len(self.execResult) > limitLine:
            res = self.execResult
            self.execResult = []
            self.consoleTextEdit.standardOutput(res)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EFKLogSystemWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
