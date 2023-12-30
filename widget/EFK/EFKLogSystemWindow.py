# -*- coding: utf-8 -*-
# python 3.x
# Filename: EFKLogSystemWindow.py
# 定义一个EFKLogSystemWindow类实现EFK日志分析系统管理相关功能

import os.path
from concurrent.futures import as_completed, CancelledError
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.NetworkUtil import NetworkUtil
from util.OperaIni import *
from util.ProcessManager import KEY_VALUE, ProcessManager, KEY_PROGRAM
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


def waitEsSystemStart():
    return ShellUtil.waitExecFinished('curl -XGET http://localhost:9200',
                                      '"cluster_name" : "elk"'), 'waitEsSystemStart', ''


def waitKibanaSystemStart():
    return ShellUtil.waitExecFinished('netstat -ano | findstr 5601 | findstr "LISTENING"',
                                      '127.0.0.1:5601'), 'waitKibanaSystemStart', ''


class EFKLogSystemWindow(QMainWindow):
    windowList = []
    __showErrorDialogSignal = pyqtSignal(str)

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
        self.__executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="LogSystem_")
        self.__futureList = []
        self.__execResult = []
        self.__esSoftwarePath = None
        self.__kibanaSoftwarePath = None
        self.__filebeatSoftwarePath = None
        self.__processEnv = []
        self.__esProcessManager: ProcessManager = None
        self.__kibanaProcessManager: ProcessManager = None
        self.__filebeatProcessManager: ProcessManager = None

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.categoryManageGroupBox = self.createManageGroupBox()
        hLayout.addWidget(self.categoryManageGroupBox, 3)

        self.consoleTextEdit = CommonTextEdit(linkClicked=self.__linkClicked)
        hLayout.addWidget(self.consoleTextEdit, 2)

        self.__showErrorDialogSignal.connect(self.__showErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()

    # 重写关闭事件，回到第一界面
    def closeEvent(self, event):
        self.__destroy()
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
        self.__startSystemBtn = WidgetUtil.createPushButton(box, text='启动EFK系统',
                                                            onClicked=self.__startSystemClickEvent)
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

    def __startSystemClickEvent(self):
        LogUtil.i(TAG, '[__startSystemClickEvent]')
        self.consoleTextEdit.clear()
        softwarePath = self.__efkSoftwarePathWidget.getData()
        if not softwarePath:
            WidgetUtil.showErrorDialog(message="请输入软件安装路径")
            return
        self.__configManager.setEFKSoftwarePath(softwarePath)
        self.__configManager.saveConfigs()

        self.__asyncFuncManager.asyncExec(self.__startSystem, 'startSystem', (softwarePath,))
        pass

    def __startSystem(self, softwarePath):
        if not self.__parseEFKSoftwarePath(softwarePath):
            self.__showErrorDialogSignal.emit('请先下载安装相应软件')
            self.__asyncFuncManager.hideLoading()
            return
        self.__prepareProcessEnv()
        self.__startEsProcess()
        as_completed(self.__futureList)
        self.__asyncFuncManager.hideLoading()
        pass

    def __startEsProcess(self):
        LogUtil.i(TAG, '[__startEsProcess]')
        execCmd = ('cmd /c ' if PlatformUtil.isWindows() else '') + \
                  os.path.join(self.__esSoftwarePath, 'bin/elasticsearch')
        self.__esProcessManager = ProcessManager(name='elasticsearch',
                                                 cmdList=[{KEY_PROGRAM: execCmd}],
                                                 workingDir=self.__esSoftwarePath,
                                                 processEnv=self.__processEnv,
                                                 standardOutput=self.standardOutput,
                                                 standardError=self.standardError)
        future = self.__executor.submit(self.__esProcessManager.run)
        self.__futureList.append(future)
        waitFuture = self.__executor.submit(waitEsSystemStart)
        self.__futureList.append(waitFuture)
        for future in as_completed([future, waitFuture]):
            try:
                isSuccess, taskName, resultData = future.result()
                if taskName == 'waitEsSystemStart':
                    if isSuccess:
                        LogUtil.i(TAG, taskName, 'exec success.')
                        self.__startKibanaProcess()
                    else:
                        self.__destroy()
            except CancelledError as err:
                LogUtil.e(TAG, "[__startEsProcess] CancelledError", err)
        pass

    def __startKibanaProcess(self):
        LogUtil.i(TAG, '[__startKibanaProcess]')
        execCmd = ('cmd /c ' if PlatformUtil.isWindows() else '') + \
                  os.path.join(self.__kibanaSoftwarePath, 'bin/kibana')
        self.__kibanaProcessManager = ProcessManager(name='kibana',
                                                     cmdList=[{KEY_PROGRAM: execCmd}],
                                                     workingDir=self.__kibanaSoftwarePath,
                                                     processEnv=self.__processEnv,
                                                     standardOutput=self.standardOutput,
                                                     standardError=self.standardError)
        future = self.__executor.submit(self.__kibanaProcessManager.run)
        self.__futureList.append(future)
        waitFuture = self.__executor.submit(waitKibanaSystemStart)
        for future in as_completed([future, waitFuture]):
            try:
                isSuccess, taskName, resultData = future.result()
                if taskName == 'waitKibanaSystemStart':
                    if isSuccess:
                        self.__startFilebeatProcess()
                    else:
                        self.__destroy()
            except CancelledError as err:
                LogUtil.e(TAG, "[__startKibanaProcess] CancelledError", err)
        pass

    def __startFilebeatProcess(self):
        self.__asyncFuncManager.hideLoading()
        LogUtil.i(TAG, '[__startFilebeatProcess]')

    def __prepareProcessEnv(self):
        self.__processEnv = [
            {KEY_NAME: "ES_JAVA_HOME", KEY_VALUE: os.path.join(self.__esSoftwarePath, 'jdk')}
        ]
        LogUtil.d(TAG, '[__prepareProcessEnv]', self.__processEnv)

    def __parseEFKSoftwarePath(self, softwarePath):
        fileNames = os.listdir(softwarePath)
        esZipFp = None
        kibanaZipFp = None
        filebeatZipFp = None
        for fn in fileNames:
            fp = os.path.join(softwarePath, fn)
            if os.path.isfile(fp):
                if fn.startswith(SOFTWARE_NAME_ELASTICSEARCH):
                    esZipFp = fp
                elif fn.startswith(SOFTWARE_NAME_KIBANA):
                    kibanaZipFp = fp
                elif fn.startswith(SOFTWARE_NAME_FILEBEAT):
                    filebeatZipFp = fp
                continue
            if fn.startswith(SOFTWARE_NAME_ELASTICSEARCH):
                self.__esSoftwarePath = fp
            elif fn.startswith(SOFTWARE_NAME_KIBANA):
                self.__kibanaSoftwarePath = fp
            elif fn.startswith(SOFTWARE_NAME_FILEBEAT):
                self.__filebeatSoftwarePath = fp
        isSuccess = True
        if not self.__esSoftwarePath:
            if not esZipFp or not FileUtil.unzipFile(esZipFp, os.path.split(esZipFp)[0]):
                self.__showDownloadInfo(softwarePath, SOFTWARE_NAME_ELASTICSEARCH, DOWNLOAD_URLS[0])
                isSuccess = False
        if not self.__kibanaSoftwarePath:
            if not kibanaZipFp or not FileUtil.unzipFile(kibanaZipFp, os.path.split(kibanaZipFp)[0]):
                self.__showDownloadInfo(softwarePath, SOFTWARE_NAME_KIBANA, DOWNLOAD_URLS[1])
                isSuccess = False
        if not self.__filebeatSoftwarePath:
            if not filebeatZipFp or not FileUtil.unzipFile(filebeatZipFp, os.path.split(filebeatZipFp)[0]):
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

    def standardOutput(self, log):
        self.__appendLog(log, color=ColorEnum.BLUE)
        pass

    def standardError(self, log):
        self.__appendLog(log, color=ColorEnum.RED)
        pass

    def __appendLog(self, log: str, color: ColorEnum = ColorEnum.BLACK, limitLine=0):
        self.__execResult.append({KEY_LOG: log, KEY_COLOR: color.value})
        if len(self.__execResult) > limitLine:
            res = self.__execResult
            self.__execResult = []
            self.consoleTextEdit.standardOutput(res)

    def __showErrorDialog(self, msg):
        WidgetUtil.showErrorDialog(message=msg)

    def __destroy(self):
        LogUtil.i(TAG, '__destroy')
        if self.__filebeatProcessManager:
            self.__filebeatProcessManager.kill()
            self.__filebeatProcessManager = None
        if self.__kibanaProcessManager:
            self.__kibanaProcessManager.kill()
            self.__kibanaProcessManager = None
        if self.__esProcessManager:
            self.__esProcessManager.kill()
            self.__esProcessManager = None
        for future in self.__futureList:
            future.cancel()
        self.__futureList.clear()
        self.__executor.shutdown(wait=False, cancel_futures=True)
        self.__asyncFuncManager.hideLoading()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EFKLogSystemWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
