# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisDialog.py
# 定义一个LogAnalysisDialog类实现log分析相关功能
import threading

from PyQt5.QtCore import pyqtSignal

from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "LogAnalysisDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'LogAnalysis'
KEY_LOG_FILE_PATH = 'logFilePath'
KEY_LOG_FILE_REG = 'logFileReg'
KEY_LOG_START_TIME = 'logStartTime'
KEY_LOG_END_TIME = 'logEndTime'
KEY_LOG_FILE_TIME_INDEX = 'logFileTimeIndex'
KEY_FILE_TIME_FORMAT = 'fileTimeFormat'


class LogAnalysisDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        LogAnalysisDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        LogAnalysisDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.35)
        LogUtil.d(TAG, "Init Log Analysis Dialog")
        self.setObjectName("LogAnalysisDialog")
        self.resize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        # self.setFixedSize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Log分析工具"))

        self.isDebug = isDebug
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.logFilePath = self.operaIni.getValue(KEY_LOG_FILE_PATH, KEY_SECTION)
        self.logFileReg = self.operaIni.getValue(KEY_LOG_FILE_REG, KEY_SECTION)
        self.fileTimeFormat = self.operaIni.getValue(KEY_FILE_TIME_FORMAT, KEY_SECTION)
        self.logFileTimeIndex = self.operaIni.getValue(KEY_LOG_FILE_TIME_INDEX, KEY_SECTION)

        logEndTime = self.operaIni.getValue(KEY_LOG_END_TIME, KEY_SECTION)
        if not logEndTime:
            logEndTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT)
        self.logEndTime = QDateTime.fromString(logEndTime, DATETIME_FORMAT)

        logStartTime = self.operaIni.getValue(KEY_LOG_START_TIME, KEY_SECTION)
        if logStartTime:
            self.logStartTime = QDateTime.fromString(logStartTime, DATETIME_FORMAT)
        else:
            self.logStartTime = self.logEndTime.addDays(-1)

        self.loadingDialog = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        extractLogGroupBox = self.createExtractLogGroupBox(self)

        vLayout.addWidget(extractLogGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        self.hideLoadingSignal.connect(self.hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def hideLoading(self):
        if self.loadingDialog:
            self.loadingDialog.close()
            self.loadingDialog = None
        pass

    def createExtractLogGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="提取日志")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.logFilePath if self.logFilePath else '',
                                                             isEnable=False, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="提取文件格式", minSize=QSize(120, const.HEIGHT))
        self.fileRegPathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.logFileReg if self.logFileReg else '',
                                                             toolTip='输入文件匹配正则表达式',
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="提取Log日期范围", minSize=QSize(120, const.HEIGHT))
        # 指定当前日期时间为控件的日期时间
        self.startDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                               dateTime=self.logStartTime,
                                                               maxDateTime=self.logEndTime,
                                                               displayFormat=DATETIME_FORMAT,
                                                               onDateTimeChanged=self.logStartTimeChanged,
                                                               sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text='-')
        self.endDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                             dateTime=self.logEndTime,
                                                             minDateTime=self.logStartTime,
                                                             displayFormat=DATETIME_FORMAT,
                                                             onDateTimeChanged=self.logEndTimeChanged,
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="日期过滤Log文件规则：", minSize=QSize(120, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="日期起始位置", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeIndexSpinBox = WidgetUtil.createSpinBox(splitter,
                                                                value=int(self.logFileTimeIndex) if self.logFileTimeIndex else 0,
                                                                step=1, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="日期格式", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeFormatLE = WidgetUtil.createLineEdit(splitter,
                                                             text=self.fileTimeFormat if self.fileTimeFormat else '',
                                                             toolTip="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）",
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="提取", onClicked=self.extractLog))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def getLogFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def logStartTimeChanged(self, dateTime: QDateTime):
        self.logStartTime = dateTime
        self.endDateTimeEdit.setMinimumDateTime(dateTime)
        LogUtil.i(TAG, 'logStartTimeChanged', self.logStartTime.toString(DATETIME_FORMAT))
        pass

    def logEndTimeChanged(self, dateTime: QDateTime):
        self.logEndTime = dateTime
        self.startDateTimeEdit.setMaximumDateTime(dateTime)
        LogUtil.i(TAG, 'logEndTimeChanged', self.logEndTime.toString(DATETIME_FORMAT))
        pass

    def extractLog(self):
        self.logFilePath = self.logFilePathLineEdit.text().strip()
        if not self.logFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return
        self.logFileReg = self.fileRegPathLineEdit.text().strip()
        if not self.logFileReg:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件的正则表达式")
            return
        self.fileTimeFormat = self.logFileTimeFormatLE.text().strip()
        if not self.fileTimeFormat:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）")
            return

        self.logFileTimeIndex = self.logFileTimeIndexSpinBox.value()

        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_PATH, self.logFilePath)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_REG, self.logFileReg)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_TIME_INDEX, str(self.logFileTimeIndex))
        self.operaIni.addItem(KEY_SECTION, KEY_FILE_TIME_FORMAT, self.fileTimeFormat)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_START_TIME, self.logStartTime.toString(DATETIME_FORMAT))
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_END_TIME, self.logEndTime.toString(DATETIME_FORMAT))
        self.operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def execExtractLog(self):
        LogUtil.d(TAG, 'execExtractLog start.')
        srcFiles = FileUtil.findFilePathList(self.logFilePath, [self.logFileReg], ['.*/tmp/.*', '.*/tmp1/.*'])
        LogUtil.d(TAG, 'execExtractLog find files: ', srcFiles)
        for zipFile in srcFiles:
            FileUtil.unzipFile(zipFile, os.path.join(self.logFilePath, './tmp'))
        self.hideLoadingSignal.emit()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
