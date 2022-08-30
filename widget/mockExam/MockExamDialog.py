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

OPTION_CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def delDictData(key, dicts):
    if key in dicts:
        del dicts[key]
    pass


def getDictData(key, dicts):
    if key in dicts:
        return dicts[key]
    return None


class MockExamDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)

        self.curQuestionObj = None
        self.curQuestionNo = 1
        self.yourAnswers = {}
        self.errAnswers = {}
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
            # 必须是成员变量，本地变量不行，很奇怪
            self.multiChoiceGroup = WidgetUtil.createButtonGroup(onToggled=self.multiChoiceToggled)
            self.multiChoiceGroup.setExclusive(False)
            for option in range(self.maxOptionNum + 1):
                checkBox = WidgetUtil.createCheckBox(self.scrollAreaWidget)
                checkBox.setMinimumHeight(30)
                self.multiOptionBtnList.append(checkBox)
                self.multiChoiceGroup.addButton(checkBox, option)
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
        for no in range(1, self.mockExamUtil.totalQuestionNums + 1):
            self.errAnswers[no] = None

        self.prepareLayout()

        self.curQuestionNo = 1
        self.curQuestionObj = self.mockExamUtil.nextQuestion()
        self.renderQuestion(self.curQuestionObj, None)
        pass

    def updateChangeQuestionBtn(self):
        self.preBtn.setEnabled(self.mockExamUtil.hasPre())
        self.nextBtn.setEnabled(self.mockExamUtil.hasNext())

    def renderQuestion(self, questionObj, yourAnswer):
        self.questionDesc.setText(f"{questionObj[KEY_REAL_QUESTION_NO]}. " + questionObj[KEY_QUESTION])

        if questionObj[KEY_QUESTION_TYPE] == QUESTION_TYPE_MULTI_CHOICE:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.multiOptionBtnList)
        else:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.oneChoiceOptionBtnList)

        self.updateChangeQuestionBtn()
        pass

    def oneChoiceToggled(self):
        option = OPTION_CHAR[self.oneChoiceGroup.checkedId()]
        self.yourAnswers[self.curQuestionNo] = option
        if self.curQuestionObj[KEY_ANSWER] == option:
            delDictData(self.curQuestionNo, self.errAnswers)
        else:
            self.errAnswers[self.curQuestionNo] = option
        LogUtil.e("oneChoiceToggled", self.yourAnswers, self.errAnswers)
        pass

    def multiChoiceToggled(self):
        LogUtil.e("multiChoiceToggled")
        checkedOptions = []
        for index, checkBox in enumerate(self.multiOptionBtnList):
            if checkBox.isChecked():
                checkedOptions.append(OPTION_CHAR[index])

        if len(checkedOptions) > 0:
            self.yourAnswers[self.curQuestionNo] = checkedOptions
            self.errAnswers[self.curQuestionNo] = checkedOptions
            if len(checkedOptions) == len(self.curQuestionObj[KEY_ANSWER]):
                isCorrect = True
                for correctAnswer in self.curQuestionObj[KEY_ANSWER]:
                    if correctAnswer not in checkedOptions:
                        isCorrect = False
                        break
                if isCorrect:
                    delDictData(self.curQuestionNo, self.errAnswers)
        else:
            # 多选没有选择
            self.errAnswers[self.curQuestionNo] = None
            delDictData(self.curQuestionNo, self.yourAnswers)
        LogUtil.e("multiChoiceToggled", self.yourAnswers, self.errAnswers)
        pass

    def updateChoiceOptionBtn(self, questionObj, yourAnswer, choiceOptionBtnList):
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
                choiceOptionBtnList[optionIndex].setText(f"{optionX}. {optionDesc}")
                choiceOptionBtnList[optionIndex].setVisible(True)
            else:
                break
        if yourAnswer:
            for optionX in yourAnswer:
                choiceOptionBtnList[ord(optionX) - 65].setChecked(True)
        pass

    def preQuestionFunc(self):
        LogUtil.d("preQuestionFunc")
        self.curQuestionNo -= 1
        self.curQuestionObj = self.mockExamUtil.preQuestion()
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        return False

    def nextQuestionFunc(self):
        LogUtil.d("nextQuestionFunc")
        self.curQuestionNo += 1
        self.curQuestionObj = self.mockExamUtil.nextQuestion()
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        return False

    def submitFunc(self):
        LogUtil.d("submitFunc")
        if len(self.yourAnswers) < self.mockExamUtil.totalQuestionNums:
            WidgetUtil.showQuestionDialog(message=f"您还有{self.mockExamUtil.totalQuestionNums - len(self.yourAnswers)}道题未做，确认提交？",
                                          acceptFunc=self.submitExam)
        else:
            self.submitExam()
        return False

    def submitExam(self):
        errNo, score = self.mockExamUtil.calculateResults(self.errAnswers)
        isPassExam = self.mockExamUtil.isPassExam(score)
        LogUtil.d("submitExam", "做错：", errNo, "分数：", score, "通过：", isPassExam)
        if errNo > 0:
            if isPassExam:
                WidgetUtil.showQuestionDialog(message=f"恭喜您通过本轮考试，获得 {score} 分的好成绩，是否需要查看错误的题目？", acceptFunc=self.seeErrQuestions)
            else:
                WidgetUtil.showQuestionDialog(message=f"很遗憾您未能通过本轮考试，获得 {score} 分，是否需要查看错误的题目？", acceptFunc=self.seeErrQuestions)

        else:
            WidgetUtil.showAboutDialog(text="恭喜您获得满分的成绩，下次再接再厉！！！")

    def seeErrQuestions(self):
        LogUtil.d("seeErrQuestions")
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockExamDialog()
    window.show()
    sys.exit(app.exec_())
