# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExtractMergeLogDialog.py
# 定义一个ExtractMergeLogDialog类实现从log目录提取合并指定日期范围的log到一个log文件的功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "ExtractMergeLogDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'ExtractMergeLog'
KEY_EXTRACT_LOG_FILE_PATH = 'extractLogFilePath'
KEY_EXTRACT_LOG_FILE_REG = 'extractLogFileReg'
KEY_EXTRACT_LOG_START_TIME = 'extractLogStartTime'
KEY_EXTRACT_LOG_END_TIME = 'extractLogEndTime'
KEY_EXTRACT_LOG_FILE_TIME_INDEX = 'extractFileTimeIndex'
KEY_EXTRACT_FILE_TIME_FORMAT = 'extractFileTimeFormat'


class ExtractMergeLogDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        ExtractMergeLogDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        ExtractMergeLogDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Extract Merge Log Dialog")
        self.setObjectName("ExtractMergeLogDialog")
        self.resize(ExtractMergeLogDialog.WINDOW_WIDTH, ExtractMergeLogDialog.WINDOW_HEIGHT)
        # self.setFixedSize(ExtractMergeLogDialog.WINDOW_WIDTH, ExtractMergeLogDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="筛选指定日期范围Log工具"))

        self.isDebug = isDebug
        self.operaIni = OperaIni()
        self.extractLogFilePath = self.operaIni.getValue(KEY_EXTRACT_LOG_FILE_PATH, KEY_SECTION)
        self.extractLogFileReg = self.operaIni.getValue(KEY_EXTRACT_LOG_FILE_REG, KEY_SECTION)
        self.extractFileTimeFormat = self.operaIni.getValue(KEY_EXTRACT_FILE_TIME_FORMAT, KEY_SECTION)
        self.extractLogFileTimeIndex = self.operaIni.getValue(KEY_EXTRACT_LOG_FILE_TIME_INDEX, KEY_SECTION)

        logEndTime = self.operaIni.getValue(KEY_EXTRACT_LOG_END_TIME, KEY_SECTION)
        if not logEndTime:
            logEndTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT)
        self.extractLogEndTime = QDateTime.fromString(logEndTime, DATETIME_FORMAT)

        logStartTime = self.operaIni.getValue(KEY_EXTRACT_LOG_START_TIME, KEY_SECTION)
        if logStartTime:
            self.extractLogStartTime = QDateTime.fromString(logStartTime, DATETIME_FORMAT)
        else:
            self.extractLogStartTime = self.extractLogEndTime.addDays(-1)

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
                                                             text=self.extractLogFilePath if self.extractLogFilePath else '',
                                                             isEnable=False, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="提取文件格式", minSize=QSize(120, const.HEIGHT))
        self.fileRegPathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.extractLogFileReg if self.extractLogFileReg else '',
                                                             toolTip='输入文件匹配正则表达式',
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="提取Log日期范围", minSize=QSize(120, const.HEIGHT))
        # 指定当前日期时间为控件的日期时间
        self.startDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                               dateTime=self.extractLogStartTime,
                                                               maxDateTime=self.extractLogEndTime,
                                                               displayFormat=DATETIME_FORMAT,
                                                               onDateTimeChanged=self.logStartTimeChanged,
                                                               sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text='-')
        self.endDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                             dateTime=self.extractLogEndTime,
                                                             minDateTime=self.extractLogStartTime,
                                                             displayFormat=DATETIME_FORMAT,
                                                             onDateTimeChanged=self.logEndTimeChanged,
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="Log文件中日期格式规则：", minSize=QSize(120, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="日期起始位置", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeIndexSpinBox = WidgetUtil.createSpinBox(splitter,
                                                                value=int(
                                                                    self.extractLogFileTimeIndex) if self.extractLogFileTimeIndex else 0,
                                                                step=1, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="日期格式", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeFormatLE = WidgetUtil.createLineEdit(splitter,
                                                             text=self.extractFileTimeFormat if self.extractFileTimeFormat else '',
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
        fp = WidgetUtil.getExistingDirectory(caption='请选择Log文件所在路径',
                                             directory=self.extractLogFilePath if self.extractLogFilePath else './')
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def logStartTimeChanged(self, dateTime: QDateTime):
        self.extractLogStartTime = dateTime
        self.endDateTimeEdit.setMinimumDateTime(dateTime)
        LogUtil.i(TAG, 'logStartTimeChanged', self.extractLogStartTime.toString(DATETIME_FORMAT))
        pass

    def logEndTimeChanged(self, dateTime: QDateTime):
        self.extractLogEndTime = dateTime
        self.startDateTimeEdit.setMaximumDateTime(dateTime)
        LogUtil.i(TAG, 'logEndTimeChanged', self.extractLogEndTime.toString(DATETIME_FORMAT))
        pass

    def extractLog(self):
        self.extractLogFilePath = self.logFilePathLineEdit.text().strip()
        if not self.extractLogFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return
        self.extractLogFileReg = self.fileRegPathLineEdit.text().strip()
        if not self.extractLogFileReg:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件的正则表达式")
            return
        self.extractFileTimeFormat = self.logFileTimeFormatLE.text().strip()
        if not self.extractFileTimeFormat:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）")
            return

        self.extractLogFileTimeIndex = self.logFileTimeIndexSpinBox.value()

        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_PATH, self.extractLogFilePath)
        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_REG, self.extractLogFileReg)
        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_TIME_INDEX, str(self.extractLogFileTimeIndex))
        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_FILE_TIME_FORMAT, self.extractFileTimeFormat)
        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_START_TIME,
                              self.extractLogStartTime.toString(DATETIME_FORMAT))
        self.operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_END_TIME, self.extractLogEndTime.toString(DATETIME_FORMAT))
        self.operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog(isDebug=self.isDebug)
        pass

    def execExtractLog(self):
        LogUtil.d(TAG, 'execExtractLog start.')
        srcFiles = FileUtil.findFilePathList(self.extractLogFilePath, [self.extractLogFileReg],
                                             ['.*/tmp/.*', '.*/tmp1/.*'])
        LogUtil.d(TAG, 'execExtractLog find files: ', srcFiles)
        tmpDir = os.path.join(self.extractLogFilePath, 'tmp')
        tmp1Dir = os.path.join(self.extractLogFilePath, 'tmp1')
        FileUtil.clearPath(tmpDir)
        FileUtil.clearPath(tmp1Dir)
        for zipFile in srcFiles:
            if self.isValidFile(zipFile):
                FileUtil.unzipFile(zipFile, tmpDir)
        files = []
        for dirpath, dirnames, filenames in os.walk(tmpDir):
            for filename in sorted(filenames):
                files.append(os.path.join(dirpath, filename))
        LogUtil.d(TAG, 'execExtractLog unzip files: ', files)
        if len(files) > 0:
            _, fn = os.path.split(files[0])
            dstFp = os.path.join(tmp1Dir, fn)
            FileUtil.mergeFiles(files, dstFp)
        self.hideLoadingSignal.emit()
        pass

    def isValidFile(self, fp):
        LogUtil.d(TAG, 'isValidFile', fp)
        _, fn = os.path.split(fp)
        try:
            time = fn[self.extractLogFileTimeIndex: self.extractLogFileTimeIndex + len(self.extractFileTimeFormat)]
            fileTime = QDateTime.fromString(time, self.extractFileTimeFormat)
            return self.extractLogStartTime <= fileTime <= self.extractLogEndTime
        except Exception as err:
            LogUtil.e(TAG, 'isValidFile 错误信息：', err)
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExtractMergeLogDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
