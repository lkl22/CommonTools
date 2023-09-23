# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonCheckBoxs.py
# 定义一个CommonCheckBoxs窗口类实现通用复选框的功能
import sys
from util.DictUtil import DictUtil
from util.WidgetUtil import *
from widget.custom.ICommonWidget import ICommonWidget

TAG = 'CommonCheckBoxs'


class CommonCheckBoxs(ICommonWidget):
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
        super(CommonCheckBoxs, self).__init__()
        self.__groupList = []
        self.__defaultValue = []
        self.__buttonClicked = buttonClicked
        self.__checkBoxs: [QCheckBox] = []
        self.__label = label
        self.__spacing = spacing
        self.__maxCount = maxCount
        self.__buttonGroup = None

        self.vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 5, 5, 5), spacing=10)
        self.labelWidget = WidgetUtil.createLabel(self, text=self.__label)
        self.updateData(groupList, defaultValue)
        self.setAutoFillBackground(True)
        if toolTip:
            self.setToolTip(toolTip)
        pass

    def __internalButtonClicked(self, radioButton):
        selectData = []
        for index, checkBox in enumerate(self.__checkBoxs):
            if checkBox.isChecked():
                info = self.__groupList[index]
                selectData.append(DictUtil.get(info, KEY_DATA, DictUtil.get(info, KEY_SHOW_TEXT)))
        self.__defaultValue = selectData
        LogUtil.i(TAG, "__internalButtonClicked：", self.__defaultValue)
        if self.__buttonClicked:
            self.__buttonClicked(self.__defaultValue)
        pass

    def __removeOldWidget(self):
        # 必须调一下delete，不然旧的还会显示
        for checkBox in self.__checkBoxs:
            checkBox.deleteLater()
        self.__checkBoxs.clear()
        WidgetUtil.removeAllChild(self.vbox)
        pass

    def __updateUi(self):
        self.vbox.addWidget(self.labelWidget)
        hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=self.__spacing)
        self.__buttonGroup = WidgetUtil.createButtonGroup(buttonClicked=self.__internalButtonClicked, exclusive=False)
        for i in range(len(self.__groupList)):
            if i % self.__maxCount == 0:
                hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
                self.vbox.addLayout(hbox)
                hbox = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=self.__spacing)
            itemData = DictUtil.get(self.__groupList[i], KEY_DATA, DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT))
            isChecked = itemData in self.__defaultValue
            checkBox = WidgetUtil.createCheckBox(self, text=DictUtil.get(self.__groupList[i], KEY_SHOW_TEXT, ''),
                                                 isChecked=isChecked)
            self.__buttonGroup.addButton(checkBox, i)
            self.__checkBoxs.append(checkBox)
            hbox.addWidget(checkBox)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        self.vbox.addLayout(hbox)
        # 重新调整尺寸
        self.adjustSize()
        pass

    def updateData(self, groupList: list[dict or str], defaultValue=None):
        if type(groupList[0]) == str:
            self.__groupList = [{KEY_SHOW_TEXT: item} for item in groupList]
        else:
            self.__groupList = groupList
        self.__defaultValue = defaultValue if defaultValue else []

        self.__removeOldWidget()
        self.__updateUi()
        pass

    def getData(self):
        return self.__defaultValue


if __name__ == "__main__":
    app = QApplication(sys.argv)
    e = CommonCheckBoxs(label='请选择：',
                        defaultValue=['ddd', 'rr', 'eeee'],
                        groupList=[{
                            KEY_SHOW_TEXT: 'dd',
                            KEY_DATA: 'ddd'
                        }, {
                            KEY_SHOW_TEXT: 'rrr',
                            KEY_DATA: 'rr'
                        }, {
                            KEY_SHOW_TEXT: 'eeee'
                        }],
                        buttonClicked=lambda data: LogUtil.i(TAG, data),
                        maxCount=2,
                        toolTip='dddddd')
    e.show()

    e.updateData(groupList=[{
        KEY_SHOW_TEXT: 'dkkkkkd',
        KEY_DATA: 'djjdd'
    }, {
        KEY_SHOW_TEXT: 'rjjjjrr',
        KEY_DATA: 'rjjr'
    }])
    sys.exit(app.exec_())
