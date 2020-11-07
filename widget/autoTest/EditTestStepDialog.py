# -*- coding: utf-8 -*-
# python 3.x
# Filename: EditTestStepDialog.py
# 定义一个EditTestStepDialog类实现添加测试步骤
from constant.TestStepConst import *
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *


class EditTestStepDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 180

    def __init__(self, callbackFunc, stepType=const.STEP_TYPE_SINGLE_CLICK, params={}):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init edit test step Dialog")
        self.setObjectName("EditTestStepDialog")
        self.resize(EditTestStepDialog.WINDOW_WIDTH, EditTestStepDialog.WINDOW_HEIGHT)
        self.setFixedSize(EditTestStepDialog.WINDOW_WIDTH, EditTestStepDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Test step"))

        self.callbackFunc = callbackFunc
        self.stepType: int = stepType
        self.params = params

        sizePolicy = WidgetUtil.createSizePolicy()

        vbox = WidgetUtil.createVBoxLayout()
        width = EditTestStepDialog.WINDOW_WIDTH - const.PADDING * 2
        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="操作类型：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.superTestTypes = WidgetUtil.createButtonGroup(onToggled=self.superTestTypeToggled)
        for i in range(len(const.STEP_TYPE_NAMES)):
            self.superTestTypes.addButton(
                WidgetUtil.createRadioButton(splitter, text=const.STEP_TYPE_NAMES[i] + "  ", isChecked=(stepType / 10 == i)), i)
        WidgetUtil.createLabel(splitter, text="", sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        self.subTypeSplitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createLabel(self.subTypeSplitter, text="", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.subClickTestTypes = WidgetUtil.createButtonGroup(onToggled=self.subClickTestTypeToggled)
        for i in range(len(const.CLICK_TYPES)):
            self.subClickTestTypes.addButton(
                WidgetUtil.createRadioButton(self.subTypeSplitter, text=const.CLICK_TYPES[i] + "  ", isChecked=False), i)

        self.subSwipeTestTypes = WidgetUtil.createButtonGroup(onToggled=self.subSwipeTestTypeToggled)
        for i in range(len(const.SWIPE_TYPES)):
            self.subSwipeTestTypes.addButton(
                WidgetUtil.createRadioButton(self.subTypeSplitter, text=const.SWIPE_TYPES[i] + "  ", isChecked=False), i)

        WidgetUtil.createLabel(self.subTypeSplitter, text="", sizePolicy=sizePolicy)
        self.subTestTypeToggledVisible()
        vbox.addWidget(self.subTypeSplitter)

        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        # WidgetUtil.createPushButton(splitter, text="dark color：", minSize=QSize(100, const.HEIGHT), onClicked=self.darkColorSelected)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.darkColorLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = DialogUtil.createBottomBtn(self, okCallback=self.acceptFunc, cancelBtnText="Cancel")
        vbox.addLayout(splitter)

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       EditTestStepDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)
        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def subTestTypeToggledVisible(self):
        """
        设置子测试类型显示隐藏
        """
        if self.stepType / 10 != 0:
            for btn in self.subClickTestTypes.buttons():
                btn.hide()
        else:
            for btn in self.subClickTestTypes.buttons():
                btn.setVisible(True)
            self.subClickTestTypes.button(self.stepType % 10).setChecked(True)

        if self.stepType / 10 != 1:
            for btn in self.subSwipeTestTypes.buttons():
                btn.hide()
        else:
            for btn in self.subSwipeTestTypes.buttons():
                btn.setVisible(True)
            self.subSwipeTestTypes.button(self.stepType % 10).setChecked(True)

    def superTestTypeToggled(self):
        index = self.superTestTypes.checkedId()
        self.stepType = index * 10
        LogUtil.i("superTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[index])
        self.subTestTypeToggledVisible()
        pass

    def subClickTestTypeToggled(self):
        superIndex = self.superTestTypes.checkedId()
        subIndex = self.subClickTestTypes.checkedId()
        self.stepType = superIndex * 10 + subIndex
        LogUtil.i("subClickTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex], const.CLICK_TYPES[subIndex])
        pass

    def subSwipeTestTypeToggled(self):
        superIndex = self.superTestTypes.checkedId()
        subIndex = self.subSwipeTestTypes.checkedId()
        self.stepType = superIndex * 10 + subIndex
        LogUtil.i("subSwipeTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex], const.SWIPE_TYPES[subIndex])
        pass

    def acceptFunc(self):
        LogUtil.i("acceptFunc")
        pass

