# -*- coding: utf-8 -*-
# python 3.x
# Filename: EFKLogSystemWindow.py
# 定义一个EFKLogSystemWindow类实现EFK日志分析系统管理相关功能

import os.path
from concurrent.futures import as_completed, CancelledError, Future
from concurrent.futures.thread import ThreadPoolExecutor

from PyQt5.QtWidgets import QMainWindow

from constant.ColorEnum import ColorEnum
from manager.AsyncFuncManager import AsyncFuncManager
from util.DialogUtil import *
from util.ListUtil import ListUtil
from util.NetworkUtil import NetworkUtil
from util.OperaIni import *
from util.ProcessManager import *
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

TYPE_READY = 1
TYPE_STOPPED = 2


def waitEsSystemStart():
    return ShellUtil.waitExecFinished('curl -XGET http://localhost:9200',
                                      '"cluster_name" : "elk"'), 'waitEsSystemStart', ''


def waitKibanaSystemStart():
    return ShellUtil.waitExecFinished('netstat -ano | findstr 5601 | findstr "LISTENING"',
                                      '127.0.0.1:5601'), 'waitKibanaSystemStart', ''


def startEFKServiceSystem():
    return ShellUtil.runCode('''from widget.EFK.EFKServiceSystem import *
EFKServiceSystem.start()'''), 'startEFKServiceSystem', ''


def showErrorDialog(msg):
    WidgetUtil.showErrorDialog(message=msg)


