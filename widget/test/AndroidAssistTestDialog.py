# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAssistTestDialog.py
# 定义一个AndroidAssistTestDialog类实现android测试相关功能
from util.AdbUtil import AdbUtil
from util.DateUtil import DateUtil
from util.JsonUtil import JsonUtil
from util.OperaIni import OperaIni
from util.WeditorUtil import *
from widget.test.EditTestStepDialog import *

ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME = 'com.lkl.androidtestassisttool'
ANDROID_TEST_ASSIST_TOOL_MAIN_ACTIVITY = '.MainActivity'
ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION = 10002
ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION_NAME = "1.0.2"


class AndroidAssistTestDialog(QtWidgets.QDialog):
    TABLE_KEY_TYPE = '操作类型'
    TABLE_KEY_DESC = '操作描述信息'

    def __init__(self, defaultPackageName="", defaultActivityName="", isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AndroidAssistTestDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AndroidAssistTestDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d("Init Android Assist Test Dialog")
        self.setObjectName("AndroidAssistTestDialog")

        self.hasCheckInstallFinish = False
        self.hasDownloadFinish = False
        self.notOftenUsedCmds = [
            {"text": '查看运行的Activities', "func": self.getRunningActivities},
            {"text": '是否安装', "func": self.isInstalled},
            {"text": '获取apk版本信息', "func": self.getVersionInfo},
            {"text": '查看应用安装路径', "func": self.getApkPath},
            {"text": '查看应用列表（系统）', "func": lambda: self.getPackageList("-s")},
            {"text": '查看应用列表（第三方）', "func": lambda: self.getPackageList("-3")},
            {"text": '获取设备公网IP地址', "func": self.getPubicIpAddr},
            {"text": '获取设备IP地址', "func": self.getIPAddr},
            {"text": '获取设备MAC地址', "func": self.getMACAddr}
        ]
        self.isDebug = isDebug
        if isDebug:
            self.operaIni = OperaIni("../../resources/config/BaseConfig.ini")
        else:
            self.operaIni = OperaIni()

        self.autoClickButtonTxt = "|".join(JsonUtil.decode(self.operaIni.getValue("autoClickButtonText", "test")))

        self.resize(AndroidAssistTestDialog.WINDOW_WIDTH, AndroidAssistTestDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AndroidAssistTestDialog.WINDOW_WIDTH, AndroidAssistTestDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android测试辅助工具"))

        self.defaultPackageName = defaultPackageName
        self.defaultActivityName = defaultActivityName
        self.execTestStepTableDatas = []
        self.adbGroupBoxHeight = 580

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        adbGroupBox = self.createGroupBox(self)
        vLayout.addWidget(adbGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="Android Test")
        sizePolicy = WidgetUtil.createSizePolicy()

        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入应用的包名：", minSize=QSize(80, const.HEIGHT)))
        self.packageNameLineEdit = WidgetUtil.createLineEdit(box, text=self.defaultPackageName,
                                                             holderText="请输入应用的包名",
                                                             sizePolicy=sizePolicy)
        hbox.addWidget(self.packageNameLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入要启动页面的activity：", minSize=QSize(80, const.HEIGHT)))
        self.activityNameLineEdit = WidgetUtil.createLineEdit(box, text=self.defaultActivityName,
                                                              holderText="请输入要启动页面的activity",
                                                              sizePolicy=sizePolicy)
        hbox.addWidget(self.activityNameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.cmdComboBox = WidgetUtil.createComboBox(box, sizePolicy=sizePolicy,
                                                     currentIndexChanged=self.cmdComboBoxIndexChanged)
        hbox.addWidget(self.cmdComboBox)
        for item in self.notOftenUsedCmds:
            self.cmdComboBox.addItem(item.get("text"))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="执行", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.execComboBoxCmd))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="清除应用数据与缓存", onClicked=self.clearApkData))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="启动应用/调起Activity", onClicked=self.startActivity))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="清缓存并重启应用", onClicked=self.clearDataAndRestartApp))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入要传输的文字：", minSize=QSize(80, const.HEIGHT)))
        self.inputTextLineEdit = WidgetUtil.createLineEdit(box, holderText="请输入要传输的文字", sizePolicy=sizePolicy)
        hbox.addWidget(self.inputTextLineEdit)
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="传输", minSize=QSize(100, const.HEIGHT), onClicked=self.inputText))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box, text="文件传输：", minSize=QSize(80, const.HEIGHT)))

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="电脑上的文件路径", onClicked=self.getPcFilePath))
        self.pcPathLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.pcPathLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="设备里的文件路径", minSize=QSize(80, const.HEIGHT)))
        self.phonePathLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.phonePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="复制设备里的文件到电脑", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.pullFile))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="复制电脑里的文件到设备", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.pushFile))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box, text="抓取视频、log：", minSize=QSize(80, const.HEIGHT)))

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="视频、Log存储路径", onClicked=self.getVideoLogFilePath))
        self.videoLogPathLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.videoLogPathLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入缓存空间大小：", alignment=Qt.AlignRight | Qt.AlignVCenter,
                                              minSize=QSize(150, const.HEIGHT)))
        self.cacheSizeSpinBox = WidgetUtil.createSpinBox(box, value=30, minValue=10, maxValue=100, step=5,
                                                         suffix="M", sizePolicy=sizePolicy)
        hbox.addWidget(self.cacheSizeSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请输入录屏总时长：", alignment=Qt.AlignRight | Qt.AlignVCenter,
                                              minSize=QSize(150, const.HEIGHT)))
        self.totalTimeSpinBox = WidgetUtil.createSpinBox(box, value=30, minValue=10, maxValue=300, step=5,
                                                         suffix="s", sizePolicy=sizePolicy)
        hbox.addWidget(self.totalTimeSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="测试环境准备", minSize=QSize(100, const.HEIGHT),
                                                   onClicked=self.prepareEvn))
        self.extractBtn = WidgetUtil.createPushButton(box, text="抓取视频、log", minSize=QSize(100, const.HEIGHT),
                                                      isEnable=False, onClicked=self.extractVideoAndLog)
        hbox.addWidget(self.extractBtn)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="操作信息：", minSize=QSize(80, const.HEIGHT)))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="清除操作信息", onClicked=self.clearExecRes))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.execResTE = WidgetUtil.createTextEdit(box, isReadOnly=True)
        vbox.addWidget(self.execResTE, 1)
        return box

    def checkAdbEnv(self):
        if not AdbUtil.isInstalledAdbEvn():
            WidgetUtil.showErrorDialog(message="adb指令未安装，请在 http://adbdownload.com/ 下载安装包，并配置好环境变量后重启！！！")
            return False
        res = AdbUtil.isDeviceConnect()
        if not res:
            WidgetUtil.showErrorDialog(message="Android设备未连接，请连接设备后重试！！！")
            return False
        return True

    def getPackageName(self):
        return self.packageNameLineEdit.text().strip()

    def getActivityName(self):
        return self.activityNameLineEdit.text().strip()

    def cmdComboBoxIndexChanged(self, index: int):
        LogUtil.e("cmdComboBoxIndexChanged %d" % index)
        pass

    def execComboBoxCmd(self):
        if not self.checkAdbEnv():
            return
        index = self.cmdComboBox.currentIndex()
        self.notOftenUsedCmds[index].get("func")()
        pass

    def isInstalled(self):
        packageName = self.getPackageName()
        if AdbUtil.isInstalled(self.getPackageName()):
            self.printRes("{} 已经安装".format(packageName))
        else:
            self.printRes("{} 未安装".format(packageName))
        pass

    def getVersionInfo(self):
        packageName = self.getPackageName()
        self.printRes('{} 的版本号：{} 版本名：{}'.format(packageName, AdbUtil.getVersionCode(packageName, -1),
                                                 AdbUtil.getVersionName(packageName, "not installed")))
        pass

    def getApkPath(self):
        packageName = self.getPackageName()
        self.printRes('{} 的安装路径：{}'.format(packageName, AdbUtil.getApkPath(packageName)))
        pass

    def getPackageList(self, params):
        self.printRes(f"\n\n获取安装应用开始（{params}）：", '#0f0')
        self.printCmdRes(*AdbUtil.getPackageList(params))
        self.printRes("获取安装应用结束", '#0f0')
        pass

    def getIPAddr(self):
        self.printRes(f"\n\n获取设备IP地址开始：", '#0f0')
        self.printCmdRes(*AdbUtil.getIPAddr())
        self.printRes("获取设备IP地址结束", '#0f0')
        pass

    def getMACAddr(self):
        self.printRes(f"\n\n获取设备MAC地址开始：", '#0f0')
        self.printCmdRes(*AdbUtil.getMACAddr())
        self.printRes("获取设备MAC地址结束", '#0f0')
        pass

    def getPubicIpAddr(self):
        if not self.checkTestApkInstall():
            return
        self.printRes(f"\n\n获取设备公网IP地址开始：", '#0f0')
        ip = AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", 'getPublicIpAddr'),
                                          AdbUtil.putBooleanExtra("clearPublicIp", True))
        retryTimes = 5
        while not ip and retryTimes > 0:
            retryTimes -= 1
            time.sleep(1)
            ip = AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", 'getPublicIpAddr'))

        if ip:
            self.printRes(f"获取设备公网IP地址：{ip}")
        else:
            self.printRes("获取失败，请检查网络稍后重试。", '#f00')

        self.printRes("获取设备公网IP地址结束", '#0f0')
        pass

    def getRunningActivities(self):
        self.printRes('正在运行的Activities：\n{}'.format(AdbUtil.getRunningActivities()))
        pass

    def clearApkData(self):
        if not self.checkAdbEnv():
            return
        packageName = self.getPackageName()
        if not packageName:
            WidgetUtil.showErrorDialog(message="请先输入应用的包名！")
            return
        self.printRes('{} 清除数据结果：{}'.format(packageName, AdbUtil.clearApkData(packageName)))
        pass

    def startActivity(self):
        if not self.checkAdbEnv():
            return
        packageName = self.getPackageName()
        if not packageName:
            WidgetUtil.showErrorDialog(message="请先输入应用的包名！")
            return
        self.printRes('{} 启动结果：{}'.format(packageName, AdbUtil.startActivity(packageName, self.getActivityName())))
        pass

    def clearDataAndRestartApp(self):
        if not self.checkAdbEnv():
            return
        packageName = self.getPackageName()
        if not packageName:
            WidgetUtil.showErrorDialog(message="请先输入应用的包名！")
            return
        self.printRes('{} 清除数据结果：{}'.format(packageName, AdbUtil.clearApkData(packageName)))
        self.printRes('{} 启动结果：{}'.format(packageName, AdbUtil.startActivity(packageName)))
        pass

    def inputText(self):
        if not self.checkAdbEnv():
            return
        if AdbUtil.inputBase64Text(self.inputTextLineEdit.text().strip()):
            self.printRes("已经传输完成。")
        pass

    def getPcFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.pcPathLineEdit.setText(fp)
        pass

    def pullFile(self):
        if not self.checkAdbEnv():
            return
        pcPath = self.pcPathLineEdit.text().strip()
        phonePath = self.phonePathLineEdit.text().strip()
        self.printRes("复制设备里的文件到电脑: ")
        self.printCmdRes(*AdbUtil.pullFile(phonePath, pcPath))
        pass

    def pushFile(self):
        if not self.checkAdbEnv():
            return
        pcPath = self.pcPathLineEdit.text().strip()
        phonePath = self.phonePathLineEdit.text().strip()
        self.printRes("复制电脑里的文件到设备: ")
        self.printCmdRes(*AdbUtil.pushFile(pcPath, phonePath))
        pass

    def getVideoLogFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.videoLogPathLineEdit.setText(fp)
        pass

    def prepareEvn(self):
        if not self.checkAdbEnv():
            return
        videoLogPath = self.videoLogPathLineEdit.text().strip()
        if not videoLogPath:
            WidgetUtil.showErrorDialog(message="请设置视频、log文件保存目录")
            return
        FileUtil.mkDirs(videoLogPath)
        if not self.checkTestApkInstall():
            return

        self.printRes("准备启动apk，并准备环境。。。")
        while AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", "isEvnReady")) == "false":
            AdbUtil.forceStopApp(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)
            AdbUtil.startActivity(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME, ANDROID_TEST_ASSIST_TOOL_MAIN_ACTIVITY,
                                  " ".join(AdbUtil.putIntExtra("cacheSize", self.cacheSizeSpinBox.value())))
            AdbUtil.autoClickBtn(self.autoClickButtonTxt)
        self.printRes("准备捕获日志。。。")
        tempLog = open(os.path.join(videoLogPath, "tempLog"), 'w')
        ShellUtil.run("adb logcat -c && adb logcat -v threadtime", tempLog)
        self.printRes("测试环境已经准备完成。")
        self.extractBtn.setEnabled(True)
        pass

    def checkTestApkInstall(self):
        if not self.hasCheckInstallFinish and int(AdbUtil.getVersionCode(
                ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)) < ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION:
            AdbUtil.uninstallApk(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)
            self.printRes("准备下载测试apk。。。")
            downloadFile = "v{}.apk".format(ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION_NAME)
            if os.path.isfile(downloadFile):
                self.printRes("apk已经存在。。。")
                self.hasDownloadFinish = True
            if not self.hasDownloadFinish:
                url = f"https://github.com/lkl22/AndroidTestAssistTool/releases/download/v{ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION_NAME}/app-release.apk"
                if not NetworkUtil.downloadPackage(url, downloadFile):
                    WidgetUtil.showErrorDialog(message="下载apk失败，请检查网络后，重新尝试！")
                    FileUtil.removeFile(downloadFile)
                    return False
                self.hasDownloadFinish = True
            self.printRes("apk下载完成，准备安装。。。")
            out, err = AdbUtil.installApk(downloadFile)
            self.printCmdRes(out, err)
            while int(AdbUtil.getVersionCode(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)) < \
                    ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION:
                AdbUtil.autoClickBtn(self.autoClickButtonTxt)

        self.hasCheckInstallFinish = True
        return True

    def extractVideoAndLog(self):
        nowTimestamp = DateUtil.nowTimestamp(True)
        AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", "startMuxer"),
                                     AdbUtil.putLongExtra("timestamp", nowTimestamp),
                                     AdbUtil.putIntExtra("totalTime", self.totalTimeSpinBox.value()))
        AdbUtil.killAdbServer()
        AdbUtil.startAdbServer()
        videoLogPath = self.videoLogPathLineEdit.text().strip()
        # 提取log
        self.extractLog(nowTimestamp, videoLogPath)
        while AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", 'isFinishedMuxer'),
                                           AdbUtil.putLongExtra("timestamp", nowTimestamp)) == 'false':
            time.sleep(0.2)
        videoPhoneFp = AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", 'getMuxerVideo'),
                                                    AdbUtil.putLongExtra("timestamp", nowTimestamp))
        AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", 'rmFinishedMuxer'),
                                     AdbUtil.putLongExtra("timestamp", nowTimestamp))
        finalVideoFp = os.path.join(videoLogPath, FileUtil.getFileName(videoPhoneFp))
        AdbUtil.pullFile(videoPhoneFp, finalVideoFp)
        self.printRes("视频录制成功: {}".format(finalVideoFp))

        # 重新准备测试环境
        self.extractBtn.setEnabled(False)
        self.prepareEvn()
        pass

    def extractLog(self, nowTimestamp: int, videoLogPath: str):
        self.printRes("开始提取日志。。。")
        timeFormat: str = "%m-%d %H:%M:%S"
        srcFileName = DateUtil.timestamp2Time(int(nowTimestamp / 1000), "%Y%m%d_%H%M%S") + '_backup.log'
        FileUtil.modifyFilesName([os.path.join(videoLogPath, 'tempLog')], srcFileName)
        dstFile = os.path.join(videoLogPath,
                               DateUtil.timestamp2Time(int(nowTimestamp / 1000), "%Y%m%d_%H%M%S") + '.log')
        AdbUtil.extractLog(os.path.join(videoLogPath, srcFileName), dstFile,
                           DateUtil.timestamp2Time(nowTimestamp / 1000 - self.totalTimeSpinBox.value(), timeFormat),
                           DateUtil.timestamp2Time(nowTimestamp / 1000, timeFormat))
        self.printRes("log抓取成功: {}".format(dstFile))

    def clearExecRes(self):
        self.execResTE.clear()
        pass

    def execCmd(self, cmd: str):
        LogUtil.d("exec cmd:", cmd)
        if cmd:
            self.printRes('执行指令：')
            self.printRes(cmd + '\n')
            out, err = ShellUtil.exec(cmd)
            if out:
                self.printRes('输出结果：')
                self.printRes(out)
            if err:
                self.printRes('错误信息：\n', '#f00')
                self.printRes(err, '#f00')
                return False
        return True

    def printCmdRes(self, out, err):
        if out:
            if 'error:' in out:
                self.printRes(out, '#f00')
            else:
                self.printRes(out)
        if err:
            self.printRes(err, '#f00')

    def printRes(self, res: str = '', color='#00f'):
        LogUtil.i("printRes", res)
        WidgetUtil.appendTextEdit(self.execResTE, res, color)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidAssistTestDialog(defaultPackageName='com.lkl.androidtestassisttool',
                                     defaultActivityName='.MainActivity',
                                     isDebug=True)
    window.show()
    sys.exit(app.exec_())
