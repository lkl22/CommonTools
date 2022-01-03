# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidAssistTestDialog.py
# 定义一个AndroidAssistTestDialog类实现android测试相关功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.TestStepConst import *
from constant.WidgetConst import *
from util.AdbUtil import AdbUtil
from util.FileUtil import *
from util.DialogUtil import *
from util.ShellUtil import *
from util.LogUtil import *
from util.WeditorUtil import *
from widget.test.EditTestStepDialog import *

ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME = 'com.lkl.androidtestassisttool'
ANDROID_TEST_ASSIST_TOOL_MAIN_ACTIVITY = '.MainActivity'
ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION = 10001
ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION_NAME = "1.0.1"


class AndroidAssistTestDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 680
    TABLE_KEY_TYPE = '操作类型'
    TABLE_KEY_DESC = '操作描述信息'

    def __init__(self, defaultPackageName="", defaultActivityName=""):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android Assist Test Dialog")
        self.setObjectName("AndroidAssistTestDialog")

        self.hasCheckInstallFinish = False
        self.notOftenUsedCmds = [
            {"text": '查看运行的Activities', "func": self.getRunningActivities},
            {"text": '是否安装', "func": self.isInstalled},
            {"text": '获取apk版本信息', "func": self.getVersionInfo},
            {"text": '查看应用安装路径', "func": self.getApkPath}
        ]

        self.resize(AndroidAssistTestDialog.WINDOW_WIDTH, AndroidAssistTestDialog.WINDOW_HEIGHT)
        self.setFixedSize(AndroidAssistTestDialog.WINDOW_WIDTH, AndroidAssistTestDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android测试辅助工具"))

        self.defaultPackageName = defaultPackageName
        self.u: Uiautomator = None
        self.t: AutoTestUtil = None
        self.defaultActivityName = defaultActivityName
        self.execTestStepTableDatas = []
        self.adbGroupBoxHeight = 580

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(
            QRect(const.PADDING, const.PADDING, AndroidAssistTestDialog.WINDOW_WIDTH - const.PADDING * 2,
                  AndroidAssistTestDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        adbGroupBox = self.createGroupBox(layoutWidget)
        vLayout.addWidget(adbGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidAssistTestDialog.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="Android Test", minSize=QSize(width, self.adbGroupBoxHeight))
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="请输入应用的包名：", minSize=QSize(80, const.HEIGHT))
        self.packageNameLineEdit = WidgetUtil.createLineEdit(splitter, text=self.defaultPackageName,
                                                             holderText="请输入应用的包名",
                                                             sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="请输入要启动页面的activity：", minSize=QSize(80, const.HEIGHT))
        self.activityNameLineEdit = WidgetUtil.createLineEdit(splitter, text=self.defaultActivityName,
                                                              holderText="请输入要启动页面的activity",
                                                              sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, int(const.HEIGHT * 1.2)))
        self.cmdComboBox = WidgetUtil.createComboBox(splitter, sizePolicy=sizePolicy, currentIndexChanged=self.cmdComboBoxIndexChanged)
        for item in self.notOftenUsedCmds:
            self.cmdComboBox.addItem(item.get("text"))
        WidgetUtil.createPushButton(splitter, text="执行", fixedSize=QSize(100, const.HEIGHT), onClicked=self.execComboBoxCmd)

        yPos += int(const.HEIGHT_OFFSET * 1.2)
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="清除应用数据与缓存", onClicked=self.clearApkData)
        WidgetUtil.createPushButton(splitter, text="启动应用/调起Activity", onClicked=self.startActivity)
        WidgetUtil.createPushButton(splitter, text="清缓存并重启应用", onClicked=self.clearDataAndRestartApp)

        yPos += int(const.HEIGHT_OFFSET * 1.5)
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="请输入要传输的文字：", minSize=QSize(80, const.HEIGHT))
        self.inputTextLineEdit = WidgetUtil.createLineEdit(splitter, holderText="请输入要传输的文字", sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="传输", minSize=QSize(100, const.HEIGHT), onClicked=self.inputText)

        yPos += int(const.HEIGHT_OFFSET * 1.5)
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="文件传输：", minSize=QSize(80, const.HEIGHT))
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="电脑上的文件路径", onClicked=self.getPcFilePath)
        self.pcPathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="设备里的文件路径", minSize=QSize(80, const.HEIGHT))
        self.phonePathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, int(width / 2), const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="复制设备里的文件到电脑", minSize=QSize(100, const.HEIGHT),
                                    onClicked=self.pullFile)
        WidgetUtil.createPushButton(splitter, text="复制电脑里的文件到设备", minSize=QSize(100, const.HEIGHT),
                                    onClicked=self.pushFile)

        yPos += int(const.HEIGHT_OFFSET * 1.5)
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="抓取视频、log：", minSize=QSize(80, const.HEIGHT))
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="测试环境准备", minSize=QSize(100, const.HEIGHT), onClicked=self.prepareEvn)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="操作信息：", minSize=QSize(80, const.HEIGHT))
        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 180))
        self.execResTE = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        return box

    def getPackageName(self):
        return self.packageNameLineEdit.text().strip()

    def getActivityName(self):
        return self.activityNameLineEdit.text().strip()

    def cmdComboBoxIndexChanged(self, index: int):
        LogUtil.e("cmdComboBoxIndexChanged %d" % index)
        pass

    def execComboBoxCmd(self):
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

    def getRunningActivities(self):
        self.printRes('正在运行的Activities：\n{}'.format(AdbUtil.getRunningActivities()))
        pass

    def clearApkData(self):
        packageName = self.getPackageName()
        self.printRes('{} 清除数据结果：{}'.format(packageName, AdbUtil.clearApkData(packageName)))
        pass

    def startActivity(self):
        packageName = self.getPackageName()
        self.printRes('{} 启动结果：{}'.format(packageName, AdbUtil.startActivity(packageName, self.getActivityName())))
        pass

    def clearDataAndRestartApp(self):
        packageName = self.getPackageName()
        self.printRes('{} 清除数据结果：{}'.format(packageName, AdbUtil.clearApkData(packageName)))
        self.printRes('{} 启动结果：{}'.format(packageName, AdbUtil.startActivity(packageName)))
        pass

    def inputText(self):
        if AdbUtil.inputBase64Text(self.inputTextLineEdit.text().strip()):
            self.printRes("已经传输完成。")
        pass

    def getPcFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.pcPathLineEdit.setText(fp)
        pass

    def pullFile(self):
        pcPath = self.pcPathLineEdit.text().strip()
        phonePath = self.phonePathLineEdit.text().strip()
        self.printRes("复制设备里的文件到电脑: ")
        self.printCmdRes(*AdbUtil.pullFile(phonePath, pcPath))
        pass

    def pushFile(self):
        pcPath = self.pcPathLineEdit.text().strip()
        phonePath = self.phonePathLineEdit.text().strip()
        self.printRes("复制电脑里的文件到设备: ")
        self.printCmdRes(*AdbUtil.pushFile(pcPath, phonePath))
        pass

    def prepareEvn(self):
        if not self.hasCheckInstallFinish and int(AdbUtil.getVersionCode(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)) < ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION:
            WidgetUtil.showErrorDialog(message="{} 支持的最低版本 {} ，请升级到高版本。".format(
                ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME, ANDROID_TEST_ASSIST_TOOL_LOWEST_VERSION_NAME))
            return
        self.hasCheckInstallFinish = True
        if AdbUtil.sendOperationRequest(AdbUtil.putStringExtra("type", "isEvnReady")) == "false":
            AdbUtil.forceStopApp(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME)
            AdbUtil.startActivity(ANDROID_TEST_ASSIST_TOOL_PACKAGE_NAME, ANDROID_TEST_ASSIST_TOOL_MAIN_ACTIVITY)
            WidgetUtil.showErrorDialog(message='1、请检查权限是否都已开启\n2、点击"立即开启"同意截屏')
            return
        self.printRes("测试环境已经准备完成。")
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
        WidgetUtil.appendTextEdit(self.execResTE, res, color)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidAssistTestDialog(defaultPackageName='com.lkl.androidtestassisttool',
                                     defaultActivityName='.MainActivity')
    window.show()
    sys.exit(app.exec_())
