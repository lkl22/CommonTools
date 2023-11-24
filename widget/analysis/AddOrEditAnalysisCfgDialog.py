# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditAnalysisCfgDialog.py
# 定义一个AddOrEditAnalysisCfgDialog类实现添加、编辑log分析规则配置的功能
import copy
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.analysis.AddOrEditResultMapDialog import AddOrEditResultMapDialog
from widget.analysis.LogAnalysisManager import *
from widget.analysis.SpliceLogParamsWidget import SpliceLogParamsWidget
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonTableView import CommonTableView

TAG = "AddOrEditAnalysisCfgDialog"
HEADERS = {
    KEY_SRC_LOG: {KEY_TITLE: "Log原始文字"}, KEY_MAP_TXT: {KEY_TITLE: "映射文字"},
    KEY_IS_ENABLE: {KEY_TITLE: "Enable", KEY_DATETIME: DEFAULT_VALUE_IS_ENABLE},
    KEY_IS_FUNCTION: {KEY_TITLE: "执行函数", KEY_DEFAULT: DEFAULT_VALUE_IS_FUNCTION}
}


class AddOrEditAnalysisCfgDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, ruleList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.__initWidgetConfig()

        self.__ruleList = ruleList if ruleList else []
        self.__callback = callback
        self.__isAdd = default is None
        self.__default = default
        isEnable = DictUtil.get(self.__default, KEY_IS_ENABLE, DEFAULT_VALUE_IS_ENABLE)
        needCostTime = DictUtil.get(self.__default, KEY_NEED_COST_TIME, DEFAULT_VALUE_NEED_COST_TIME)
        needSpliceLog = DictUtil.get(self.__default, KEY_NEED_SPLICE_LOG, DEFAULT_VALUE_NEED_SPLICE_LOG)
        needLogMap = DictUtil.get(self.__default, KEY_NEED_LOG_MAP, DEFAULT_VALUE_NEED_LOG_MAP)
        self.__logMapRules = copy.deepcopy(DictUtil.get(self.__default, KEY_RESULT_MAP, []))
        self.__logSpliceParams = DictUtil.get(self.__default, KEY_SPLICE_PARAMS, {})

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelMinSize = QSize(90, const.HEIGHT)
        self.__nameLineEdit = CommonLineEdit(label='Name', text=DictUtil.get(default, KEY_NAME),
                                             labelMinSize=labelMinSize, toolTip="规则名称")
        vLayout.addWidget(self.__nameLineEdit)

        self.__descLineEdit = CommonLineEdit(label='Description', text=DictUtil.get(default, KEY_DESC),
                                             labelMinSize=labelMinSize, toolTip="规则描述")
        vLayout.addWidget(self.__descLineEdit)

        self.__logKeywordLineEdit = CommonLineEdit(label='日志关键字', text=DictUtil.get(default, KEY_LOG_KEYWORD),
                                                   labelMinSize=labelMinSize, toolTip="日志关键字，用于从日志中筛选指定Log")
        vLayout.addWidget(self.__logKeywordLineEdit)

        self.__costTimeCheckBox = WidgetUtil.createCheckBox(self, text="统计耗时",
                                                            toolTip="默认不统计耗时，只打印日志",
                                                            isChecked=needCostTime,
                                                            clicked=self.__costTimeCheckChange)
        vLayout.addWidget(self.__costTimeCheckBox)
        self.__costTimeBox = WidgetUtil.createHBoxLayout()
        vLayout.addLayout(self.__costTimeBox)
        self.__startLogKeywordLineEdit = CommonLineEdit(label='起始时间的日志关键字',
                                                        text=DictUtil.get(default, KEY_START_LOG_KEYWORD),
                                                        labelMinSize=labelMinSize, toolTip="起始时间日志关键字，用于从日志中筛选指定Log",
                                                        isEnable=needCostTime)
        self.__costTimeBox.addWidget(self.__startLogKeywordLineEdit)

        self.__endLogKeywordLineEdit = CommonLineEdit(label='结束时间的日志关键字',
                                                      text=DictUtil.get(default, KEY_END_LOG_KEYWORD),
                                                      labelMinSize=labelMinSize, toolTip="结束时间日志关键字，用于从日志中筛选指定Log",
                                                      isEnable=needCostTime)
        self.__costTimeBox.addWidget(self.__endLogKeywordLineEdit)

        self.__spliceLogCheckBox = WidgetUtil.createCheckBox(self, text="查找处理日志",
                                                             isChecked=needSpliceLog,
                                                             clicked=self.__spliceLogCheckChange)
        vLayout.addWidget(self.__spliceLogCheckBox)
        self.__spliceLogParamsWidget = SpliceLogParamsWidget(value=self.__logSpliceParams, isEnable=needSpliceLog,
                                                             toolTip="处理分行打印日志，通过起始关键字查找日志，可以根据关键拆分正则表达式决策是否继续拼接，或者根据结束关键字结束log拼接，拼接后结果可以按指定函数执行输出结果")
        vLayout.addWidget(self.__spliceLogParamsWidget)

        self.__logMapTableView = CommonTableView(addBtnTxt="添加Log映射配置", headers=HEADERS,
                                                 items=self.__logMapRules,
                                                 addOrEditItemFunc=self.__addOrEditItemFunc)
        vLayout.addWidget(self.__logMapTableView, 1)

        hBox = WidgetUtil.createHBoxLayout(spacing=30)
        self.__enableCheckBox = WidgetUtil.createCheckBox(self, text="Enable",
                                                          toolTip="默认Enable，规则生效",
                                                          isChecked=isEnable)
        hBox.addWidget(self.__enableCheckBox)
        self.__logMapCheckBox = WidgetUtil.createCheckBox(self, text="结果映射",
                                                          toolTip="默认不对日志结果做映射",
                                                          isChecked=needLogMap)
        hBox.addWidget(self.__logMapCheckBox)
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
        AddOrEditAnalysisCfgDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Analysis Cfg Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Log分析规则配置"))
        self.setObjectName("AddOrEditAnalysisCfgDialog")
        self.resize(AddOrEditAnalysisCfgDialog.WINDOW_WIDTH, AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditAnalysisCfgDialog.WINDOW_WIDTH, AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT)
        self.setWindowModality(Qt.WindowModal)
        pass

    def __costTimeCheckChange(self):
        isCheck = self.__costTimeCheckBox.isChecked()
        self.__startLogKeywordLineEdit.setEnabled(isCheck)
        self.__endLogKeywordLineEdit.setEnabled(isCheck)
        pass

    def __spliceLogCheckChange(self):
        isCheck = self.__spliceLogCheckBox.isChecked()
        self.__spliceLogParamsWidget.setEnabled(isCheck)
        pass

    def __addOrEditItemFunc(self, callback, default, items):
        AddOrEditResultMapDialog(callback=callback, default=default, ruleList=items)

    def __acceptFunc(self):
        name = self.__nameLineEdit.getData()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入规则名")
            return

        if self.__isAdd or self.__default[KEY_NAME] != name:
            for item in self.__ruleList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的规则名，{name}已经存在了，不能重复添加")
                    return

        isChecked = self.__costTimeCheckBox.isChecked()

        logKeyword = self.__logKeywordLineEdit.getData()
        startLogKeyword = DictUtil.get(self.__default, KEY_START_LOG_KEYWORD, '')
        endLogKeyword = DictUtil.get(self.__default, KEY_END_LOG_KEYWORD, '')
        if isChecked:
            startLogKeyword = self.__startLogKeywordLineEdit.getData()
            if not startLogKeyword:
                WidgetUtil.showErrorDialog(message="请输入过滤开始时间的关键字")
                return
            endLogKeyword = self.__endLogKeywordLineEdit.getData()
            if not endLogKeyword:
                WidgetUtil.showErrorDialog(message="请输入过滤结束时间的关键字")
                return

        desc = self.__descLineEdit.getData()

        if not self.__default:
            self.__default = {}
        self.__default[KEY_NAME] = name
        self.__default[KEY_DESC] = desc
        self.__default[KEY_LOG_KEYWORD] = logKeyword
        self.__default[KEY_IS_ENABLE] = self.__enableCheckBox.isChecked()

        self.__default[KEY_NEED_COST_TIME] = isChecked
        self.__default[KEY_START_LOG_KEYWORD] = startLogKeyword
        self.__default[KEY_END_LOG_KEYWORD] = endLogKeyword

        self.__default[KEY_NEED_SPLICE_LOG] = self.__spliceLogCheckBox.isChecked()
        self.__default[KEY_SPLICE_PARAMS] = self.__spliceLogParamsWidget.getData()

        self.__default[KEY_NEED_LOG_MAP] = self.__logMapCheckBox.isChecked()
        self.__default[KEY_RESULT_MAP] = self.__logMapTableView.getData()

        self.__callback(self.__default if self.__isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditAnalysisCfgDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window = AddOrEditAnalysisCfgDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                        default={'name': 'dd', 'desc': 'ddd', 'needCostTime': False},
                                        ruleList=[{'name': 'ddd', 'desc': 'ddd', 'needCostTime': False}],
                                        isDebug=True)
    window.show()
    sys.exit(app.exec_())
