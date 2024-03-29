# -*- coding: utf-8 -*-
# python 3.x
# Filename: EditTestStepDialog.py
# 定义一个EditTestStepDialog类实现添加测试步骤
from PyQt5.QtWidgets import QAbstractButton
from constant.WidgetConst import *
from util.AutoTestUtil import *
from util.Uiautomator import *

TAG = "EditTestStepDialog"


class EditTestStepDialog(QtWidgets.QDialog):
    def __init__(self, callbackFunc, stepType=const.STEP_TYPE_SINGLE_CLICK, params={}, u: Uiautomator = None,
                 isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        EditTestStepDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.5)
        EditTestStepDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d(TAG, "Init edit test step Dialog")
        self.setObjectName("EditTestStepDialog")
        self.resize(EditTestStepDialog.WINDOW_WIDTH, EditTestStepDialog.WINDOW_HEIGHT)
        # self.setFixedSize(EditTestStepDialog.WINDOW_WIDTH, EditTestStepDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="添加/编辑Test step"))

        self.callbackFunc = callbackFunc
        self.stepType: int = stepType
        self.params = params
        self.u: Uiautomator = u
        self.t: AutoTestUtil = None

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="操作类型：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(80, const.HEIGHT)))
        self.superTestTypes = WidgetUtil.createButtonGroup(buttonClicked=self.superTestTypeToggled)
        for i in range(len(const.STEP_TYPE_NAMES)):
            radioButton = WidgetUtil.createRadioButton(self, text=const.STEP_TYPE_NAMES[i] + "  ",
                                                       isChecked=(stepType // 10 == i))
            self.superTestTypes.addButton(radioButton, i)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(self, text="", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(80, const.HEIGHT)))
        self.subClickTestTypes = WidgetUtil.createButtonGroup(buttonClicked=self.subClickTestTypeToggled)
        for i in range(len(const.CLICK_TYPES)):
            radioButton = WidgetUtil.createRadioButton(self, text=const.CLICK_TYPES[i] + "  ", isChecked=False)
            self.subClickTestTypes.addButton(radioButton, i)
            hbox.addWidget(radioButton)

        self.subSwipeTestTypes = WidgetUtil.createButtonGroup(buttonClicked=self.subSwipeTestTypeToggled)
        for i in range(len(const.SWIPE_TYPES)):
            radioButton = WidgetUtil.createRadioButton(self, text=const.SWIPE_TYPES[i] + "  ", isChecked=False)
            self.subSwipeTestTypes.addButton(radioButton, i)
            hbox.addWidget(radioButton)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        clickParamGroupBox = self.createClickParamGroupBox(self)
        vbox.addWidget(clickParamGroupBox)

        swipeParamGroupBox = self.createSwipeParamGroupBox(self)
        vbox.addWidget(swipeParamGroupBox)

        findParamGroupBox = self.createFindParamGroupBox(self)
        vbox.addWidget(findParamGroupBox)
        vbox.addWidget(WidgetUtil.createLabel(self), 1)

        self.groupBoxList = []
        self.groupBoxList.append(clickParamGroupBox)
        self.groupBoxList.append(swipeParamGroupBox)
        self.groupBoxList.append(findParamGroupBox)

        self.subTestTypeToggledVisible()
        self.setClickParam(self.params)
        self.setSwipeParam(self.params)
        self.setFindParam(self.params)

        btnBox = WidgetUtil.createDialogButtonBox(
            standardButton=QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Ignore,
            parent=self, clickedFunc=self.clickedFunc)
        self.testBtn = btnBox.button(QDialogButtonBox.Ignore if PlatformUtil.isMac() else QDialogButtonBox.Ok)
        self.cancelBtn = btnBox.button(QDialogButtonBox.Cancel if PlatformUtil.isMac() else QDialogButtonBox.Ignore)
        self.okBtn = btnBox.button(QDialogButtonBox.Ok if PlatformUtil.isMac() else QDialogButtonBox.Cancel)
        self.testBtn.setText("Test")
        self.cancelBtn.setText("Cancel")
        self.okBtn.setText("Ok")

        vbox.addWidget(btnBox)

        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
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
        LogUtil.i(TAG, "superTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[index])
        self.subTestTypeToggledVisible()
        self.setClickParam()
        self.setSwipeParam()
        self.setFindParam()
        pass

    def subClickTestTypeToggled(self):
        superIndex = self.superTestTypes.checkedId()
        subIndex = self.subClickTestTypes.checkedId()
        self.stepType = superIndex * 10 + subIndex
        LogUtil.i(TAG, "subClickTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex],
                  const.CLICK_TYPES[subIndex])
        pass

    def subSwipeTestTypeToggled(self):
        superIndex = self.superTestTypes.checkedId()
        subIndex = self.subSwipeTestTypes.checkedId()
        self.stepType = superIndex * 10 + subIndex
        LogUtil.i(TAG, "subSwipeTestTypeToggled", self.stepType, const.STEP_TYPE_NAMES[superIndex],
                  const.SWIPE_TYPES[subIndex])
        pass

    def createClickParamGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="click params")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="目标对象XPath：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        self.clickXpathLineEdit = WidgetUtil.createLineEdit(box)
        hbox.addWidget(self.clickXpathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        sizePolicy = WidgetUtil.createSizePolicy()
        hbox.addWidget(WidgetUtil.createLabel(box, text="click对象坐标：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        hbox.addWidget(WidgetUtil.createLabel(box, text="x坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(50, const.HEIGHT)))
        self.clickXPosSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.5, minValue=0, maxValue=10000,
                                                               step=0.1, suffix='  %/px', decimals=3,
                                                               sizePolicy=sizePolicy)
        hbox.addWidget(self.clickXPosSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="y坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(50, const.HEIGHT)))
        self.clickYPosSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.5, minValue=0, maxValue=10000,
                                                               step=0.1, suffix='  %/px', decimals=3,
                                                               sizePolicy=sizePolicy)
        hbox.addWidget(self.clickYPosSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="描述：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        self.clickDescLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.clickDescLineEdit)
        vbox.addLayout(hbox)
        return box

    def createSwipeParamGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="swipe params")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        sizePolicy = WidgetUtil.createSizePolicy()
        hbox.addWidget(WidgetUtil.createLabel(box, text="起始坐标：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(80, const.HEIGHT)))
        hbox.addWidget(WidgetUtil.createLabel(box, text="x坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(50, const.HEIGHT)))
        self.swipeXPosSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.5, minValue=0, maxValue=10000,
                                                               step=0.1, suffix='  %/px', decimals=3,
                                                               sizePolicy=sizePolicy)
        hbox.addWidget(self.swipeXPosSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="y坐标", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(50, const.HEIGHT)))
        self.swipeYPosSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.5, minValue=0, maxValue=10000,
                                                               step=0.1, suffix='  %/px', decimals=3,
                                                               sizePolicy=sizePolicy)
        hbox.addWidget(self.swipeYPosSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="滑动距离：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(80, const.HEIGHT)))
        self.swipeDistanceSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.3, minValue=0, maxValue=10000,
                                                                   step=0.1, suffix='  %/px', decimals=3,
                                                                   sizePolicy=sizePolicy)
        hbox.addWidget(self.swipeDistanceSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="滑动时长：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(80, const.HEIGHT)))
        self.swipeDurationSpinBox = WidgetUtil.createDoubleSpinBox(box, value=0.03, minValue=0.005, maxValue=10,
                                                                   step=0.01, suffix='  s', decimals=3,
                                                                   sizePolicy=sizePolicy)
        hbox.addWidget(self.swipeDurationSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="描述：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(80, const.HEIGHT)))
        self.swipeDescLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.swipeDescLineEdit)
        vbox.addLayout(hbox)
        return box

    def createFindParamGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="find params")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        sizePolicy = WidgetUtil.createSizePolicy()
        hbox.addWidget(WidgetUtil.createLabel(box, text="目标对象XPath：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        self.findXathLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.findXathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="间隔时间：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        self.intervalTimeSpinBox = WidgetUtil.createSpinBox(box, value=3, minValue=1, maxValue=10, step=1,
                                                            suffix='s', sizePolicy=sizePolicy)
        hbox.addWidget(self.intervalTimeSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="等待次数：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(150, const.HEIGHT)))
        self.repeatNumSpinBox = WidgetUtil.createSpinBox(box, value=0, minValue=0, maxValue=10, step=1,
                                                         suffix='次', sizePolicy=sizePolicy)
        hbox.addWidget(self.repeatNumSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="描述：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                                              minSize=QSize(100, const.HEIGHT)))
        self.findDescLineEdit = WidgetUtil.createLineEdit(box, sizePolicy=sizePolicy)
        hbox.addWidget(self.findDescLineEdit)
        vbox.addLayout(hbox)
        return box

    def setClickParam(self, params: dict = {}):
        keys = params.keys()
        if keys.__contains__(const.KEY_XPATH) and params[const.KEY_XPATH]:
            self.clickXpathLineEdit.setText(params[const.KEY_XPATH])
        else:
            self.clickXpathLineEdit.setText('')
        if keys.__contains__(const.KEY_X):
            self.clickXPosSpinBox.setValue(params[const.KEY_X])
        else:
            self.clickXPosSpinBox.setValue(0.5)
        if keys.__contains__(const.KEY_Y):
            self.clickYPosSpinBox.setValue(params[const.KEY_Y])
        else:
            self.clickYPosSpinBox.setValue(0.5)
        if keys.__contains__(const.KEY_DESC) and not keys.__contains__(const.KEY_AUTO_GEN_DESC):
            self.clickDescLineEdit.setText(params[const.KEY_DESC])
        else:
            self.clickDescLineEdit.setText('')

    def setSwipeParam(self, params: dict = {}):
        keys = params.keys()
        if keys.__contains__(const.KEY_X):
            self.swipeXPosSpinBox.setValue(params[const.KEY_X])
        else:
            self.swipeXPosSpinBox.setValue(0.5)
        if keys.__contains__(const.KEY_Y):
            self.swipeYPosSpinBox.setValue(params[const.KEY_Y])
        else:
            self.swipeYPosSpinBox.setValue(0.5)
        if keys.__contains__(const.KEY_DISTANCE):
            self.swipeDistanceSpinBox.setValue(params[const.KEY_DISTANCE])
        else:
            self.swipeDistanceSpinBox.setValue(0.3)
        if keys.__contains__(const.KEY_DURATION):
            self.swipeDurationSpinBox.setValue(params[const.KEY_DURATION])
        else:
            self.swipeDurationSpinBox.setValue(0.03)
        if keys.__contains__(const.KEY_DESC) and not keys.__contains__(const.KEY_AUTO_GEN_DESC):
            self.swipeDescLineEdit.setText(params[const.KEY_DESC])
        else:
            self.swipeDescLineEdit.setText('')

    def setFindParam(self, params: dict = {}):
        keys = params.keys()
        if keys.__contains__(const.KEY_XPATH) and params[const.KEY_XPATH]:
            self.findXathLineEdit.setText(params[const.KEY_XPATH])
        else:
            self.findXathLineEdit.setText('')
        if keys.__contains__(const.KEY_INTERVAL_TIME):
            self.intervalTimeSpinBox.setValue(params[const.KEY_INTERVAL_TIME])
        else:
            self.intervalTimeSpinBox.setValue(3)
        if keys.__contains__(const.KEY_REPEAT_NUM):
            self.repeatNumSpinBox.setValue(params[const.KEY_REPEAT_NUM])
        else:
            self.repeatNumSpinBox.setValue(0)
        if keys.__contains__(const.KEY_DESC) and not keys.__contains__(const.KEY_AUTO_GEN_DESC):
            self.findDescLineEdit.setText(params[const.KEY_DESC])
        else:
            self.findDescLineEdit.setText('')

    def clickedFunc(self, btn: QAbstractButton):
        LogUtil.d(TAG, "clickedFunc", btn.text())
        if btn == self.testBtn:
            self.testStep()
        elif btn == self.cancelBtn:
            self.close()
        elif btn == self.okBtn:
            self.acceptFunc()
        pass

    def acceptFunc(self):
        LogUtil.i(TAG, "acceptFunc")
        self.getParams()
        if not self.checkParams():
            LogUtil.i(TAG, "testStep params check failed.")
            return
        if self.callbackFunc:
            self.callbackFunc(self.stepType, self.params)
        self.close()
        pass

    def testStep(self):
        LogUtil.i(TAG, "testStep")
        if not self.u:
            self.u = Uiautomator()
        if not self.t:
            self.t = AutoTestUtil(self.u)
        if self.u.err:
            self.u.reConnect()
            if self.u.err:
                WidgetUtil.showErrorDialog(message='连接设备错误信息：{}'.format(self.u.err))
                return
        self.getParams()
        if not self.checkParams():
            LogUtil.i(TAG, "testStep params check failed.")
            return
        res = self.t.startTestStep(stepType=self.stepType, params=self.params)
        LogUtil.d(TAG, 'res:', res)
        pass

    def getParams(self):
        self.params = {}
        if self.stepType // 10 == 0:
            self.params[const.KEY_XPATH] = self.clickXpathLineEdit.text().strip()
            x = self.clickXPosSpinBox.value()
            self.params[const.KEY_X] = x
            y = self.clickYPosSpinBox.value()
            self.params[const.KEY_Y] = y
            desc = self.clickDescLineEdit.text().strip()
            if not desc:
                self.params[const.KEY_AUTO_GEN_DESC] = True
                desc = '{} xpath: "{}" or position: ({}{}, {}{})' \
                    .format(AutoTestUtil.stepName(self.stepType), self.params[const.KEY_XPATH],
                            x, '%' if x < 1 else 'px', y, '%' if y < 1 else 'px')
            self.params[const.KEY_DESC] = desc
        elif self.stepType // 10 == 1:
            x = self.swipeXPosSpinBox.value()
            self.params[const.KEY_X] = x
            y = self.swipeYPosSpinBox.value()
            self.params[const.KEY_Y] = y
            distance = self.swipeDistanceSpinBox.value()
            self.params[const.KEY_DISTANCE] = distance
            duration = self.swipeDurationSpinBox.value()
            self.params[const.KEY_DURATION] = duration
            desc = self.swipeDescLineEdit.text().strip()
            if not desc:
                self.params[const.KEY_AUTO_GEN_DESC] = True
                desc = '{} start position: ({}{}, {}{}) swipe distance: {}{} duration: {}s' \
                    .format(AutoTestUtil.stepName(self.stepType), x, '%' if x < 1 else 'px', y, '%' if y < 1 else 'px',
                            distance, '%' if distance < 1 else 'px', duration)
            self.params[const.KEY_DESC] = desc
        elif self.stepType // 10 == 2:
            self.params[const.KEY_XPATH] = self.findXathLineEdit.text().strip()
            self.params[const.KEY_INTERVAL_TIME] = self.intervalTimeSpinBox.value()
            self.params[const.KEY_REPEAT_NUM] = self.repeatNumSpinBox.value()
            desc = self.findDescLineEdit.text().strip()
            if not desc:
                self.params[const.KEY_AUTO_GEN_DESC] = True
                desc = '{} xpath: "{}" interval time: {}s repeat: {}次' \
                    .format(AutoTestUtil.stepName(self.stepType), self.params[const.KEY_XPATH],
                            self.params[const.KEY_INTERVAL_TIME], self.params[const.KEY_REPEAT_NUM])
            self.params[const.KEY_DESC] = desc

        LogUtil.i(TAG, "getParams", self.stepType, self.params)
        pass

    def checkParams(self):
        if not self.params:
            WidgetUtil.showErrorDialog(message="请先设置执行参数")
            return False
        keys = self.params.keys()
        if not keys:
            WidgetUtil.showErrorDialog(message="请先设置执行参数")
            return False
        if self.stepType // 10 == 2 and (not keys.__contains__(const.KEY_XPATH) or not self.params[const.KEY_XPATH]):
            WidgetUtil.showErrorDialog(message="请设置xpath参数")
            return False
        return True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = EditTestStepDialog(callbackFunc=lambda stepType, params: {
        LogUtil.d(TAG, "callback:", "stepType", stepType, "params", params)
    }, isDebug=True)
    window.show()
    sys.exit(app.exec_())
