# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditResultMapDialog.py
# 定义一个AddOrEditResultMapDialog类实现添加、编辑结果映射配置的功能

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.analysis.LogAnalysisManager import *

TAG = "AddOrEditResultMapDialog"


class AddOrEditResultMapDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, ruleList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditResultMapDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditResultMapDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Result Map Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Log结果映射规则配置"))
        if ruleList is None:
            ruleList = []
        self.ruleList = ruleList
        self.callback = callback
        self.isAdd = default is None
        self.default = default
        isEnable = DictUtil.get(self.default, KEY_IS_ENABLE, DEFAULT_VALUE_IS_ENABLE)

        self.setObjectName("AddOrEditResultMapDialog")
        self.resize(AddOrEditResultMapDialog.WINDOW_WIDTH, AddOrEditResultMapDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditResultMapDialog.WINDOW_WIDTH, AddOrEditResultMapDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 90

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="原始文字：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.srcLogLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_SRC_LOG),
                                                        toolTip="Log中的原始输出")
        hBox.addWidget(self.srcLogLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="映射结果：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.mapTxtLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_MAP_TXT),
                                                        toolTip="替换后的结果")
        hBox.addWidget(self.mapTxtLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=30)
        self.enableCheckBox = WidgetUtil.createCheckBox(self, text="Enable",
                                                        toolTip="默认Enable，规则生效",
                                                        isChecked=isEnable)
        hBox.addWidget(self.enableCheckBox)
        hBox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hBox)

        # vLayout.addWidget(WidgetUtil.createLabel(self), 1)
        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        srcLog = self.srcLogLineEdit.text().strip()
        if not srcLog:
            WidgetUtil.showErrorDialog(message="请输入Log原始文字")
            return

        if self.isAdd or self.default[KEY_SRC_LOG] != srcLog:
            for item in self.ruleList:
                if srcLog == item[KEY_SRC_LOG]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的Log原始文字，{srcLog}已经存在了，不能重复添加")
                    return

        mapTxt = self.mapTxtLineEdit.text().strip()
        if not mapTxt:
            WidgetUtil.showErrorDialog(message="请输入映射结果文字")
            return

        if not self.default:
            self.default = {}
        self.default[KEY_SRC_LOG] = srcLog
        self.default[KEY_MAP_TXT] = mapTxt
        self.default[KEY_IS_ENABLE] = self.enableCheckBox.isChecked()

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditResultMapDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    # window = AddOrEditResultMapDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
    #                                     default={'name': 'dd', 'desc': 'ddd', 'needCostTime': False},
    #                                     cfgList=[{'name': 'ddd', 'desc': 'ddd', 'needCostTime': False}],
    #                                     isDebug=True)
    window.show()
    sys.exit(app.exec_())
