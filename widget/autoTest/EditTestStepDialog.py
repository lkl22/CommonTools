# -*- coding: utf-8 -*-
# python 3.x
# Filename: EditTestStepDialog.py
# 定义一个EditTestStepDialog类实现添加测试步骤
from constant.TestStepConst import *
from constant.WidgetConst import *
from util.DialogUtil import *
from util.AutoTestUtil import *
from util.Uiautomator import *


class EditTestStepDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 350

    def __init__(self, callbackFunc, stepType=const.STEP_TYPE_SINGLE_CLICK, params={}, u: Uiautomator = None):
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
        self.u: Uiautomator = u
        self.t: AutoTestUtil = None

        sizePolicy = WidgetUtil.createSizePolicy()
        width = EditTestStepDialog.WINDOW_WIDTH - const.PADDING * 2

        vbox = WidgetUtil.createVBoxLayout()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       EditTestStepDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)

        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="操作类型：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.superTestTypes = WidgetUtil.createButtonGroup(onToggled=self.superTestTypeToggled)
        for i in range(len(const.STEP_TYPE_NAMES)):
            self.superTestTypes.addButton(
                WidgetUtil.createRadioButton(splitter, text=const.STEP_TYPE_NAMES[i] + "  ",
                                             isChecked=(stepType / 10 == i)), i)
        WidgetUtil.createLabel(splitter, text="", sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        self.subTypeSplitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width,
                                                                              const.HEIGHT))
        WidgetUtil.createLabel(self.subTypeSplitter, text="", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.subClickTestTypes = WidgetUtil.createButtonGroup(onToggled=self.subClickTestTypeToggled)
        for i in range(len(const.CLICK_TYPES)):
            self.subClickTestTypes.addButton(
                WidgetUtil.createRadioButton(self.subTypeSplitter, text=const.CLICK_TYPES[i] + "  ", isChecked=False),
                i)

        self.subSwipeTestTypes = WidgetUtil.createButtonGroup(onToggled=self.subSwipeTestTypeToggled)
        for i in range(len(const.SWIPE_TYPES)):
            self.subSwipeTestTypes.addButton(
                WidgetUtil.createRadioButton(self.subTypeSplitter, text=const.SWIPE_TYPES[i] + "  ", isChecked=False),
                i)

        WidgetUtil.createLabel(self.subTypeSplitter, text="", sizePolicy=sizePolicy)
        vbox.addWidget(self.subTypeSplitter)

        clickParamGroupBox = self.createClickParamGroupBox(layoutWidget)
        vbox.addWidget(clickParamGroupBox)

        swipeParamGroupBox = self.createSwipeParamGroupBox(layoutWidget)
        vbox.addWidget(swipeParamGroupBox)

        findParamGroupBox = self.createFindParamGroupBox(layoutWidget)
        vbox.addWidget(findParamGroupBox)

        self.groupBoxList = []
        self.groupBoxList.append(clickParamGroupBox)
        self.groupBoxList.append(swipeParamGroupBox)
        self.groupBoxList.append(findParamGroupBox)

        self.subTestTypeToggledVisible()

        splitter = DialogUtil.createBottomBtn(self, okCallback=self.acceptFunc, cancelBtnText="Cancel",
                                              ignoreBtnText='Test', ignoreCallback=self.testStep)
        vbox.addLayout(splitter)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def subTestTypeToggledVisible(self):
        """
        设置子测试类型显示隐藏
        """
        if self.stepType // 10 != 0:
            for btn in self.subClickTestTypes.buttons():
                btn.hide()
        else:
            for btn in self.subClickTestTypes.buttons():
                btn.setVisible(True)
            self.subClickTestTypes.button(self.stepType % 10).setChecked(True)

        if self.stepType // 10 != 1:
            for btn in self.subSwipeTestTypes.buttons():
                btn.hide()
        else:
            for btn in self.subSwipeTestTypes.buttons():
                btn.setVisible(True)
            self.subSwipeTestTypes.button(self.stepType % 10).setChecked(True)

        for i in range(len(self.groupBoxList)):
            self.groupBoxList[i].setVisible(self.stepType // 10 == i)

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
        LogUtil.i("subClickTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex],
                  const.CLICK_TYPES[subIndex])
        pass

    def subSwipeTestTypeToggled(self):
        superIndex = self.superTestTypes.checkedId()
        subIndex = self.subSwipeTestTypes.checkedId()
        self.stepType = superIndex * 10 + subIndex
        LogUtil.i("subSwipeTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex],
                  const.SWIPE_TYPES[subIndex])
        pass

    def createClickParamGroupBox(self, parent):
        width = EditTestStepDialog.WINDOW_WIDTH - const.PADDING * 8
        box = WidgetUtil.createGroupBox(parent, title="click params", minSize=QSize(width, 200))
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        WidgetUtil.createLabel(splitter, text="目标对象XPath：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.clickXpathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="click对象坐标：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="x坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(50, const.HEIGHT))
        self.clickXPosSpinBox = WidgetUtil.createDoubleSpinBox(splitter, value=0, minValue=0, maxValue=10000, step=0.1,
                                                               sizePolicy=sizePolicy)
        WidgetUtil.createLabel(splitter, text="y坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(50, const.HEIGHT))
        self.clickYPosSpinBox = WidgetUtil.createDoubleSpinBox(splitter, value=0, minValue=0, maxValue=10000, step=0.1,
                                                               sizePolicy=sizePolicy)
        return box

    def createSwipeParamGroupBox(self, parent):
        width = EditTestStepDialog.WINDOW_WIDTH - const.PADDING * 8
        box = WidgetUtil.createGroupBox(parent, title="swipe params", minSize=QSize(width, 200))
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        # WidgetUtil.createLabel(splitter, text="目标对象XPath：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
        #                        minSize=QSize(80, const.HEIGHT))
        # self.xpathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        return box

    def createFindParamGroupBox(self, parent):
        width = EditTestStepDialog.WINDOW_WIDTH - const.PADDING * 8
        box = WidgetUtil.createGroupBox(parent, title="find params", minSize=QSize(width, 200))
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        WidgetUtil.createLabel(splitter, text="目标对象XPath：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT))
        self.findXathLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        return box

    def acceptFunc(self):
        LogUtil.i("acceptFunc")
        return True

    def testStep(self):
        LogUtil.i("testStep")
        if not self.u:
            self.u = Uiautomator()
        if not self.t:
            self.t = AutoTestUtil(self.u)
        self.getParams()
        self.t.startTestStep(self.stepType, params=self.params)
        return False

    def getParams(self):
        self.params = {}
        if self.stepType // 10 == 0:
            self.params['xpath'] = self.clickXpathLineEdit.text().strip()
            self.params['x'] = self.clickXPosSpinBox.value()
            self.params['y'] = self.clickYPosSpinBox.value()
        LogUtil.i("getParams", self.stepType, self.params)
        pass
