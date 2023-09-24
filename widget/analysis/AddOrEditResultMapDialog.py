# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditResultMapDialog.py
# 定义一个AddOrEditResultMapDialog类实现添加、编辑结果映射配置的功能

from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.analysis.LogAnalysisManager import *
from widget.custom.CommonLineEdit import CommonLineEdit

TAG = "AddOrEditResultMapDialog"


class AddOrEditResultMapDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, ruleList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.__initWidgetConfig()

        self.__ruleList = ruleList if ruleList else []
        self.__callback = callback
        self.__isAdd = default is None
        self.__default = default
        isEnable = DictUtil.get(self.__default, KEY_IS_ENABLE, DEFAULT_VALUE_IS_ENABLE)
        isFunc = DictUtil.get(self.__default, KEY_IS_FUNCTION, DEFAULT_VALUE_IS_FUNCTION)

        self.setObjectName("AddOrEditResultMapDialog")
        self.resize(AddOrEditResultMapDialog.WINDOW_WIDTH, AddOrEditResultMapDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditResultMapDialog.WINDOW_WIDTH, AddOrEditResultMapDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelMinSize = QSize(90, const.HEIGHT)
        self.__srcLogLineEdit = CommonLineEdit(label='原始文字', text=DictUtil.get(default, KEY_SRC_LOG),
                                               labelMinSize=labelMinSize, toolTip="Log中的原始输出")
        vLayout.addWidget(self.__srcLogLineEdit)

        self.__mapTxtLineEdit = CommonLineEdit(label='映射结果', text=DictUtil.get(default, KEY_MAP_TXT),
                                               labelMinSize=labelMinSize,
                                               toolTip="替换后的结果，默认普通文本，勾选Function当作函数脚本执行，输入参数为text，输出参数为res")
        vLayout.addWidget(self.__mapTxtLineEdit)

        hBox = WidgetUtil.createHBoxLayout(spacing=30)
        self.__enableCheckBox = WidgetUtil.createCheckBox(self, text="Enable",
                                                          toolTip="默认Enable，规则生效",
                                                          isChecked=isEnable)
        hBox.addWidget(self.__enableCheckBox)
        self.__funcCheckBox = WidgetUtil.createCheckBox(self, text="Function",
                                                        toolTip="默认普通文本，勾选当作函数脚本执行",
                                                        isChecked=isFunc)
        hBox.addWidget(self.__funcCheckBox)
        hBox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hBox)

        # vLayout.addWidget(WidgetUtil.createLabel(self), 1)
        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.__acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def __initWidgetConfig(self):
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditResultMapDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditResultMapDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Result Map Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Log结果映射规则配置"))
        self.setWindowModality(Qt.WindowModal)
        pass

    def __acceptFunc(self):
        srcLog = self.__srcLogLineEdit.getData()
        if not srcLog:
            WidgetUtil.showErrorDialog(message="请输入Log原始文字")
            return

        if self.__isAdd or self.__default[KEY_SRC_LOG] != srcLog:
            for item in self.__ruleList:
                if srcLog == item[KEY_SRC_LOG]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的Log原始文字，{srcLog}已经存在了，不能重复添加")
                    return

        mapTxt = self.__mapTxtLineEdit.getData()
        if not mapTxt:
            WidgetUtil.showErrorDialog(message="请输入映射结果文字")
            return

        if not self.__default:
            self.__default = {}
        self.__default[KEY_SRC_LOG] = srcLog
        self.__default[KEY_MAP_TXT] = mapTxt
        self.__default[KEY_IS_ENABLE] = self.__enableCheckBox.isChecked()
        self.__default[KEY_IS_FUNCTION] = self.__funcCheckBox.isChecked()

        self.__callback(self.__default if self.__isAdd else None)
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
