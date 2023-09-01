# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisDialog.py
# 定义一个LogAnalysisDialog类实现log分析相关功能
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *

TAG = "LogAnalysisDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'LogAnalysis'
KEY_LOG_FILE_PATH = 'logFilePath'
KEY_LOG_FILE_REG = 'logFileReg'
KEY_LOG_START_TIME = 'logStartTime'
KEY_LOG_END_TIME = 'logEndTime'


class LogAnalysisDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 350
    WINDOW_HEIGHT = 180

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        LogAnalysisDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        LogAnalysisDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Log Analysis Dialog")
        self.setObjectName("LogAnalysisDialog")
        self.resize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        # self.setFixedSize(LogAnalysisDialog.WINDOW_WIDTH, LogAnalysisDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Log分析工具"))

        self.isDebug = isDebug
        self.operaIni = OperaIni("../../resources/config/BaseConfig.ini" if isDebug else '')
        self.logFilePath = self.operaIni.getValue(KEY_LOG_FILE_PATH, KEY_SECTION)
        self.logFileReg = self.operaIni.getValue(KEY_LOG_FILE_REG, KEY_SECTION)

        logEndTime = self.operaIni.getValue(KEY_LOG_END_TIME, KEY_SECTION)
        if not logEndTime:
            logEndTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT)
        self.logEndTime = QDateTime.fromString(logEndTime, DATETIME_FORMAT)

        logStartTime = self.operaIni.getValue(KEY_LOG_START_TIME, KEY_SECTION)
        if logStartTime:
            self.logStartTime = QDateTime.fromString(logStartTime, DATETIME_FORMAT)
        else:
            self.logStartTime = self.logEndTime.addDays(-1)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        extractLogGroupBox = self.createExtractLogGroupBox(self)

        vLayout.addWidget(extractLogGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # self.hideLoadingSignal.connect(self.hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

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
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="提取文件格式", minSize=QSize(120, const.HEIGHT))
        self.fileRegPathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text='.*log\.zip$',
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
        LogUtil.i('logStartTimeChanged', self.logStartTime.toString(DATETIME_FORMAT))
        pass

    def logEndTimeChanged(self, dateTime: QDateTime):
        self.logEndTime = dateTime
        self.startDateTimeEdit.setMaximumDateTime(dateTime)
        LogUtil.i('logEndTimeChanged', self.logEndTime.toString(DATETIME_FORMAT))
        pass

    def extractLog(self):
        logFileDirPath = self.logFilePathLineEdit.text().strip()
        if not logFileDirPath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return
        fileReg = self.fileRegPathLineEdit.text().strip()
        if not fileReg:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件的正则表达式")
            return
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_PATH, logFileDirPath)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_FILE_REG, fileReg)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_START_TIME, self.logStartTime.toString(DATETIME_FORMAT))
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_END_TIME, self.logEndTime.toString(DATETIME_FORMAT))
        self.operaIni.saveIni()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
