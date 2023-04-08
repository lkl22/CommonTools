# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditConfigDialog.py
# 定义一个AddOrEditConfigDialog类实现添加/编辑查找配置
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.OperaIni import *
from util.PlatformUtil import PlatformUtil
from util.ReUtil import ReUtil
from widget.findFileContent.AddOrEditMatchDialog import AddOrEditMatchDialog
from widget.findFileContent.FindFileContentManager import *

TAG = "AddOrEditConfigDialog"


class AddOrEditConfigDialog(QtWidgets.QDialog):
    def __init__(self, default=None, configList=None, callback=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditConfigDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AddOrEditConfigDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "AddOrEditConfigDialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑配置信息"))

        self.callback = callback
        self.configList = configList if configList else []
        self.default = default if default else {}
        self.isAdd = default is None
        self.isDebug = isDebug

        self.matchList = DictUtil.get(self.default, KEY_LIST, [])

        self.setObjectName("AddOrEditConfigDialog")
        self.resize(AddOrEditConfigDialog.WINDOW_WIDTH, AddOrEditConfigDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddOrEditConfigDialog.WINDOW_WIDTH, AddOrEditConfigDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入配置名：", minSize=QSize(120, 20)))
        self.nameLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_NAME),
                                                      holderText="配置名（只能包含字母数字及下划线）")
        hbox.addWidget(self.nameLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="请输入配置描述：", minSize=QSize(120, 20)))
        self.descLineEdit = WidgetUtil.createLineEdit(self, text=DictUtil.get(default, KEY_DESC),
                                                      holderText="配置描述，用于说明该配置的作用")
        hbox.addWidget(self.descLineEdit)
        vLayout.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(self, text="添加匹配规则", onClicked=self.addMatch))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vLayout.addLayout(hbox)

        self.tableView = WidgetUtil.createTableView(self, doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.customRightMenu)
        vLayout.addWidget(self.tableView, 1)

        self.updateTableView()

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def updateTableView(self):
        tableData = []
        for match in self.matchList:
            tableData.append({
                KEY_NAME: DictUtil.get(match, KEY_NAME, ""),
                KEY_DESC: DictUtil.get(match, KEY_DESC, ""),
                KEY_PATTERN: DictUtil.get(match, KEY_PATTERN, ""),
                KEY_IS_REG: DictUtil.get(match, KEY_IS_REG, DEFAULT_VALUE_IS_REG)
            })
        WidgetUtil.addTableViewData(self.tableView, tableData,
                                    headerLabels=["匹配规则名", "匹配规则名描述", "匹配规则", "正则规则"])
        # WidgetUtil.tableViewSetColumnWidth(self.cmdTableView, 0, 100)
        pass

    def addMatch(self):
        LogUtil.d(TAG, "addMatch")
        AddOrEditMatchDialog(matchList=self.matchList, callback=self.addOrEditMatchCallback,
                             isDebug=self.isDebug).show()
        pass

    def addOrEditMatchCallback(self, info):
        LogUtil.i(TAG, "addOrEditMatchCallback", info)
        if info:
            self.matchList.append(info)
        self.updateTableView()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)

        matchInfo = self.matchList[row]
        AddOrEditMatchDialog(default=matchInfo, matchList=self.matchList, callback=self.addOrEditMatchCallback,
                             isDebug=self.isDebug).show()
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.tableView.currentIndex().row()
        LogUtil.i(TAG, "customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delMatch)
        menu.exec(self.tableView.mapToGlobal(pos))
        pass

    def delMatch(self):
        name = self.matchList[self.curDelRow][KEY_NAME]
        LogUtil.i(TAG, f"delMatch {name}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{name}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i(TAG, "delTableItem")
        self.matchList.remove(self.matchList[self.curDelRow])
        self.updateTableView()
        pass

    def acceptFunc(self):
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入配置名")
            return
        desc = self.descLineEdit.text().strip()
        if not desc:
            WidgetUtil.showErrorDialog(message="请输入配置描述")
            return
        if not ReUtil.match(name, "\\w*"):
            WidgetUtil.showErrorDialog(message="请输入正确的配置名（只能包含字母数字及下划线）")
            return
        for item in self.configList:
            if name == item[KEY_NAME]:
                WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的配置，{name}已经存在了，可以下拉选择")
                return
            if desc == item[KEY_DESC]:
                WidgetUtil.showErrorDialog(message=f"请设置一个其他的描述，{desc}已经存在了，相同的描述会产生混淆")
                return
        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_LIST] = self.matchList
        if self.callback:
            self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditConfigDialog(configList=[], callback=lambda it: LogUtil.d(TAG, it), isDebug=True)
    window = AddOrEditConfigDialog(default={'name': '111', 'desc': '2233', 'list': [{'name': '11', 'desc': '222', 'pattern': '333', 'isReg': False}]},
                                   configList=[], callback=lambda it: LogUtil.d(TAG, it), isDebug=True)
    window.show()
    sys.exit(app.exec_())
