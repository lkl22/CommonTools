# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonRadioButtons.py
# 定义一个CommonRadioButtons窗口类实现通用单选按钮选择的功能
import sys
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonRadioButtons'


class CommonRadioButtons(ICommonWidget):
    def __init__(self, label: str, groupList: list[dict or str], defaultValue=None, buttonClicked=None, maxCount=12,
                 spacing=30, toolTip=None):
        """
        创建通用的单选按钮选项组件
        :param label: 选项描述文本
        :param groupList: 选项列表
        :param defaultValue: 默认选中选项的文本
        :param buttonClicked: 点击回调
        :param maxCount: 一行显示最大的item
        :param spacing: item间间隔
        :param toolTip: toolTip
        """
        super(CommonRadioButtons, self).__init__()

        self.__groupList = []
        self.__defaultValue = None
        self.__buttonClicked = buttonClicked
        self.__radioButtons: [QRadioButton] = []
        self.__spacing = spacing
        self.__maxCount = maxCount
        self.__buttonGroup = None

        self.__vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        self.__labelWidget = WidgetUtil.createLabel(self, text=label)

        self.updateData(groupList, defaultValue)

        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __internalButtonClicked(self, radioButton):
        radioInfo = self.__groupList[self.__buttonGroup.checkedId()]
        self.__defaultValue = DictUtil.get(radioInfo, KEY_DATA, DictUtil.get(radioInfo, KEY_SHOW_TEXT))
        LogUtil.i(TAG, "__internalButtonClicked：", self.__defaultValue)
        if self.__buttonClicked:
            self.__buttonClicked(self.__defaultValue)
        pass

    def __removeOldWidget(self):
        # 必须调一下delete，不然旧的还会显示
        for checkBox in self.__radioButtons:
            checkBox.deleteLater()
        self.__radioButtons.clear()
        WidgetUtil.removeAllChild(self.__vbox)
        pass

    def __updateUi(self):
        self.__vbox.addWidget(self.__labelWidget)
        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=self.__spacing)
        self.__buttonGroup = WidgetUtil.createButtonGroup(buttonClicked=self.__internalButtonClicked)
        for i in range(len(self.__groupList)):
            if i % self.__maxCount == 0:
                hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
                self.__vbox.addLayout(hbox)
                hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=self.__spacing)
            radioData = DictUtil.get(self.__groupList[i], KEY_DATA, DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT))
            radioButton = WidgetUtil.createRadioButton(self, text=DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT, ''),
                                                       isChecked=radioData == self.__defaultValue)
            self.__buttonGroup.addButton(radioButton, i)
            self.__radioButtons.append(radioButton)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.__vbox.addLayout(hbox)
        # 重新调整尺寸
        self.adjustSize()
        pass

    def updateData(self, groupList: list[dict or str], defaultValue=None):
        if type(groupList[0]) == str:
            self.__groupList = [{KEY_SHOW_TEXT: item} for item in groupList]
        else:
            self.__groupList = groupList
        self.__defaultValue = defaultValue if defaultValue else DictUtil.get(self.__groupList[0], KEY_DATA,
                                                                             DictUtil.get(self.__groupList[0],
                                                                                          KEY_SHOW_TEXT))

        self.__removeOldWidget()
        self.__updateUi()
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
                           buttonClicked=lambda data: LogUtil.d(TAG, data),
                           maxCount=2,
                           toolTip='dddddd')
    e.show()

    e.updateData(groupList=[{
        KEY_SHOW_TEXT: 'gggg',
        KEY_DATA: 'gg'
    }, {
        KEY_SHOW_TEXT: 'eee',
        KEY_DATA: 'ee'
    }], defaultValue='ee')
    sys.exit(app.exec_())
