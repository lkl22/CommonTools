# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonComboBox.py
# 定义一个CommonComboBox窗口类实现通用下拉选择弹框的功能
import copy
import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QListView
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonComboBox'


class CommonComboBox(ICommonWidget):
    def __init__(self, label: str, default=None, groupList: [{} or str] = [], isEditable=False, toolTip=None,
                 dataChanged=None):
        """
        创建下拉选择框
        :param label: label
        :param default: 默认数据
        :param groupList: 显示下拉列表数据
        :param isEditable: true 可以编辑
        :param toolTip: toolTip
        :param dataChanged: 选项changed回调事件
        """
        super(CommonComboBox, self).__init__()
        # self.setWindowFlags(QtCore.Qt.SplashScreen | QtCore.Qt.FramelessWindowHint)
        self.__originalGroupList = []
        self.__groupList = []
        self.__default = ''
        self.__curIndex = -1
        self.__dataChanged = dataChanged

        hBox = WidgetUtil.createHBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        hBox.addWidget(WidgetUtil.createLabel(self, text=label))
        self.__comboBox = WidgetUtil.createComboBox(self, isEditable=isEditable, activated=self.__activated)
        self.__comboBox.setView(QListView())
        self.setStyleSheet('QComboBox QAbstractItemView::item {padding-top:2px;padding-bottom:2px}')
        hBox.addWidget(self.__comboBox, 1)
        if isEditable:
            self.__deleteBtn = WidgetUtil.createPushButton(self, text='Del', onClicked=self.__showDeleteItemDialog)
            hBox.addWidget(self.__deleteBtn)
        self.updateData(default, groupList)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __updateComboBox(self):
        LogUtil.d(TAG, '__updateComboBox')
        curIndex = 0
        self.__comboBox.clear()
        for index, item in enumerate(self.__groupList):
            if KEY_SHOW_TEXT not in item:
                continue
            if KEY_COLOR in item:
                pixmap = QPixmap(180, 60)
                pixmap.fill(QColor(item[KEY_COLOR]))
                self.__comboBox.addItem(QIcon(pixmap), item[KEY_SHOW_TEXT])
            else:
                self.__comboBox.addItem(item[KEY_SHOW_TEXT])
            data = DictUtil.get(item, KEY_DATA, DictUtil.get(item, KEY_SHOW_TEXT))
            if self.__default == data:
                curIndex = index
        if not self.__groupList:
            self.__deleteBtn.setEnabled(False)
        self.__curIndex = curIndex
        self.__comboBox.setCurrentIndex(curIndex)
        pass

    def __activated(self, index):
        curText = self.__comboBox.currentText()
        LogUtil.d(TAG, '__activated oldIndex: ', self.__curIndex, ' newIndex: ', index, curText, len(self.__groupList))
        self.__curIndex = index
        if index >= len(self.__groupList):
            newData = {KEY_SHOW_TEXT: curText}
            self.__groupList.append(newData)
            self.__default = curText
            self.__deleteBtn.setEnabled(True)
            LogUtil.d(TAG, '__activated add item', newData)
        else:
            curData = self.__groupList[index]
            self.__default = DictUtil.get(curData, KEY_DATA, DictUtil.get(curData, KEY_SHOW_TEXT))
            LogUtil.d(TAG, '__activated', curData, self.__default, curText)
        if self.__dataChanged:
            self.__dataChanged(self.__default, None)
        pass

    def __showDeleteItemDialog(self):
        LogUtil.d(TAG, '__showDeleteItemDialog')
        if 0 <= self.__curIndex < len(self.__groupList):
            primaryName = self.__groupList[self.__curIndex][KEY_SHOW_TEXT]
            LogUtil.i(TAG, f"__showDeleteItemDialog {primaryName}")
            WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{primaryName}</span> 吗？",
                                          acceptFunc=self.__delItemFunc)
        pass

    def __delItemFunc(self):
        deleteItem = self.__groupList[self.__curIndex]
        deleteData = DictUtil.get(deleteItem, KEY_DATA, DictUtil.get(deleteItem, KEY_SHOW_TEXT))
        LogUtil.d(TAG, '__delItemFunc')
        ListUtil.remove(self.__groupList, self.__groupList[self.__curIndex])
        if len(self.__groupList) > 0:
            curData = self.__groupList[0]
            self.__default = DictUtil.get(curData, KEY_DATA, DictUtil.get(curData, KEY_SHOW_TEXT))
        else:
            self.__default = None
        self.__updateComboBox()
        if self.__dataChanged:
            self.__dataChanged(self.__default, deleteData)
        pass

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        # 不复写，按下entry键时，删除按钮事件也会被响应
        LogUtil.d(TAG, 'keyPressEvent')
        pass

    def updateData(self, default=None, groupList: [{} or str] = []):
        self.__originalGroupList = groupList
        if not groupList or type(groupList[0]) == str:
            self.__groupList = copy.deepcopy([{KEY_SHOW_TEXT: item} for item in groupList])
        else:
            self.__groupList = copy.deepcopy([item for item in groupList if item])
        self.__default = default if default else (DictUtil.get(self.__groupList[0], KEY_DATA,
                                                               DictUtil.get(self.__groupList[0],
                                                                            KEY_SHOW_TEXT)) if self.__groupList else '')
        self.__curIndex = -1
        self.__updateComboBox()
        pass

    def getData(self):
        return self.__default

    def getGroupList(self):
        if not self.__originalGroupList or type(self.__originalGroupList[0]) == str:
            return [item[KEY_SHOW_TEXT] for item in self.__groupList]
        return self.__groupList


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # e = CommonComboBox()
    # e = CommonComboBox(fileParam=["file", "./", "*.py", "*.py"])
    # e = CommonComboBox(dirParam=["dir", "./"])
    # e = CommonComboBox(label='选择颜色：', default='ss', groupList=[
    #     {KEY_COLOR: '#FF0000', KEY_SHOW_TEXT: 'red', KEY_DATA: 'ss'},
    #     {KEY_COLOR: '#00FF00', KEY_SHOW_TEXT: 'green'},
    #     {KEY_SHOW_TEXT: 'blue'}, {}
    # ], isEditable=True, toolTip='请选择需要的颜色', dataChanged=lambda data: LogUtil.d(TAG, data))
    e = CommonComboBox(label='选择颜色：', default='', groupList=[], isEditable=True, toolTip='请选择需要的颜色',
                       dataChanged=lambda data: LogUtil.d(TAG, 'callback', data))
    e.show()
    sys.exit(app.exec_())