class EFKLogSystemWindow(QMainWindow):
    windowList = []
    __showErrorDialogSignal = pyqtSignal(str)
    __changeBtnStatusSignal = pyqtSignal(int)

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        EFKLogSystemWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        EFKLogSystemWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, f'Init EFK Log System Window. pid: {os.getpid()}')
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
        self.__filebeatFuture: Future = None
        self.__efkServiceFuture: Future = None

        self.__filebeatConfigDir = os.path.join(FileUtil.getProjectPath(), 'resources/efk/config/filebeat')
        self.__logDir = self.__configManager.getLogDirPath()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        vBox = WidgetUtil.createVBoxLayout()
        self.efkManageGroupBox = self.createManageGroupBox()
        vBox.addWidget(self.efkManageGroupBox)
        self.phoneLogGroupBox = self.createPhoneLogGroupBox()
        vBox.addWidget(self.phoneLogGroupBox)
        vBox.addSpacerItem(WidgetUtil.createVSpacerItem())
        hLayout.addLayout(vBox, 3)

        self.consoleTextEdit = CommonTextEdit(linkClicked=self.__linkClicked)
        hLayout.addWidget(self.consoleTextEdit, 2)

        self.__showErrorDialogSignal.connect(showErrorDialog)
        self.__changeBtnStatusSignal.connect(self.__changeBtnStatus)
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
        box = WidgetUtil.createGroupBox(self, title="EFK系统管理")
        vBox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=5)
        labelMinSize = QSize(130, 0)
        self.__efkSoftwarePathWidget = DragInputWidget(label='EFK软件路径',
                                                       text=self.__configManager.getEFKSoftwarePath(),
                                                       dirParam={KEY_CAPTION: 'EFK软件所在路径'},
                                                       labelMinSize=labelMinSize,
                                                       toolTip='EFK软件所在路径',
                                                       textChanged=self.__softwarePathChanged,
                                                       required=True)
        vBox.addWidget(self.__efkSoftwarePathWidget)
        self.__logDirPathWidget = DragInputWidget(label='Log文件路径',
                                                  text=self.__configManager.getLogDirPath(),
                                                  dirParam={KEY_CAPTION: '日志文件所在路径'},
                                                  labelMinSize=labelMinSize,
                                                  toolTip='日志文件所在路径，待分析日志的根路径，默认：D:/log/，根路径下分Harmony|Android/group/[subDir/]日志格式',
                                                  textChanged=self.__logPathChanged)
        vBox.addWidget(self.__logDirPathWidget)

        self.__notepadDirPathWidget = DragInputWidget(label='notepad++安装路径',
                                                      text=self.__configManager.getNotepadDirPath(),
                                                      dirParam={KEY_CAPTION: 'notepad++安装路径'},
                                                      labelMinSize=labelMinSize,
                                                      toolTip='notepad++安装路径，可以通过notepad++打开对应文件，不配将不会通过notepad++打开',
                                                      textChanged=self.__notepadDirPathWidgetChanged)
        vBox.addWidget(self.__notepadDirPathWidget)

        hBox = WidgetUtil.createHBoxLayout()
        self.__openConfigDirBtn = WidgetUtil.createPushButton(box, text='打开配置文件路径',
                                                              onClicked=self.__openConfigDirEvent)
        hBox.addWidget(self.__openConfigDirBtn)
        self.__openFieldCfgDocBtn = WidgetUtil.createPushButton(box, text='打开配置data view Field指导',
                                                                onClicked=self.__openFieldCfgDocEvent)
        hBox.addWidget(self.__openFieldCfgDocBtn)
        vBox.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout()
        self.__startSystemBtn = WidgetUtil.createPushButton(box, text='启动EFK系统',
                                                            onClicked=self.__startSystemClickEvent)
        hBox.addWidget(self.__startSystemBtn)
        self.__stopSystemBtn = WidgetUtil.createPushButton(box, text='停止EFK系统', isEnable=False,
                                                           onClicked=self.__stopSystemClickEvent)
        hBox.addWidget(self.__stopSystemBtn)
        self.__restartSystemBtn = WidgetUtil.createPushButton(box, text='重启EFK系统', isEnable=False,
                                                              onClicked=self.__restartSystemClickEvent)
        hBox.addWidget(self.__restartSystemBtn)
        self.__openSystemBtn = WidgetUtil.createPushButton(box, text='打开EFK系统', isEnable=False,
                                                           onClicked=self.__openSystemClickEvent)
        hBox.addWidget(self.__openSystemBtn)
        vBox.addLayout(hBox)
        vBox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def createPhoneLogGroupBox(self):
        box = WidgetUtil.createGroupBox(self, title="手机日志系统")
        vBox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=5)
        labelMinSize = QSize(130, 0)

        hBox = WidgetUtil.createHBoxLayout()
        self.__clearPhoneLogBtn = WidgetUtil.createPushButton(box, text='清除手机日志',
                                                              onClicked=self.__clearPhoneLogEvent)
        hBox.addWidget(self.__clearPhoneLogBtn)
        self.__startLogcatBtn = WidgetUtil.createPushButton(box, text='启动实时日志',
                                                            onClicked=self.__startLogcatEvent)
        hBox.addWidget(self.__startLogcatBtn)
        vBox.addLayout(hBox)
        vBox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def __softwarePathChanged(self, fp):
        LogUtil.i(TAG, '[__softwarePathChanged]', fp)
        self.__configManager.setInited(False)

    def __logPathChanged(self, fp):
        LogUtil.i(TAG, '[__logPathChanged]', fp)
        self.__refreshLogDir()
        if not self.__startSystemBtn.isEnabled():
            self.__startFilebeatProcess()

    def __notepadDirPathWidgetChanged(self, fp):
        LogUtil.i(TAG, '[__notepadDirPathWidgetChanged]', fp)
        self.__configManager.setNotepadDirPath(fp)

    def __changeBtnStatus(self, type: int):
        if type == TYPE_READY:
            self.__startSystemBtn.setEnabled(False)
            self.__stopSystemBtn.setEnabled(True)
            self.__restartSystemBtn.setEnabled(True)
            self.__openSystemBtn.setEnabled(True)
        elif type == TYPE_STOPPED:
            self.__startSystemBtn.setEnabled(True)
            self.__stopSystemBtn.setEnabled(False)
            self.__restartSystemBtn.setEnabled(False)
            self.__openSystemBtn.setEnabled(False)

    def __openConfigDirEvent(self):
        FileUtil.openFile(self.__filebeatConfigDir)

    def __openFieldCfgDocEvent(self):
        NetworkUtil.openWebBrowser(
            'https://github.com/lkl22/CommonTools/blob/master/doc/efkSystem/editDataViewField.md')

    def __startSystemClickEvent(self):
        LogUtil.i(TAG, '[__startSystemClickEvent]')
        self.__executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="LogSystem_")
        self.consoleTextEdit.clear()
        softwarePath = self.__efkSoftwarePathWidget.getData()
        if not softwarePath:
            WidgetUtil.showErrorDialog(message="请输入软件安装路径")
            return
        self.__configManager.setEFKSoftwarePath(softwarePath)
        self.__startSystemBtn.setEnabled(False)
        self.__asyncFuncManager.asyncExec(self.__startSystem, 'startSystem', (softwarePath,))
        pass

    def __stopSystemClickEvent(self):
        LogUtil.i(TAG, '[__stopSystemClickEvent]')
        self.__destroy()
        self.__changeBtnStatusSignal.emit(TYPE_STOPPED)
        pass

    def __restartSystemClickEvent(self):
        LogUtil.i(TAG, '[__restartSystemClickEvent]')
        self.__startFilebeatProcess()
        pass

    def __openSystemClickEvent(self):
        LogUtil.i(TAG, '[__openSystemClickEvent]')
        NetworkUtil.openWebBrowser('http://localhost:5601')
        pass

    def __startSystem(self, softwarePath):
        if not self.__parseEFKSoftwarePath(softwarePath):
            self.__showErrorDialogSignal.emit('请先下载安装相应软件')
            self.__changeBtnStatusSignal.emit(TYPE_STOPPED)
            self.__asyncFuncManager.hideLoading()
            return
        self.__refreshConfig()
        self.__prepareProcessEnv()
        self.__startEsProcess()
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
                    ListUtil.remove(self.__futureList, waitFuture)
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
                    ListUtil.remove(self.__futureList, waitFuture)
                    if isSuccess:
                        self.__asyncFuncManager.hideLoading()
                        self.__changeBtnStatusSignal.emit(TYPE_READY)
                        self.__startFilebeatProcess()
                        self.__startEFKServiceProcess()
                    else:
                        self.__destroy()
            except CancelledError as err:
                LogUtil.e(TAG, "[__startKibanaProcess] CancelledError", err)
        pass

    def __startEFKServiceProcess(self):
        LogUtil.i(TAG, '[__startEFKServiceProcess]')
        self.__efkServiceFuture = self.__executor.submit(startEFKServiceSystem)
        for future in as_completed([self.__efkServiceFuture]):
            try:
                _, taskName, resultData = future.result()
            except CancelledError as err:
                LogUtil.e(TAG, "[__startEFKServiceProcess] CancelledError", err)
        pass

    def __startFilebeatProcess(self):
        LogUtil.i(TAG, '[__startFilebeatProcess]')
        self.__killFilebeatSystem()
        dataDir = FileUtil.formatPath(os.path.join(self.__filebeatSoftwarePath, "data"))
        softwareRunlogDir = FileUtil.formatPath(os.path.join(self.__filebeatSoftwarePath, "logs"))
        cmdList = [
            # 清除es的data stream
            {KEY_PROGRAM: 'curl', KEY_ARGUMENTS: '-X DELETE http://localhost:9200/_data_stream/filebeat-8.11.3'},
            {KEY_PROGRAM: 'rmdir', KEY_ARGUMENTS: f'/s /q "{dataDir}"'},
            {KEY_PROGRAM: 'rmdir', KEY_ARGUMENTS: f'/s /q "{softwareRunlogDir}"'},
            {
                KEY_PROGRAM: FileUtil.formatPath(os.path.join(self.__filebeatSoftwarePath, "filebeat")),
                KEY_ARGUMENTS: f'-e -c "{FileUtil.formatPath(os.path.join(self.__filebeatConfigDir, "filebeat.yml"))}" ' +
                               f'-E "scriptPath={self.__filebeatConfigDir}" ' +
                               f'-E "logDir={self.__logDir}" '
            },
        ]
        self.__filebeatProcessManager = ProcessManager(name='filebeat',
                                                       cmdList=cmdList,
                                                       workingDir=self.__filebeatSoftwarePath,
                                                       processEnv=self.__processEnv,
                                                       standardOutput=self.standardOutput,
                                                       standardError=self.standardError)
        self.__filebeatFuture = self.__executor.submit(self.__filebeatProcessManager.run)
        self.__futureList.append(self.__filebeatFuture)

    def __refreshConfig(self):
        LogUtil.i(TAG, '[__refreshConfig]', self.__configManager.isInit())
        if self.__configManager.isInit():
            return
        FileUtil.modifyFilePath(os.path.join(FileUtil.getProjectPath(), 'resources/efk/config/elasticsearch.yml'),
                                os.path.join(self.__esSoftwarePath, 'config/elasticsearch.yml'))
        FileUtil.modifyFilePath(os.path.join(FileUtil.getProjectPath(), 'resources/efk/config/kibana.yml'),
                                os.path.join(self.__kibanaSoftwarePath, 'config/kibana.yml'))
        self.__refreshLogDir()
        self.__configManager.setInited()
        pass

    def __refreshLogDir(self):
        logDir = FileUtil.formatPath(self.__logDirPathWidget.getData())
        if logDir:
            self.__logDir = logDir
            self.__configManager.setLogDirPath(logDir)
        FileUtil.mkDirs(os.path.join(logDir, 'harmony/realtime'))
        FileUtil.mkDirs(os.path.join(logDir, 'android/realtime'))
        LogUtil.i(TAG, '[__refreshLogDir]', logDir)
        pass

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

    def __killFilebeatSystem(self):
        LogUtil.i(TAG, '__killFilebeatSystem')
        if self.__filebeatProcessManager:
            self.__filebeatProcessManager.kill()
            self.__filebeatProcessManager = None
        if self.__filebeatFuture:
            self.__filebeatFuture.cancel()
            ListUtil.remove(self.__futureList, self.__filebeatFuture)

    def __destroy(self):
        LogUtil.i(TAG, '__destroy')
        self.__changeBtnStatusSignal.emit(TYPE_STOPPED)
        self.__killFilebeatSystem()
        if self.__kibanaProcessManager:
            self.__kibanaProcessManager.kill()
            self.__kibanaProcessManager = None
            ShellUtil.killByPids(ShellUtil.findPidsByPort('5601'), excludePid=os.getpid())
        if self.__esProcessManager:
            self.__esProcessManager.kill()
            self.__esProcessManager = None
            ShellUtil.killByPids(ShellUtil.findPidsByPort('9200'), excludePid=os.getpid())
        if self.__efkServiceFuture:
            self.__efkServiceFuture.cancel()
            self.__efkServiceFuture = None
            ShellUtil.killByPids(ShellUtil.findPidsByPort('5000'), excludePid=os.getpid())
        for future in self.__futureList:
            future.cancel()
        self.__futureList.clear()
        if self.__executor:
            self.__executor.shutdown(wait=False, cancel_futures=True)
            self.__executor = None
        self.__asyncFuncManager.hideLoading()

    def __clearPhoneLogEvent(self):
        LogUtil.i(TAG, '__clearPhoneLogEvent')
        pass

    def __startLogcatEvent(self):
        LogUtil.i(TAG, '__startLogcatEvent')
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EFKLogSystemWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
