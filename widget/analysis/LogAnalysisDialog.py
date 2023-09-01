# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogAnalysisDialog.py
# 定义一个LogAnalysisDialog类实现log分析相关功能
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *

TAG = "LogAnalysisDialog"


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
                                                             text='/Users/likunlun/PycharmProjects/CommonTools/widget/analysis/test',
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
        self.startDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter, sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text='-')
        self.endDateTimeEdit = WidgetUtil.createDateTimeEdit(splitter, sizePolicy=sizePolicy)
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

    def extractLog(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LogAnalysisDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())

