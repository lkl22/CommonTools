# -*- coding: utf-8 -*-
# python 3.x
# Filename: ExtractMergeLogDialog.py
# 定义一个ExtractMergeLogDialog类实现从log目录提取合并指定日期范围的log到一个log文件的功能
import copy
import os.path
import threading
from PyQt5.QtCore import pyqtSignal

from util.DateUtil import DateUtil
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from widget.custom.CommonComboBox import CommonComboBox
from widget.custom.CommonDateTimeFormatEdit import CommonDateTimeFormatEdit
from widget.custom.CommonDateTimeRangeEdit import CommonDateTimeRangeEdit
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.DragInputWidget import DragInputWidget
from widget.custom.LoadingDialog import LoadingDialog

TAG = "ExtractMergeLogDialog"

KEY_SECTION = 'ExtractMergeLog'


class ExtractMergeLogDialog(QtWidgets.QDialog):
    __hideLoadingSignal = pyqtSignal(bool, str)

    def __init__(self, callback=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        ExtractMergeLogDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        ExtractMergeLogDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init Extract Merge Log Dialog")
        self.setObjectName("ExtractMergeLogDialog")
        self.resize(ExtractMergeLogDialog.WINDOW_WIDTH, ExtractMergeLogDialog.WINDOW_HEIGHT)
        # self.setFixedSize(ExtractMergeLogDialog.WINDOW_WIDTH, ExtractMergeLogDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="筛选指定日期范围Log工具"))

        self.__isDebug = isDebug
        self.__callback = callback
        self.__operaIni = OperaIni()
        self.__configs = JsonUtil.decode(self.__operaIni.getValue(KEY_CONFIGS, KEY_SECTION), {})
        self.__list = DictUtil.get(self.__configs, KEY_LIST, [])
        self.__defaultConfig = ListUtil.get(self.__list, KEY_NAME, DictUtil.get(self.__configs, KEY_DEFAULT),
                                            KEY_CONFIG, {})

        self.__initData()
        self.__datetimeIndex = None
        self.__datetimeFormat = None
        self.__startDatetime = None
        self.__endDatetime = None

        self.__loadingDialog = None

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        labelMinSize = QSize(120, const.HEIGHT)
        self.__configComboBox = CommonComboBox(label='选择规则', default=DictUtil.get(self.__configs, KEY_DEFAULT),
                                               groupList=[item[KEY_NAME] for item in self.__list],
                                               isEditable=True, maxWidth=int(WidgetUtil.getScreenWidth() * 0.5),
                                               dataChanged=self.__configChanged)
        vbox.addWidget(self.__configComboBox)

        self.__logDirPathWidget = DragInputWidget(label='日志文件路径',
                                                  text=self.__extractLogFP,
                                                  dirParam={KEY_CAPTION: '日志文件所在路径'},
                                                  labelMinSize=labelMinSize,
                                                  textChanged=self.__logDirChanged,
                                                  toolTip='日志文件所在路径')
        vbox.addWidget(self.__logDirPathWidget)

        self.__logFileRegEdit = CommonLineEdit(label='提取文件名格式', text=self.__extractLogFileReg,
                                               labelMinSize=labelMinSize,
                                               toolTip='输入文件名匹配正则表达式')
        vbox.addWidget(self.__logFileRegEdit)

        self.__dateTimeRangeEdit = CommonDateTimeRangeEdit(label='提取Log日期范围', value=self.__datetimeRange,
                                                           maxOffsetValue=900,
                                                           labelMinSize=labelMinSize,
                                                           datetimeFormat=DictUtil.get(self.__datetimeFormatRule,
                                                                                       KEY_DATETIME_FORMAT))
        vbox.addWidget(self.__dateTimeRangeEdit)

        self.__datetimeFormatEdit = CommonDateTimeFormatEdit(label='文本日期格式规则', value=self.__datetimeFormatRule,
                                                             labelMinSize=labelMinSize,
                                                             editingFinished=self.__datetimeFormatChanged)
        vbox.addWidget(self.__datetimeFormatEdit)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(self, text="筛选合并", onClicked=self.__extractLog))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=lambda: self.__extractLog(True),
                                                  rejectedFunc=lambda: self.close())
        vbox.addWidget(btnBox)

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

    def __configChanged(self, config, deleteData):
        LogUtil.d(TAG, '__configChanged cur data', config, 'delete data', deleteData)
        if deleteData:
            ListUtil.remove(self.__list, ListUtil.find(self.__list, KEY_NAME, deleteData))
        defaultConfig = ListUtil.get(self.__list, KEY_NAME, config, KEY_CONFIG, {})
        if not defaultConfig and not deleteData:
            # 添加新的配置，不清之前的cfg，复用
            self.__defaultConfig = copy.deepcopy(self.__defaultConfig)
            self.__list.append({KEY_NAME: config, KEY_CONFIG: self.__defaultConfig})
            self.__configs = {KEY_DEFAULT: config, KEY_LIST: self.__list}
            self.__saveConfig()
            return
        self.__defaultConfig = defaultConfig
        self.__configs = {KEY_DEFAULT: config, KEY_LIST: self.__list}
        self.__updateUi()
        self.__saveConfig()
        pass

    def __initData(self):
        self.__extractLogFP = DictUtil.get(self.__defaultConfig, KEY_FILE_PATH)
        self.__extractLogFileReg = DictUtil.get(self.__defaultConfig, KEY_REG)
        self.__datetimeRange = DictUtil.get(self.__defaultConfig, KEY_DATETIME_RANGE)
        self.__datetimeFormatRule = DictUtil.get(self.__defaultConfig, KEY_DATETIME_FORMAT_RULE)
        pass

    def __updateUi(self):
        self.__initData()
        self.__logDirPathWidget.updateData(self.__extractLogFP)
        self.__logFileRegEdit.updateData(self.__extractLogFileReg)

        self.__dateTimeRangeEdit.updateData(self.__datetimeRange)
        self.__dateTimeRangeEdit.updateDatetimeFormat(DictUtil.get(self.__datetimeFormatRule, KEY_DATETIME_FORMAT))
        self.__datetimeFormatEdit.updateData(self.__datetimeFormatRule)
        pass

    def __datetimeFormatChanged(self):
        self.__dateTimeRangeEdit.updateDatetimeFormat(
            DictUtil.get(self.__datetimeFormatEdit.getData(), KEY_DATETIME_FORMAT))
        pass

    def __logDirChanged(self, logDir):
        LogUtil.d(TAG, '__logDirChanged', logDir)
        self.__extractLogFileReg = self.__logFileRegEdit.getData()
        self.__datetimeFormatRule = self.__datetimeFormatEdit.getData()
        if not self.__extractLogFileReg or not self.__datetimeFormatRule or not logDir:
            return
        srcFiles = FileUtil.findFilePathList(logDir, [self.__extractLogFileReg],
                                             ['.*/tmp/.*', '.*/tmp1/.*'])
        LogUtil.d(TAG, '__logDirChanged find files: ', srcFiles)
        datetimeIndex = self.__datetimeFormatRule[KEY_START_INDEX]
        datetimeFormat = self.__datetimeFormatRule[KEY_DATETIME_FORMAT]
        times = []
        for srcFile in srcFiles:
            _, fn = os.path.split(srcFile)
            time = fn[datetimeIndex: datetimeIndex + len(datetimeFormat)]
            if DateUtil.isValidDate(time, datetimeFormat, True):
                times.append(time)
        if not times:
            LogUtil.d(TAG, '__logDirChanged have not valid file.')
            return
        lastTime = sorted(times)[-1]
        LogUtil.d(TAG, '__logDirChanged last file: ', lastTime)
        self.__dateTimeRangeEdit.updateData(
            DictUtil.join([self.__dateTimeRangeEdit.getData(), {KEY_DATETIME: lastTime}]))
        pass

    def __saveConfig(self):
        if not self.__configs:
            WidgetUtil.showErrorDialog(message="请选择或输入规则名称")
            return False
        self.__extractLogFP = self.__logDirPathWidget.getData()
        if not self.__extractLogFP or not FileUtil.existsDir(self.__extractLogFP):
            WidgetUtil.showErrorDialog(message="请选择有效的日志文件所在目录（目录可能不存在了）")
            return False
        self.__extractLogFileReg = self.__logFileRegEdit.getData()
        if not self.__extractLogFileReg:
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件的正则表达式")
            return False
        self.__datetimeFormatRule = self.__datetimeFormatEdit.getData()
        if not DictUtil.get(self.__datetimeFormatRule, KEY_DATETIME_FORMAT):
            WidgetUtil.showErrorDialog(message="请输入匹配Log文件名里的日期格式（例如：yyyyMMdd_HHmmss）")
            return False
        self.__datetimeRange = self.__dateTimeRangeEdit.getData()

        self.__defaultConfig[KEY_FILE_PATH] = self.__extractLogFP
        self.__defaultConfig[KEY_REG] = self.__extractLogFileReg
        self.__defaultConfig[KEY_DATETIME_FORMAT_RULE] = self.__datetimeFormatRule
        self.__defaultConfig[KEY_DATETIME_RANGE] = self.__datetimeRange
        self.__operaIni.addItem(KEY_SECTION, KEY_CONFIGS,
                                JsonUtil.encode(self.__configs, ensureAscii=False))
        self.__operaIni.saveIni()
        return True

    def __extractLog(self, isClosed=False):
        if not self.__saveConfig():
            LogUtil.d(TAG, 'sava config failed.')
            return

        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=self.__execExtractLog, args=(isClosed,)).start()
        if not self.__loadingDialog:
            self.__loadingDialog = LoadingDialog()
        pass

    def __execExtractLog(self, isClosed):
        LogUtil.d(TAG, 'execExtractLog start.', isClosed)
        self.__datetimeIndex = self.__datetimeFormatRule[KEY_START_INDEX]
        self.__datetimeFormat = self.__datetimeFormatRule[KEY_DATETIME_FORMAT]

        srcFiles = FileUtil.findFilePathList(self.__extractLogFP, [self.__extractLogFileReg],
                                             ['.*/tmp/.*', '.*/tmp1/.*'])
        LogUtil.d(TAG, 'execExtractLog find files: ', srcFiles)
        tmpDir = os.path.join(self.__extractLogFP, 'tmp')
        tmp1Dir = os.path.join(self.__extractLogFP, 'tmp1')
        FileUtil.removeDir(tmpDir)
        FileUtil.removeDir(tmp1Dir)

        startTime, endTime = self.__dateTimeRangeEdit.getDateRange()
        # 时间范围转为文件名中相同格式
        self.__startDatetime = QDateTime.fromString(startTime.toString(self.__datetimeFormat), self.__datetimeFormat)
        self.__endDatetime = QDateTime.fromString(endTime.toString(self.__datetimeFormat), self.__datetimeFormat)

        for srcFile in srcFiles:
            if self.__isValidFile(srcFile):
                _, ext = os.path.splitext(srcFile)
                if FileUtil.isZipFile(srcFile):
                    FileUtil.unzipFile(srcFile, tmpDir)
                else:
                    _, fn = os.path.split(srcFile)
                    FileUtil.modifyFilePath(srcFile, os.path.join(tmpDir, fn))
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
            time = fn[self.__datetimeIndex: self.__datetimeIndex + len(self.__datetimeFormat)]
            fileTime = QDateTime.fromString(time, self.__datetimeFormat)
            return self.__startDatetime <= fileTime <= self.__endDatetime
        except Exception as err:
            LogUtil.e(TAG, 'isValidFile 错误信息：', err)
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ExtractMergeLogDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
