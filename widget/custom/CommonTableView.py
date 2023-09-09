# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonTableView.py
# 定义一个CommonTableView窗口类实现通用tableView的功能
import sys
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QFrame, QAbstractItemView

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.WidgetUtil import *

TAG = 'CommonTableView'


class CommonTableView(QFrame):
    def __init__(self, addBtnTxt: str, headers: {}, items: list[dict], addOrEditItemFunc,
                 toolTip=None):
        super(CommonTableView, self).__init__()
        self.__headers = headers
        self.__items = items
        self.__addOrEditItemFunc = addOrEditItemFunc

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=5)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__addItemBtn = WidgetUtil.createPushButton(self, text=addBtnTxt, onClicked=self.__addItem)
        hbox.addWidget(self.__addItemBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.__tableView = WidgetUtil.createTableView(self, doubleClicked=self.__tableDoubleClicked)
        # 设为不可编辑
        self.__tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.__tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.__tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.__tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__tableView.customContextMenuRequested.connect(self.__customRightMenuRequested)
        self.__updateTableView()
        vbox.addWidget(self.__tableView, 1)

        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)

        vbox.setContentsMargins(0, 0, 0, 0)
        pass

    def __addItem(self):
        LogUtil.d(TAG, "__addItem")

        self.__addOrEditItemFunc(callback=self.__addOrEditItemCallback,
                                 items=self.__items)
        pass

    def __addOrEditItemCallback(self, info):
        LogUtil.d(TAG, "__addOrEditItemCallback", info)
        if info:
            self.__items.append(info)
        self.__updateTableView()
        pass

    def __tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "__tableDoubleClicked：row ", row, ' col', index.column(), ' data ', oldValue)
        self.__addOrEditItemFunc(callback=self.__addOrEditItemCallback,
                                 default=self.__items[row],
                                 items=self.__items)
        pass

    def __customRightMenuRequested(self, pos):
        self.__curRow = self.__tableView.currentIndex().row()
        LogUtil.i(TAG, "__customRightMenuRequested", pos, ' row: ', self.__curRow)
        menu = WidgetUtil.createMenu("删除", func1=self.__delItemDialog)
        menu.exec(self.__tableView.mapToGlobal(pos))
        pass

    def __delItemDialog(self):
        primaryName = self.__items[self.__curRow][KEY_PRIMARY]
        LogUtil.i(TAG, f"__delItemDialog {primaryName}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{primaryName}</span> 吗？",
                                      acceptFunc=self.__delItemFunc)
        pass

    def __delItemFunc(self):
        LogUtil.i(TAG, "delRuleTableItem")
        self.__items.remove(self.__items[self.__curRow])
        self.__updateTableView()
        pass

    def __updateTableView(self):
        tableData = []
        for item in self.__items:
            data = {}
            for key, value in self.__headers.items():
                data[key] = DictUtil.get(item, key, DictUtil.get(value, KEY_DEFAULT, ''))
            tableData.append(data)
        WidgetUtil.addTableViewData(self.__tableView, tableData,
                                    headerLabels=[item[KEY_TITLE] for item in self.__headers.values()])
        pass

    def getData(self):
        return self.__items


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonTableView(addBtnTxt='添加',
                        headers={
                            KEY_PRIMARY: {KEY_TITLE: '规则名'}, 'isEnable': {KEY_TITLE: 'Enable', KEY_DEFAULT: True},
                            'costTime': {KEY_TITLE: '统计耗时'}
                        },
                        items=[{
                            KEY_PRIMARY: '22'
                        }, {
                            KEY_PRIMARY: '33',
                            'isEnable': False,
                            'costTime': 20,
                        }], addOrEditItemFunc=lambda callback, default=None, items=None: callback({KEY_PRIMARY: '55'})
                        )
    e.show()
    sys.exit(app.exec_())
