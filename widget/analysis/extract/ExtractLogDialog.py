# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExtractLogDialog.py
# 定义一个ExtractLogDialog类实现从log文件提取指定条件的log到另一个log文件的功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from constant.WidgetConst import *
from util.DateUtil import DateUtil
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.LoadingDialog import LoadingDialog

TAG = "ExtractLogDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'ExtractLog'
KEY_SRC_LOG_FILE_PATH = 'srcLogFilePath'
KEY_DST_LOG_FILE_PATH = 'dstLogFilePath'
KEY_LOG_START_TIME = 'logStartTime'
KEY_LOG_END_TIME = 'logEndTime'
KEY_LOG_TIME_INDEX = 'logTimeIndex'
KEY_LOG_TIME_FORMAT = 'logTimeFormat'


class ExtractLogDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        ExtractLogDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        ExtractLogDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Extract Log Dialog")
        self.setObjectName("ExtractLogDialog")
        self.resize(ExtractLogDialog.WINDOW_WIDTH, ExtractLogDialog.WINDOW_HEIGHT)
        # self.setFixedSize(ExtractLogDialog.WINDOW_WIDTH, ExtractLogDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="提取Log日志到指定文件工具"))

        self.isDebug = isDebug
        self.operaIni = OperaIni()
        self.srcLogFilePath = self.operaIni.getValue(KEY_SRC_LOG_FILE_PATH, KEY_SECTION)
        self.dstLogFilePath = self.operaIni.getValue(KEY_DST_LOG_FILE_PATH, KEY_SECTION)
        self.logTimeIndex = self.operaIni.getValue(KEY_LOG_TIME_INDEX, KEY_SECTION)
        self.logTimeFormat = self.operaIni.getValue(KEY_LOG_TIME_FORMAT, KEY_SECTION)
        self.validTimeFormat = None
        self.dstFp = None

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
        WidgetUtil.createPushButton(splitter, text="源日志文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFile)
        self.srcLogFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                                text=self.srcLogFilePath if self.srcLogFilePath else '',
                                                                isEnable=False, sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text="目标目录", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getDstFilePath)
        self.dstLogFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                                text=self.dstLogFilePath if self.dstLogFilePath else '',
                                                                toolTip='需要存放到的目录',
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
        WidgetUtil.createLabel(splitter, text="Log文件中日期格式规则：", minSize=QSize(120, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="日期起始位置", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeIndexSpinBox = WidgetUtil.createSpinBox(splitter,
                                                                value=int(
                                                                    self.logTimeIndex) if self.logTimeIndex else 0,
                                                                step=1, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="日期格式", minSize=QSize(60, const.HEIGHT))
        self.logFileTimeFormatLE = WidgetUtil.createLineEdit(splitter,
                                                             text=self.logTimeFormat if self.logTimeFormat else '',
                                                             toolTip="请输入匹配Log文件里的日期格式（例如：yyyy-MM-dd HH:mm:ss）",
                                                             sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="提取", onClicked=self.extractLog))
        self.openDstFileBtn = WidgetUtil.createPushButton(box, text="打开目标文件", isEnable=False, onClicked=self.__openDstLog)
        hbox.addWidget(self.openDstFileBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        self.resultLabel = WidgetUtil.createLabel(box)
        vbox.addWidget(self.resultLabel)
        return box

    def getSrcFile(self):
        parentDir = './'
        if self.srcLogFilePath:
            parentDir, _ = os.path.split(self.srcLogFilePath)
        fp = WidgetUtil.getOpenFileName(caption='请选择Log文件', directory=parentDir)
        if fp:
            self.srcLogFilePathLineEdit.setText(fp)
        pass

    def getDstFilePath(self):
        fp = WidgetUtil.getExistingDirectory(caption='请选择Log文件所在路径',
                                             directory=self.dstLogFilePath if self.dstLogFilePath else './')
        if fp:
            self.dstLogFilePathLineEdit.setText(fp)
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
        self.srcLogFilePath = self.srcLogFilePathLineEdit.text().strip()
        if not self.srcLogFilePath:
            WidgetUtil.showErrorDialog(message="请选择需要提取的源日志文件")
            return
        self.dstLogFilePath = self.dstLogFilePathLineEdit.text().strip()
        if not self.dstLogFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件需要存放的目录")
            return
        while self.dstLogFilePath.endswith("/") or self.dstLogFilePath.endswith("\\"):
            self.dstLogFilePath = self.dstLogFilePath[:len(self.dstLogFilePath) - 1]
        LogUtil.d(TAG, "目标目录：", self.dstLogFilePath)
        self.logTimeFormat = self.logFileTimeFormatLE.text().strip()
        if not self.logTimeFormat:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件里的日期格式（例如：yyyy-MM-dd HH:mm:ss）")
            return

        self.logTimeIndex = self.logFileTimeIndexSpinBox.value()

        self.operaIni.addItem(KEY_SECTION, KEY_SRC_LOG_FILE_PATH, self.srcLogFilePath)
        self.operaIni.addItem(KEY_SECTION, KEY_DST_LOG_FILE_PATH, self.dstLogFilePath)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_TIME_INDEX, str(self.logTimeIndex))
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_TIME_FORMAT, self.logTimeFormat)
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_START_TIME, self.logStartTime.toString(DATETIME_FORMAT))
        self.operaIni.addItem(KEY_SECTION, KEY_LOG_END_TIME, self.logEndTime.toString(DATETIME_FORMAT))
        self.operaIni.saveIni()

        self.validTimeFormat = self.logTimeFormat.replace('yyyy', '%Y').replace('MM', '%m').replace('dd', '%d').replace(
            'HH', '%H').replace('mm', '%M').replace('ss', '%S')

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=()).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog()
        pass

    def execExtractLog(self):
        LogUtil.d(TAG, 'execExtractLog start.')
        self.dstFp = os.path.join(self.dstLogFilePath, self.logStartTime.toString('yyyyMMddHHmmss'))
        FileUtil.mkFilePath(self.dstFp)
        FileUtil.removeFile(self.dstFp)

        startTime = QDateTime.fromString(self.logStartTime.toString(self.logTimeFormat), self.logTimeFormat)
        endTime = QDateTime.fromString(self.logEndTime.toString(self.logTimeFormat), self.logTimeFormat)
        srcFile = open(self.srcLogFilePath, 'r')
        dstFile = open(self.dstFp, 'w')
        line = srcFile.readline()
        while line:
            datetime = self.__getDatetime(line)
            if datetime:
                if datetime >= startTime:
                    dstFile.write(line)
                if datetime > endTime:
                    break
            else:
                dstFile.write(line)
            try:
                line = srcFile.readline()
            except Exception as ex:
                dstFile.write(line)
                LogUtil.e("invalid line：{} \nex: {}".format(line, ex))

        srcFile.close()
        dstFile.close()

        self.resultLabel.setText(f"处理完成，目标文件：{self.dstFp}")
        self.openDstFileBtn.setEnabled(True)
        self.hideLoadingSignal.emit()
        pass

    def __getDatetime(self, line):
        try:
            timeStr = line[self.logTimeIndex: self.logTimeIndex + len(self.logTimeFormat)]
            if DateUtil.isValidDate(timeStr, self.validTimeFormat):
                return QDateTime.fromString(timeStr, self.logTimeFormat)
        except Exception as err:
            LogUtil.e(TAG, '__getDatetime 错误信息：', err)
        return None

    def __openDstLog(self):
        if self.dstFp:
            FileUtil.openFile(self.dstFp)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExtractLogDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
