# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditAnalysisCfgDialog.py
# 定义一个AddOrEditAnalysisCfgDialog类实现添加、编辑log分析规则配置的功能
import copy

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from widget.analysis.LogAnalysisManager import *

TAG = "AddOrEditAnalysisCfgDialog"


class AddOrEditAnalysisCfgDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, ruleList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditAnalysisCfgDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.2)
        LogUtil.d(TAG, "Add or Edit Analysis Cfg Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Log分析规则配置"))
        if ruleList is None:
            ruleList = []
        self.ruleList = ruleList
        self.callback = callback
        self.isAdd = default is None
        self.default = default

        self.setObjectName("AddOrEditAnalysisCfgDialog")
        self.resize(AddOrEditAnalysisCfgDialog.WINDOW_WIDTH, AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AddOrEditAnalysisCfgDialog.WINDOW_WIDTH, AddOrEditAnalysisCfgDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 90

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="Name：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      toolTip="规则名称")
        hBox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text="Description：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      toolTip="规则描述")
        hBox.addWidget(self.descLineEdit)
        vLayout.addLayout(hBox)

        hBox = WidgetUtil.createHBoxLayout(spacing=10)
        self.costTimeCheckBox = WidgetUtil.createCheckBox(self, text="统计耗时",
                                                          toolTip="默认不统计耗时，只打印日志",
                                                          isChecked=DictUtil.get(self.default, KEY_NEED_COST_TIME,
                                                                                 DEFAULT_VALUE_NEED_COST_TIME))
        hBox.addWidget(self.costTimeCheckBox)
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
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入规则名")
            return

        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.ruleList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的规则名，{name}已经存在了，不能重复添加")
                    return

        desc = self.descLineEdit.text().strip()

        if not self.default:
            self.default = {}
        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_NEED_COST_TIME] = self.costTimeCheckBox.isChecked()
        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AddOrEditAnalysisCfgDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    # window = AddOrEditAnalysisCfgDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
    #                                     default={'name': 'dd', 'desc': 'ddd', 'needCostTime': False},
    #                                     cfgList=[{'name': 'ddd', 'desc': 'ddd', 'needCostTime': False}],
    #                                     isDebug=True)
    window.show()
    sys.exit(app.exec_())