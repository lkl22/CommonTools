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


class AndroidAssistTestDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    TABLE_KEY_TYPE = '操作类型'
    TABLE_KEY_DESC = '操作描述信息'

    def __init__(self, defaultPackageName="", defaultActivityName=""):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android Assist Test Dialog")
        self.setObjectName("AndroidAssistTestDialog")
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
        self.exec_()

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

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="是否安装", onClicked=self.isInstalled)
        WidgetUtil.createPushButton(splitter, text="获取apk版本信息", onClicked=self.getVersionInfo)

        yPos += 185
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

    def printRes(self, res: str = '', color='#00f'):
        WidgetUtil.appendTextEdit(self.execResTE, res, color)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidAssistTestDialog(defaultPackageName='com.lkl.androidtestassisttool',
                                     defaultActivityName='.MainActivity')
    window.show()
    sys.exit(app.exec_())
