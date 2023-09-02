# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisWindow.py
# 定义一个LogAnalysisWindow类实现log分析相关功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QAbstractItemView, QMainWindow

from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.analysis.CategoryManagerWidget import CategoryManagerWidget
from widget.analysis.LogAnalysisManager import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "LogAnalysisWindow"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'LogAnalysis'
KEY_LOG_FILE_PATH = 'logFilePath'


class LogAnalysisWindow(QMainWindow):
    windowList = []
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QMainWindow.__init__(self)
        # self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        LogAnalysisWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        LogAnalysisWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init Log Analysis Window")
        self.setObjectName("LogAnalysisWindow")
        self.resize(LogAnalysisWindow.WINDOW_WIDTH, LogAnalysisWindow.WINDOW_HEIGHT)
        # self.setFixedSize(LogAnalysisWindow.WINDOW_WIDTH, LogAnalysisWindow.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Log分析工具"))

        self.isDebug = isDebug
        self.analysisManager = LogAnalysisManager(isDebug)
        self.loadingDialog = None

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)
        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(10, 10, 10, 10), spacing=10)
        layoutWidget.setLayout(hLayout)

        self.categoryManagerWidget = CategoryManagerWidget(analysisManager=self.analysisManager,
                                                           modifyCallback=self.categoryModify)

        self.categoryManageGroupBox = self.createCategoryManageGroupBox()
        hLayout.addWidget(self.categoryManageGroupBox, 3)

        self.consoleTextEdit = WidgetUtil.createTextEdit(self, isReadOnly=True)
        hLayout.addWidget(self.consoleTextEdit, 2)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        self.hideLoadingSignal.connect(self.hideLoading)

        # 重写关闭事件，回到第一界面

    def closeEvent(self, event):
        if self.isDebug:
            return
        from widget.MainWidget import MainWidget
        window = MainWidget()
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        window.show()
        event.accept()
        pass

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass

    def createCategoryManageGroupBox(self):
        box = WidgetUtil.createGroupBox(self, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(0, 0, 0, 0), spacing=5)
        vbox.addWidget(self.categoryManagerWidget)
        # logAnalysisGroupBox = self.createLogAnalysisGroupBox(self)
        # vbox.addLayout(logAnalysisGroupBox, 7)
        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.execBtn = WidgetUtil.createPushButton(box, text="开始执行", onClicked=self.extractLog)
        hbox.addWidget(self.execBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def createLogAnalysisGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="日志分析")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="提取Log文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.extractLogFile)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='',
                                                             isEnable=False, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        self.dynParamsTableView = WidgetUtil.createTableView(self, doubleClicked=self.dynParamsTableDoubleClicked)
        # 设为不可编辑
        self.dynParamsTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.dynParamsTableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.dynParamsTableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.dynParamsTableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.dynParamsTableView.customContextMenuRequested.connect(self.dynParamsCustomRightMenu)
        self.updateDynParamsTableView()
        # self.vLayout.addWidget(self.dynParamsTableView, 1)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def categoryModify(self):
        LogUtil.d(TAG, "categoryModify")

        pass

    def extractLogFile(self):
        from ExtractLogDialog import ExtractLogDialog
        ExtractLogDialog(self.isDebug)
        pass

    def getLogFilePath(self):
        fp = ''
        if self.logFilePath:
            fp, _ = os.path.split(self.logFilePath)

        fp = WidgetUtil.getOpenFileName(caption='请选择要分析的Log文件',
                                        directory=fp)
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def addDynParam(self):
        LogUtil.d(TAG, "addDynParam")
        # AddOrEditDynamicParamDialog(callback=self.addOrEditDynParamCallback,
        #                             dynParamList=self.dynArgs,
        #                             optionGroups=self.optionGroups)
        pass

    def addOrEditDynParamCallback(self, info):
        LogUtil.d(TAG, "addOrEditDynParamCallback", info)
        if info:
            self.dynArgs.append(info)
        self.updateDynParamsTableView()
        pass

    def dynParamsTableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "dynParamsTableDoubleClicked：row ", row, ' col', index.column(), ' data ', oldValue)
        # AddOrEditDynamicParamDialog(callback=self.addOrEditDynParamCallback,
        #                             default=self.dynArgs[row],
        #                             dynParamList=self.dynArgs,
        #                             optionGroups=self.optionGroups)
        pass

    def dynParamsCustomRightMenu(self, pos):
        self.curDynParamRow = self.dynParamsTableView.currentIndex().row()
        LogUtil.i(TAG, "dynParamsCustomRightMenu", pos, ' row: ', self.curDynParamRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delDynParam)
        menu.exec(self.dynParamsTableView.mapToGlobal(pos))
        pass

    def delDynParam(self):
        dynParamName = self.dynArgs[self.curDynParamRow][KEY_NAME]
        LogUtil.i(TAG, f"delDynParam {dynParamName}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{dynParamName}</span> 吗？",
                                      acceptFunc=self.delDynParamTableItem)
        pass

    def delDynParamTableItem(self):
        LogUtil.i(TAG, "delDynParamTableItem")
        self.dynArgs.remove(self.dynArgs[self.curDynParamRow])
        self.updateDynParamsTableView()
        pass

    def updateDynParamsTableView(self):
        tableData = []
        # for dynParam in self.dynArgs:
        #     tableData.append({
        #         KEY_NAME: dynParam[KEY_NAME],
        #         KEY_DESC: DictUtil.get(dynParam, KEY_DESC, ""),
        #         KEY_OPTION_GROUP: dynParam[KEY_OPTION_GROUP],
        #         KEY_OPTION: dynParam[KEY_OPTION],
        #         KEY_NEED_CAPITALIZE: DictUtil.get(dynParam, KEY_NEED_CAPITALIZE, DEFAULT_VALUE_NEED_CAPITALIZE)
        #     })
        # WidgetUtil.addTableViewData(self.dynParamsTableView, tableData,
        #                             headerLabels=["动态参数名称", "动态参数描述", "选项所属群组", "选项", "需要首字母大写"])
        # WidgetUtil.tableViewSetColumnWidth(self.cmdTableView, 0, 100)
        pass

    def extractLog(self):
        self.logFilePath = self.logFilePathLineEdit.text().strip()
        if not self.logFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def execExtractLog(self):
        LogUtil.d(TAG, 'execExtractLog start.')

        self.hideLoadingSignal.emit()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisWindow(isDebug=True)
    window.show()
    sys.exit(app.exec_())
