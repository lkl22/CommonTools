# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamDialog.py
# 定义一个MockExamDialog类实现考试刷题
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QScrollArea, QGridLayout

from constant.WidgetConst import *
from util.ExcelUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *
from util.OperaIni import *
from widget.mockExam.MockExamUtil import *


class MockExamDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)

        self.label = None
        self.multiOptionBtnList = None
        self.questionDesc = None
        self.oneChoiceGroup = None
        self.oneChoiceOptionBtnList = None
        self.examFilePath = None
        self.mockExamUtil = None

        LogUtil.d("Mock Exam Dialog")
        self.setObjectName("MockExamDialog")
        self.resize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)
        self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="模拟考试"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(
            QRect(const.PADDING, const.PADDING, MockExamDialog.WINDOW_WIDTH - const.PADDING * 2,
                  MockExamDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        genMockExamGroupBox = self.createGenMockExamGroupBox(layoutWidget)
        vLayout.addWidget(genMockExamGroupBox)

        questionArea = self.createQuestionArea()
        vLayout.addWidget(questionArea)

        splitter, self.submitBtn, self.nextBtn, self.preBtn = \
            DialogUtil.createBottomBtn(self, okBtnText="交卷", okCallback=self.submitFunc,
                                       cancelBtnText="下一题", cancelCallback=self.nextQuestionFunc,
                                       ignoreBtnText="上一题", ignoreCallback=self.preQuestionFunc)
        vLayout.addLayout(splitter)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createGenMockExamGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = MockExamDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="",
                                        minSize=QSize(width, const.GROUP_BOX_MARGIN_TOP + const.HEIGHT_OFFSET * 3))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))

        WidgetUtil.createPushButton(splitter, text="选择题库模版", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getExamFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.examFilePathLineEdit = WidgetUtil.createLineEdit(splitter,
                                                              text="/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx",
                                                              isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        self.genExamPaperByRealBtn = WidgetUtil.createPushButton(splitter, text="生成试卷",
                                                                 onClicked=self.genExamPaperByReal)
        self.genExamPaperByAllBtn = WidgetUtil.createPushButton(splitter, text="全量模拟", onClicked=self.genExamPaperByAll)
        self.startMockExamBtn = WidgetUtil.createPushButton(splitter, text="开始", isEnable=False,
                                                            onClicked=self.startMockExam)
        return box

    def createQuestionArea(self):
        self.scrollAres = QScrollArea(self)
        self.scrollAres.setWidgetResizable(True)

        self.scrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        self.scrollAres.setSizePolicy(WidgetUtil.createSizePolicy())
        self.questionVBox = QtWidgets.QVBoxLayout(self.scrollAreaWidget)
        self.scrollAres.setWidget(self.scrollAreaWidget)
        return self.scrollAres

    def getExamFilePath(self):
        fn = WidgetUtil.getOpenFileName(caption='选择模拟考试题库Excel文件', filter='*.xlsx', initialFilter='*.xlsx')
        if fn:
            self.examFilePathLineEdit.setText(fn)
        pass

    def genExamPaperByReal(self):
        self.genExamPaper(False)
        pass

    def genExamPaperByAll(self):
        self.genExamPaper(True)
        pass

    def genExamPaperMethod(self, isAll):
        if isAll:
            self.mockExamUtil.genExamPaperByAll()
        else:
            self.mockExamUtil.genExamPaperByReal()
        pass

    def genExamPaper(self, isAll):
        if self.examFilePath == self.examFilePathLineEdit.text() and self.mockExamUtil:
            self.genExamPaperMethod(isAll)
            return

        if not FileUtil.existsFile(self.examFilePathLineEdit.text()):
            WidgetUtil.showErrorDialog(message="请选择模拟考试的题库文件")
            return
        try:
            self.mockExamUtil = MockExamUtil(self.examFilePathLineEdit.text())
            self.examFilePath = self.examFilePathLineEdit.text()
            self.genExamPaperMethod(isAll)
            self.startMockExamBtn.setEnabled(True)
        except Exception as err:
            LogUtil.e('mkDirs 错误信息：', err)
            self.examFilePath = None
            WidgetUtil.showErrorDialog(message="请选择正确的模拟考试的题库文件（按照指定规范提供）")
            return
        pass

    def prepareLayout(self):
        if not self.questionDesc:
            self.questionDesc = WidgetUtil.createTextEdit(self.scrollAreaWidget, isReadOnly=True)
            self.questionDesc.setMinimumHeight(160)
            self.questionVBox.addWidget(self.questionDesc)

        if not self.oneChoiceGroup:
            self.oneChoiceOptionBtnList = []
            self.oneChoiceGroup = WidgetUtil.createButtonGroup(onToggled=self.oneChoiceToggled)
            for option in range(self.maxOptionNum + 1):
                radioButton = WidgetUtil.createRadioButton(self.scrollAreaWidget, isEnable=True)
                radioButton.setMinimumHeight(30)
                self.oneChoiceOptionBtnList.append(radioButton)
                self.oneChoiceGroup.addButton(radioButton, option)
                self.questionVBox.addWidget(radioButton)

        if not self.multiOptionBtnList:
            self.multiOptionBtnList = []
            for option in range(self.maxOptionNum + 1):
                checkBox = WidgetUtil.createCheckBox(self.scrollAreaWidget)
                checkBox.setMinimumHeight(30)
                self.multiOptionBtnList.append(checkBox)
                self.questionVBox.addWidget(checkBox)

        if not self.label:
            self.label = WidgetUtil.createLabel(self.scrollAreaWidget)
            self.label.setSizePolicy(WidgetUtil.createSizePolicy())
            self.questionVBox.addWidget(self.label)
        pass

    def startMockExam(self):
        LogUtil.e("startMockExam")
        self.genExamPaperByRealBtn.setEnabled(False)
        self.genExamPaperByAllBtn.setEnabled(False)

        self.maxOptionNum = self.mockExamUtil.maxOptionNum()
        self.prepareLayout()
        questionObj = self.mockExamUtil.nextRequest()
        self.renderQuestion(questionObj)
        self.updateChangeQuestionBtn()
        pass

    def updateChangeQuestionBtn(self):
        self.preBtn.setEnabled(self.mockExamUtil.hasPre())
        self.nextBtn.setEnabled(self.mockExamUtil.hasNext())

    def renderQuestion(self, questionObj):
        self.questionDesc.setText(f"{questionObj[KEY_REAL_QUESTION_NO]}. " + questionObj[KEY_QUESTION])

        if questionObj[KEY_QUESTION_TYPE] == QUESTION_TYPE_MULTI_CHOICE:
            self.updateChoiceOptionBtn(questionObj, self.multiOptionBtnList)
        else:
            self.updateChoiceOptionBtn(questionObj, self.oneChoiceOptionBtnList)
        pass

    def oneChoiceToggled(self):
        oneChoiceId = self.oneChoiceGroup.checkedId()
        LogUtil.e("oneChoiceToggled", oneChoiceId)
        pass

    def updateChoiceOptionBtn(self, questionObj, choiceOptionBtnList):
        # 为了消除按钮选中状态
        self.oneChoiceGroup.setExclusive(False)
        for radioButton in self.oneChoiceOptionBtnList:
            radioButton.setVisible(False)
            radioButton.setChecked(False)
        self.oneChoiceGroup.setExclusive(True)

        for checkBox in self.multiOptionBtnList:
            checkBox.setVisible(False)
            checkBox.setChecked(False)

        for optionIndex in range(self.maxOptionNum):
            optionX = chr(65 + optionIndex)
            optionDesc = questionObj[optionX]
            if optionDesc:
                choiceOptionBtnList[optionIndex].setText(optionDesc)
                choiceOptionBtnList[optionIndex].setVisible(True)
            else:
                break

    def preQuestionFunc(self):
        LogUtil.d("preQuestionFunc")
        question = self.mockExamUtil.preRequest()
        self.renderQuestion(question)
        self.updateChangeQuestionBtn()
        return False

    def nextQuestionFunc(self):
        LogUtil.d("nextQuestionFunc")
        question = self.mockExamUtil.nextRequest()
        self.renderQuestion(question)
        self.updateChangeQuestionBtn()
        return False

    def submitFunc(self):
        LogUtil.d("submitFunc")
        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockExamDialog()
    window.show()
    sys.exit(app.exec_())
