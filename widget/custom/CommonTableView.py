# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonTableView.py
# 定义一个CommonTableView窗口类实现通用tableView的功能
import sys
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonTableView'


class CommonTableView(ICommonWidget):
    def __init__(self, addBtnTxt: str, headers: {}, items: list[dict], addOrEditItemFunc,
                 toolTip=None):
        super(CommonTableView, self).__init__()
        self.setMinimumWidth(int(WidgetUtil.getScreenWidth() * 0.25))

        self.__headers = headers
        self.__items = items
        self.__addOrEditItemFunc = addOrEditItemFunc
        self.__curRow = -1

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        self.__addItemBtn = WidgetUtil.createPushButton(self, text=addBtnTxt, onClicked=self.__addItem)
        hbox.addWidget(self.__addItemBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addWidget(WidgetUtil.createLabel(self, text="顺序调整:"))
        self.__moveTopBtn = WidgetUtil.createPushButton(self, text="⬆️️", toolTip="移动到首行", isEnable=False,
                                                        onClicked=lambda: self.__moveCmdPosition(0))
        hbox.addWidget(self.__moveTopBtn)
        self.__moveUpOneBtn = WidgetUtil.createPushButton(self, text="↑️️", toolTip="向上移动一行", isEnable=False,
                                                          onClicked=lambda: self.__moveCmdPosition(
                                                              self.__curRow - 1))
        hbox.addWidget(self.__moveUpOneBtn)
        self.__moveDownOneBtn = WidgetUtil.createPushButton(self, text="↓️", toolTip="向下移动一行", isEnable=False,
                                                            onClicked=lambda: self.__moveCmdPosition(
                                                                self.__curRow + 1))
        hbox.addWidget(self.__moveDownOneBtn)
        self.__moveBottomBtn = WidgetUtil.createPushButton(self, text="⬇️️", toolTip="移动到末行", isEnable=False,
                                                           onClicked=lambda: self.__moveCmdPosition(-1))
        hbox.addWidget(self.__moveBottomBtn)
        vbox.addLayout(hbox)

        self.__tableView = WidgetUtil.createTableView(self, clicked=self.__tableClicked,
                                                      doubleClicked=self.__tableDoubleClicked)
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
        pass

    def __moveCmdPosition(self, newPos):
        LogUtil.d(TAG, "__moveCmdPosition", newPos)
        # 交换数据
        ListUtil.insert(self.__items, self.__curRow, newPos)
        # 更新table表格数据
        self.__updateTableView()
        # 更新当前选择的行
        self.__curRow = newPos if newPos >= 0 else len(self.__items) - 1
        self.__tableView.selectRow(self.__curRow)
        # 更新调整位置按钮的状态
        self.__updateMoveBtnStatus()
        pass

    def __updateMoveBtnStatus(self):
        LogUtil.d(TAG, "__updatePositionBtnStatus")
        size = len(self.__items)
        self.__moveTopBtn.setEnabled(self.__curRow > 0)
        self.__moveUpOneBtn.setEnabled(self.__curRow > 0)
        self.__moveDownOneBtn.setEnabled(0 <= self.__curRow < size - 1)
        self.__moveBottomBtn.setEnabled(0 <= self.__curRow < size - 1)
        pass

    def __tableClicked(self):
        currentRow = self.__tableView.currentIndex().row()
        LogUtil.d(TAG, "__tableClicked", currentRow)
        if currentRow != self.__curRow:
            self.__curRow = currentRow
            self.__updateMoveBtnStatus()
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
        LogUtil.i(TAG, "__delItemFunc")
        self.__items.remove(self.__items[self.__curRow])
        self.__curRow = -1
        self.__updateTableView()
        self.__updateMoveBtnStatus()
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
