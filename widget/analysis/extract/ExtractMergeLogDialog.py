# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExtractMergeLogDialog.py
# 定义一个ExtractMergeLogDialog类实现从log目录提取合并指定日期范围的log到一个log文件的功能
import os.path
import threading
from PyQt5.QtCore import pyqtSignal
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
    __hideLoadingSignal = pyqtSignal(bool, str)

    def __init__(self, callback=None, isDebug=False):
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

        self.__isDebug = isDebug
        self.__callback = callback
        self.__operaIni = OperaIni()
        self.__extractLogFP = self.__operaIni.getValue(KEY_EXTRACT_LOG_FILE_PATH, KEY_SECTION)
        self.__extractLogFileReg = self.__operaIni.getValue(KEY_EXTRACT_LOG_FILE_REG, KEY_SECTION)
        self.__extractFileTimeFormat = self.__operaIni.getValue(KEY_EXTRACT_FILE_TIME_FORMAT, KEY_SECTION)
        self.__extractLogFileTimeIndex = self.__operaIni.getValue(KEY_EXTRACT_LOG_FILE_TIME_INDEX, KEY_SECTION)

        logEndTime = self.__operaIni.getValue(KEY_EXTRACT_LOG_END_TIME, KEY_SECTION)
        if not logEndTime:
            logEndTime = QDateTime.currentDateTime().toString(DATETIME_FORMAT)
        self.__extractLogEndTime = QDateTime.fromString(logEndTime, DATETIME_FORMAT)

        logStartTime = self.__operaIni.getValue(KEY_EXTRACT_LOG_START_TIME, KEY_SECTION)
        if logStartTime:
            self.__extractLogStartTime = QDateTime.fromString(logStartTime, DATETIME_FORMAT)
        else:
            self.__extractLogStartTime = self.__extractLogEndTime.addDays(-1)

        self.__loadingDialog = None

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        extractLogGroupBox = self.__createExtractLogGroupBox(self)

        vLayout.addWidget(extractLogGroupBox)

        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=lambda: self.__extractLog(True),
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)

        self.setWindowModality(Qt.ApplicationModal)
        self.__hideLoadingSignal.connect(self.__hideLoading)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __hideLoading(self, isClosed, fp):
        if self.__loadingDialog:
            self.__loadingDialog.close()
            self.__loadingDialog = None
        LogUtil.i(TAG, 'hideLoading', fp)
        if self.__callback:
            self.__callback(fp)
        if isClosed:
            self.close()
        elif fp:
            dirPath, _ = os.path.split(fp)
            FileUtil.openFile(dirPath)
        pass

    def __createExtractLogGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="筛选合并日志")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createPushButton(splitter, text="日志文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.__getLogFilePath)
        self.logFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.__extractLogFP if self.__extractLogFP else '',
                                                             isEnable=False, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="提取文件格式", minSize=QSize(120, const.HEIGHT))
        self.fileRegPathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                             text=self.__extractLogFileReg if self.__extractLogFileReg else '',
                                                             toolTip='输入文件匹配正则表达式',
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="提取Log日期范围", minSize=QSize(120, const.HEIGHT))
        # 指定当前日期时间为控件的日期时间
        self.startDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                               dateTime=self.__extractLogStartTime,
                                                               maxDateTime=self.__extractLogEndTime,
                                                               displayFormat=DATETIME_FORMAT,
                                                               onDateTimeChanged=self.__logStartTimeChanged,
                                                               sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text='-')
        self.endDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter,
                                                             dateTime=self.__extractLogEndTime,
                                                             minDateTime=self.__extractLogStartTime,
                                                             displayFormat=DATETIME_FORMAT,
                                                             onDateTimeChanged=self.__logEndTimeChanged,
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(box)
        WidgetUtil.createLabel(splitter, text="Log文件中日期格式规则：", minSize=QSize(120, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="日期起始位置", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeIndexSpinBox = WidgetUtil.createSpinBox(splitter,
                                                                value=int(
                                                                    self.__extractLogFileTimeIndex) if self.__extractLogFileTimeIndex else 0,
                                                                step=1, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="日期格式", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeFormatLE = WidgetUtil.createLineEdit(splitter,
                                                             text=self.__extractFileTimeFormat if self.__extractFileTimeFormat else '',
                                                             toolTip="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）",
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="筛选合并", onClicked=self.__extractLog))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addWidget(WidgetUtil.createLabel(box), 1)
        return box

    def __getLogFilePath(self):
        fp = WidgetUtil.getExistingDirectory(caption='请选择Log文件所在路径',
                                             directory=self.__extractLogFP if self.__extractLogFP else './')
        if fp:
            self.logFilePathLineEdit.setText(fp)
        pass

    def __logStartTimeChanged(self, dateTime: QDateTime):
        self.__extractLogStartTime = dateTime
        self.endDateTimeEdit.setMinimumDateTime(dateTime)
        LogUtil.i(TAG, 'logStartTimeChanged', self.__extractLogStartTime.toString(DATETIME_FORMAT))
        pass

    def __logEndTimeChanged(self, dateTime: QDateTime):
        self.__extractLogEndTime = dateTime
        self.startDateTimeEdit.setMaximumDateTime(dateTime)
        LogUtil.i(TAG, 'logEndTimeChanged', self.__extractLogEndTime.toString(DATETIME_FORMAT))
        pass

    def __extractLog(self, isClosed=False):
        self.__extractLogFP = self.logFilePathLineEdit.text().strip()
        if not self.__extractLogFP:
            WidgetUtil.showErrorDialog(message="请选择日志文件所在目录")
            return
        self.__extractLogFileReg = self.fileRegPathLineEdit.text().strip()
        if not self.__extractLogFileReg:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件的正则表达式")
            return
        self.__extractFileTimeFormat = self.logFileTimeFormatLE.text().strip()
        if not self.__extractFileTimeFormat:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）")
            return

        self.__extractLogFileTimeIndex = self.logFileTimeIndexSpinBox.value()

        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_PATH, self.__extractLogFP)
        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_REG, self.__extractLogFileReg)
        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_FILE_TIME_INDEX, str(self.__extractLogFileTimeIndex))
        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_FILE_TIME_FORMAT, self.__extractFileTimeFormat)
        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_START_TIME,
                                self.__extractLogStartTime.toString(DATETIME_FORMAT))
        self.__operaIni.addItem(KEY_SECTION, KEY_EXTRACT_LOG_END_TIME,
                                self.__extractLogEndTime.toString(DATETIME_FORMAT))
        self.__operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.__execExtractLog, args=(isClosed,)).start()
        if not self.__loadingDialog:
            self.__loadingDialog = LoadingDialog()
        pass

    def __execExtractLog(self, isClosed):
        LogUtil.d(TAG, 'execExtractLog start.', isClosed)
        srcFiles = FileUtil.findFilePathList(self.__extractLogFP, [self.__extractLogFileReg],
                                             ['.*/tmp/.*', '.*/tmp1/.*'])
        LogUtil.d(TAG, 'execExtractLog find files: ', srcFiles)
        tmpDir = os.path.join(self.__extractLogFP, 'tmp')
        tmp1Dir = os.path.join(self.__extractLogFP, 'tmp1')
        FileUtil.clearPath(tmpDir)
        FileUtil.clearPath(tmp1Dir)
        for zipFile in srcFiles:
            if self.__isValidFile(zipFile):
                FileUtil.unzipFile(zipFile, tmpDir)
        files = []
        for dirpath, dirnames, filenames in os.walk(tmpDir):
            for filename in sorted(filenames):
                files.append(os.path.join(dirpath, filename))
        LogUtil.d(TAG, 'execExtractLog unzip files: ', files)
        dstFp = ''
        if len(files) > 0:
            _, fn = os.path.split(files[0])
            dstFp = os.path.join(tmp1Dir, fn)
            FileUtil.mergeFiles(files, dstFp)
        self.__hideLoadingSignal.emit(isClosed, dstFp)
        pass

    def __isValidFile(self, fp):
        LogUtil.d(TAG, 'isValidFile', fp)
        _, fn = os.path.split(fp)
        try:
            time = fn[
                   self.__extractLogFileTimeIndex: self.__extractLogFileTimeIndex + len(self.__extractFileTimeFormat)]
            fileTime = QDateTime.fromString(time, self.__extractFileTimeFormat)
            return self.__extractLogStartTime <= fileTime <= self.__extractLogEndTime
        except Exception as err:
            LogUtil.e(TAG, 'isValidFile 错误信息：', err)
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExtractMergeLogDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
