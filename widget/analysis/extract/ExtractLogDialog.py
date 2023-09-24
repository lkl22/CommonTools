# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExtractLogDialog.py
# 定义一个ExtractLogDialog类实现从log文件提取指定条件的log到另一个log文件的功能
import os.path
import threading

from PyQt5.QtCore import pyqtSignal
from util.DateUtil import DateUtil
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.custom.CommonDateTimeFormatEdit import CommonDateTimeFormatEdit
from widget.custom.CommonDateTimeRangeEdit import CommonDateTimeRangeEdit
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.LoadingDialog import LoadingDialog

TAG = "ExtractLogDialog"

DATETIME_FORMAT = 'yyyy-MM-dd HH:mm:ss'

KEY_SECTION = 'ExtractLog'
KEY_SRC_LOG_FILE_PATH = 'srcLogFilePath'
KEY_DST_LOG_FILE_PATH = 'dstLogFilePath'
KEY_LOG_TIME_RANGE = 'datetimeRange'
KEY_LOG_TIME_FORMAT_RULE = 'datetimeFormatRule'


class ExtractLogDialog(QtWidgets.QDialog):
    hideLoadingSignal = pyqtSignal()

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        ExtractLogDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        ExtractLogDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Extract Log Dialog")
        self.setObjectName("ExtractLogDialog")
        self.resize(ExtractLogDialog.WINDOW_WIDTH, ExtractLogDialog.WINDOW_HEIGHT)
        # self.setFixedSize(ExtractLogDialog.WINDOW_WIDTH, ExtractLogDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="提取Log日志到指定文件工具"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__srcLogFilePath = self.__operaIni.getValue(KEY_SRC_LOG_FILE_PATH, KEY_SECTION)
        self.__dstLogFilePath = self.__operaIni.getValue(KEY_DST_LOG_FILE_PATH, KEY_SECTION)
        self.__logDatetimeRange = JsonUtil.decode(self.__operaIni.getValue(KEY_LOG_TIME_RANGE, KEY_SECTION))
        self.__logDatetimeFormatRule = JsonUtil.decode(self.__operaIni.getValue(KEY_LOG_TIME_FORMAT_RULE, KEY_SECTION))
        self.__validTimeFormat = None
        self.__logTimeIndex = None
        self.__logTimeFormat = None
        self.__dstFp = None

        self.loadingDialog = None

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        labelMinSize = QSize(120, const.HEIGHT)
        self.__srcFilePathWidget = DragInputWidget(label='源日志文件',
                                                   text=self.__srcLogFilePath,
                                                   fileParam={KEY_CAPTION: '源日志文件'},
                                                   labelMinSize=labelMinSize,
                                                   toolTip='选择源日志文件')
        vbox.addWidget(self.__srcFilePathWidget)

        self.__dstDirPathWidget = DragInputWidget(label='目标目录',
                                                  text=self.__dstLogFilePath,
                                                  dirParam={KEY_CAPTION: '需要存放到的目录'},
                                                  labelMinSize=labelMinSize,
                                                  toolTip='需要存放到的目录')
        vbox.addWidget(self.__dstDirPathWidget)

        self.__dateTimeRangeEdit = CommonDateTimeRangeEdit(label='提取Log日期范围', value=self.__logDatetimeRange,
                                                           labelMinSize=labelMinSize)
        vbox.addWidget(self.__dateTimeRangeEdit)

        self.__datetimeFormatEdit = CommonDateTimeFormatEdit(label='文本日期格式规则', value=self.__logDatetimeFormatRule,
                                                             labelMinSize=labelMinSize)
        vbox.addWidget(self.__datetimeFormatEdit)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(self, text="提取", onClicked=self.extractLog))
        self.openDstFileBtn = WidgetUtil.createPushButton(self, text="打开目标文件", isEnable=False,
                                                          onClicked=self.__openDstLog)
        hbox.addWidget(self.openDstFileBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        self.resultLabel = WidgetUtil.createLabel(self)
        vbox.addWidget(self.resultLabel)

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

    def extractLog(self):
        self.__srcLogFilePath = self.__srcFilePathWidget.getData()
        if not self.__srcLogFilePath:
            WidgetUtil.showErrorDialog(message="请选择需要提取的源日志文件")
            return
        self.__dstLogFilePath = self.__dstDirPathWidget.getData()
        if not self.__dstLogFilePath:
            WidgetUtil.showErrorDialog(message="请选择日志文件需要存放的目录")
            return
        while self.__dstLogFilePath.endswith("/") or self.__dstLogFilePath.endswith("\\"):
            self.__dstLogFilePath = self.__dstLogFilePath[:len(self.__dstLogFilePath) - 1]
        LogUtil.d(TAG, "目标目录：", self.__dstLogFilePath)
        self.__logDatetimeFormatRule = self.__datetimeFormatEdit.getData()
        if not DictUtil.get(self.__logDatetimeFormatRule, KEY_DATETIME_FORMAT):
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件里的日期格式（例如：yyyy-MM-dd HH:mm:ss）")
            return
        self.__logDatetimeRange = self.__dateTimeRangeEdit.getData()

        self.__operaIni.addItem(KEY_SECTION, KEY_SRC_LOG_FILE_PATH, self.__srcLogFilePath)
        self.__operaIni.addItem(KEY_SECTION, KEY_DST_LOG_FILE_PATH, self.__dstLogFilePath)
        self.__operaIni.addItem(KEY_SECTION, KEY_LOG_TIME_RANGE,
                                JsonUtil.encode(self.__logDatetimeRange, ensureAscii=False))
        self.__operaIni.addItem(KEY_SECTION, KEY_LOG_TIME_FORMAT_RULE,
                                JsonUtil.encode(self.__logDatetimeFormatRule, ensureAscii=False))
        self.__operaIni.saveIni()

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.execExtractLog, args=(self.__srcLogFilePath,
                                                           self.__dstLogFilePath,
                                                           self.__logDatetimeRange,
                                                           self.__logDatetimeFormatRule)).start()
        if not self.loadingDialog:
            self.loadingDialog = LoadingDialog()
        pass

    def execExtractLog(self, srcFp, dstFp, datetimeRange, datetimeFormat):
        LogUtil.d(TAG, 'execExtractLog start.', srcFp, dstFp, datetimeRange, datetimeFormat)
        self.__logTimeIndex = datetimeFormat[KEY_START_INDEX]
        self.__logTimeFormat = datetimeFormat[KEY_DATETIME_FORMAT]
        self.__validTimeFormat = self.__logTimeFormat.replace('yyyy', '%Y').replace('MM', '%m'). \
            replace('dd', '%d').replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')

        startTime, endTime = self.__dateTimeRangeEdit.getDateRange()
        self.__dstFp = os.path.join(dstFp, startTime.toString('yyyyMMddHHmmss'))
        FileUtil.mkFilePath(self.__dstFp)
        FileUtil.removeFile(self.__dstFp)

        # 时间范围转为文本中相同格式的
        startTime = QDateTime.fromString(startTime.toString(self.__logTimeFormat), self.__logTimeFormat)
        endTime = QDateTime.fromString(endTime.toString(self.__logTimeFormat), self.__logTimeFormat)

        srcFile = open(self.__srcLogFilePath, 'r')
        dstFile = open(self.__dstFp, 'w')
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

        self.resultLabel.setText(f"处理完成，目标文件：{self.__dstFp}")
        self.openDstFileBtn.setEnabled(True)
        self.hideLoadingSignal.emit()
        pass

    def __getDatetime(self, line):
        try:
            timeStr = line[self.__logTimeIndex: self.__logTimeIndex + len(self.__logTimeFormat)]
            if DateUtil.isValidDate(timeStr, self.__validTimeFormat):
                return QDateTime.fromString(timeStr, self.__logTimeFormat)
        except Exception as err:
            LogUtil.e(TAG, '__getDatetime 错误信息：', err)
        return None

    def __openDstLog(self):
        if self.__dstFp:
            FileUtil.openFile(self.__dstFp)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExtractLogDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
