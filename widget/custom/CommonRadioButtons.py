# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonRadioButtons.py
# 定义一个CommonRadioButtons窗口类实现通用单选按钮选择的功能
import sys

from constant.WidgetConst import *
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonRadioButtons'


class CommonRadioButtons(ICommonWidget):
    def __init__(self, label: str, groupList: list[dict or str], defaultValue=None, onToggled=None, maxCount=12, spacing=30,
                 toolTip=None):
        """
        创建通用的单选按钮选项组件
        :param label: 选项描述文本
        :param groupList: 选项列表
        :param defaultValue: 默认选中选项的文本
        :param onToggled: 点击回调
        :param maxCount: 一行显示最大的item
        :param spacing: item间间隔
        :param toolTip: toolTip
        """
        super(CommonRadioButtons, self).__init__()
        if type(groupList[0]) == str:
            self.__groupList = [{KEY_SHOW_TEXT: item} for item in groupList]
        else:
            self.__groupList = groupList
        self.__defaultValue = defaultValue if defaultValue else DictUtil.get(self.__groupList[0], KEY_DATA,
                                                                             DictUtil.get(self.__groupList[0], KEY_SHOW_TEXT))
        self.__onToggled = onToggled

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        vbox.addWidget(WidgetUtil.createLabel(self, text=label))
        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=spacing)
        self.__buttonGroup = WidgetUtil.createButtonGroup(onToggled=self.__internalOnToggled)
        for i in range(len(self.__groupList)):
            if i % maxCount == 0:
                hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
                vbox.addLayout(hbox)
                hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=spacing)
            radioData = DictUtil.get(self.__groupList[i], KEY_DATA, DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT))
            radioButton = WidgetUtil.createRadioButton(self, text=DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT, ''),
                                                       isChecked=radioData == self.__defaultValue)
            self.__buttonGroup.addButton(radioButton, i)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __internalOnToggled(self, radioButton):
        radioInfo = self.__groupList[self.__buttonGroup.checkedId()]
        self.__defaultValue = DictUtil.get(radioInfo, KEY_DATA, DictUtil.get(radioInfo, KEY_SHOW_TEXT))
        LogUtil.i(TAG, "__onToggled：", self.__defaultValue)
        if self.__onToggled:
            self.__onToggled(self.__defaultValue)
        pass

    def getData(self):
        return self.__defaultValue


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonRadioButtons(label='请选择：',
                           defaultValue='eeee',
                           groupList=[{
                               KEY_SHOW_TEXT: 'dd',
                               KEY_DATA: 'ddd'
                           }, {
                               KEY_SHOW_TEXT: 'rrr',
                               KEY_DATA: 'rr'
                           }, {
                               KEY_SHOW_TEXT: 'eeee'
                           }],
                           maxCount=2,
                           toolTip='dddddd')
    e.show()
    sys.exit(app.exec_())
