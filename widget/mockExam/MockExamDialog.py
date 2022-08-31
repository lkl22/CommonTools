# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamDialog.py
# 定义一个MockExamDialog类实现考试刷题
from PyQt5.QtCore import QModelIndex, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QScrollArea, QGridLayout, QPushButton

from constant.WidgetConst import *
from util.ExcelUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *
from util.OperaIni import *
from widget.mockExam.MockExamUtil import *

OPTION_CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ANSWER_CARD_MAX_COL = 20


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
        LogUtil.d("Mock Exam Dialog")

        self.examFilePath = None
        self.mockExamUtil = None

        self.genExamPaperByRealBtn = None
        self.genExamPaperByAllBtn = None
        self.startMockExamBtn = None
        self.restartMockExamBtn = None

        self.questionDescLabel = None
        self.oneChoiceGroup = None
        self.oneChoiceOptionBtnList = None
        self.multiChoiceOptionBtnList = None
        self.answerLabel = None
        self.solutionLabel = None
        self.remarkLabel = None
        self.label = None

        self.curQuestionObj = None
        self.curQuestionNo = 1

        self.yourAnswers = {}
        self.errAnswers = {}
        self.isShowErrQuestion = False
        self.curErrQuestionIndex = 0
        self.reviewErrQuestionNoList = None
        self.isLayout = False

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

        answerCardArea = self.createAnswerCardArea()
        vLayout.addWidget(answerCardArea)

        questionArea = self.createQuestionArea()
        vLayout.addWidget(questionArea)

        splitter, self.submitBtn, self.nextBtn, self.preBtn = \
            DialogUtil.createBottomBtn(self, okBtnText="交卷", okCallback=self.submitFunc,
                                       cancelBtnText="下一题", cancelCallback=self.nextQuestionFunc,
                                       ignoreBtnText="上一题", ignoreCallback=self.preQuestionFunc)
        vLayout.addLayout(splitter)

        self.prepareMockExam()
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
        self.restartMockExamBtn = WidgetUtil.createPushButton(splitter, text="重新开始", onClicked=self.restartMockExam)
        return box

    def createAnswerCardArea(self):
        self.answerCardScrollAres = QScrollArea(self)
        self.answerCardScrollAres.setWidgetResizable(True)

        self.answerCardScrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        self.answerCardScrollAres.setMaximumHeight(60)
        self.answerCardGrid = QtWidgets.QGridLayout(self.answerCardScrollAreaWidget)
        # 设置间距
        self.answerCardGrid.setSpacing(const.PADDING)
        self.answerCardGrid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.answerCardScrollAres.setWidget(self.answerCardScrollAreaWidget)
        return self.answerCardScrollAres

    def createQuestionArea(self):
        self.questionScrollAres = QScrollArea(self)
        self.questionScrollAres.setWidgetResizable(True)

        self.questionScrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        self.questionScrollAres.setSizePolicy(WidgetUtil.createSizePolicy())
        self.questionVBox = QtWidgets.QVBoxLayout(self.questionScrollAreaWidget)
        self.questionScrollAres.setWidget(self.questionScrollAreaWidget)
        return self.questionScrollAres

    def prepareMockExam(self):
        self.genExamPaperByRealBtn.setVisible(True)
        self.genExamPaperByRealBtn.setEnabled(True)
        self.genExamPaperByAllBtn.setVisible(True)
        self.genExamPaperByAllBtn.setEnabled(True)
        self.startMockExamBtn.setVisible(True)
        self.startMockExamBtn.setEnabled(False)
        self.restartMockExamBtn.setVisible(False)

        self.hideQuestionArea()

        self.preBtn.setVisible(True)
        self.preBtn.setEnabled(False)
        self.nextBtn.setVisible(True)
        self.nextBtn.setEnabled(False)
        self.submitBtn.setVisible(True)
        self.submitBtn.setEnabled(False)

        self.errAnswers = {}
        self.yourAnswers = {}
        self.isShowErrQuestion = False
        pass

    def hideQuestionArea(self):
        if self.isLayout:
            self.questionDescLabel.setText("")
            self.hideOptionBtn()
            self.answerLabel.setText("")
            self.solutionLabel.setText("")
            self.remarkLabel.setText("")
        pass

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
        self.startMockExamBtn.setEnabled(True)
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
        except Exception as err:
            LogUtil.e('mkDirs 错误信息：', err)
            self.examFilePath = None
            WidgetUtil.showErrorDialog(message="请选择正确的模拟考试的题库文件（按照指定规范提供）")
            return
        pass

    def prepareAnswerCard(self):
        totalQuestionNums = self.mockExamUtil.totalQuestionNums
        while self.answerCardGrid.count() > totalQuestionNums:
            layoutItem = self.answerCardGrid.itemAt(totalQuestionNums)
            widget = layoutItem.widget()
            self.answerCardGrid.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

        answerCardNum = self.answerCardGrid.count()
        if answerCardNum < totalQuestionNums:
            for no in range(answerCardNum + 1, totalQuestionNums + 1):
                btn = CustomPushButton(no)
                btn.setFixedSize(QSize(40, 25))
                btn.clicked.connect(self.answerCardClicked)
                self.answerCardGrid.addWidget(btn, (no - 1) // ANSWER_CARD_MAX_COL, (no - 1) % ANSWER_CARD_MAX_COL)
        pass

    def prepareLayout(self):
        if not self.questionDescLabel:
            self.questionDescLabel = WidgetUtil.createTextEdit(self.questionScrollAreaWidget, isReadOnly=True)
            self.questionDescLabel.setMinimumHeight(160)
            self.questionVBox.addWidget(self.questionDescLabel)

        if not self.oneChoiceGroup:
            self.oneChoiceOptionBtnList = []
            self.oneChoiceGroup = WidgetUtil.createButtonGroup(onToggled=self.oneChoiceToggled)
            for option in range(self.maxOptionNum + 1):
                radioButton = WidgetUtil.createRadioButton(self.questionScrollAreaWidget, isEnable=True)
                radioButton.setMinimumHeight(30)
                self.oneChoiceOptionBtnList.append(radioButton)
                self.oneChoiceGroup.addButton(radioButton, option)
                self.questionVBox.addWidget(radioButton)

        if not self.multiChoiceOptionBtnList:
            self.multiChoiceOptionBtnList = []
            # 必须是成员变量，本地变量不行，很奇怪
            self.multiChoiceGroup = WidgetUtil.createButtonGroup(onToggled=self.multiChoiceToggled)
            self.multiChoiceGroup.setExclusive(False)
            for option in range(self.maxOptionNum + 1):
                checkBox = WidgetUtil.createCheckBox(self.questionScrollAreaWidget)
                checkBox.setMinimumHeight(30)
                self.multiChoiceOptionBtnList.append(checkBox)
                self.multiChoiceGroup.addButton(checkBox, option)
                self.questionVBox.addWidget(checkBox)

        if not self.answerLabel:
            self.answerLabel = WidgetUtil.createLabel(self.questionScrollAreaWidget)
            self.questionVBox.addWidget(self.answerLabel)

        if not self.solutionLabel:
            self.solutionLabel = WidgetUtil.createLabel(self.questionScrollAreaWidget)
            self.questionVBox.addWidget(self.solutionLabel)

        if not self.remarkLabel:
            self.remarkLabel = WidgetUtil.createLabel(self.questionScrollAreaWidget)
            self.questionVBox.addWidget(self.remarkLabel)

        if not self.label:
            self.label = WidgetUtil.createLabel(self.questionScrollAreaWidget)
            self.label.setSizePolicy(WidgetUtil.createSizePolicy())
            self.questionVBox.addWidget(self.label)
        self.isLayout = True
        pass

    def startMockExam(self):
        LogUtil.e("startMockExam")
        self.genExamPaperByRealBtn.setEnabled(False)
        self.genExamPaperByAllBtn.setEnabled(False)
        self.startMockExamBtn.setEnabled(False)

        self.maxOptionNum = self.mockExamUtil.maxOptionNum()
        for no in range(1, self.mockExamUtil.totalQuestionNums + 1):
            self.errAnswers[no] = None
        # 准备答题卡
        self.prepareAnswerCard()
        # 准备考题布局
        self.prepareLayout()

        self.curQuestionNo = 1
        self.curQuestionObj = self.mockExamUtil.nextQuestion()
        self.renderQuestion(self.curQuestionObj, None)

        self.submitBtn.setEnabled(True)
        pass

    def restartMockExam(self):
        self.prepareMockExam()
        pass

    def updateChangeQuestionBtn(self):
        if self.isShowErrQuestion:
            self.preBtn.setEnabled(self.curErrQuestionIndex > 0)
            self.nextBtn.setEnabled(self.curErrQuestionIndex < len(self.reviewErrQuestionNoList) - 1)
        else:
            self.preBtn.setEnabled(self.mockExamUtil.hasPre())
            self.nextBtn.setEnabled(self.mockExamUtil.hasNext())

    def renderQuestion(self, questionObj, yourAnswer):
        self.questionDescLabel.setText(f"{questionObj[KEY_REAL_QUESTION_NO]}. " + questionObj[KEY_QUESTION])

        if questionObj[KEY_QUESTION_TYPE] == QUESTION_TYPE_MULTI_CHOICE:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.multiChoiceOptionBtnList)
        else:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.oneChoiceOptionBtnList)

        if self.isShowErrQuestion:
            self.answerLabel.setText(
                f'''<p style="color:#80ff00ff">正确答案：{questionObj[KEY_ANSWER]}</p><p style="color:#800000ff">您的选择：{yourAnswer if yourAnswer else ""}</p>''')
            if questionObj[KEY_SOLUTION]:
                self.solutionLabel.setText(f"解析：\n{questionObj[KEY_SOLUTION]}")
            else:
                self.solutionLabel.setText("")
            if questionObj[KEY_REMARK]:
                self.remarkLabel.setText(f"备注：\n{questionObj[KEY_REMARK]}")
            else:
                self.remarkLabel.setText("")
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
        for index, checkBox in enumerate(self.multiChoiceOptionBtnList):
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

    def hideOptionBtn(self):
        """
        隐藏所有的选项按钮
        """
        # 为了消除按钮选中状态
        self.oneChoiceGroup.setExclusive(False)
        for radioButton in self.oneChoiceOptionBtnList:
            radioButton.setVisible(False)
            radioButton.setChecked(False)
        self.oneChoiceGroup.setExclusive(True)

        for checkBox in self.multiChoiceOptionBtnList:
            checkBox.setVisible(False)
            checkBox.setChecked(False)
        pass

    def updateChoiceOptionBtn(self, questionObj, yourAnswer, choiceOptionBtnList):
        # 清除选项卡的状态
        self.hideOptionBtn()

        for optionIndex in range(self.maxOptionNum):
            optionX = chr(65 + optionIndex)
            optionDesc = questionObj[optionX]
            if optionDesc:
                choiceOptionBtnList[optionIndex].setText(f"{optionX}. {optionDesc}")
                choiceOptionBtnList[optionIndex].setVisible(True)
                choiceOptionBtnList[optionIndex].setEnabled(not self.isShowErrQuestion)
            else:
                break
        if yourAnswer:
            for optionX in yourAnswer:
                choiceOptionBtnList[ord(optionX) - 65].setChecked(True)
        pass

    def preQuestionFunc(self):
        LogUtil.d("preQuestionFunc")
        if self.isShowErrQuestion:
            self.preErrQuestion()
            yourAnswer = getDictData(self.curQuestionNo, self.errAnswers)
        else:
            self.curQuestionNo -= 1
            self.curQuestionObj = self.mockExamUtil.preQuestion()
            yourAnswer = getDictData(self.curQuestionNo, self.yourAnswers)
        self.renderQuestion(self.curQuestionObj, yourAnswer)
        return False

    def nextQuestionFunc(self):
        LogUtil.d("nextQuestionFunc")
        if self.isShowErrQuestion:
            self.nextErrQuestion()
            yourAnswer = getDictData(self.curQuestionNo, self.errAnswers)
        else:
            self.curQuestionNo += 1
            self.curQuestionObj = self.mockExamUtil.nextQuestion()
            yourAnswer = getDictData(self.curQuestionNo, self.yourAnswers)
        self.renderQuestion(self.curQuestionObj, yourAnswer)
        return False

    def answerCardClicked(self, no):
        LogUtil.d("answerCardClicked", no)
        pass

    def submitFunc(self):
        LogUtil.d("submitFunc")
        if len(self.yourAnswers) < self.mockExamUtil.totalQuestionNums:
            WidgetUtil.showQuestionDialog(
                message=f"您还有{self.mockExamUtil.totalQuestionNums - len(self.yourAnswers)}道题未做，确认提交？",
                acceptFunc=self.submitExam)
        else:
            self.submitExam()
        return False

    def showExamOverLayout(self):
        self.genExamPaperByRealBtn.setVisible(False)
        self.genExamPaperByAllBtn.setVisible(False)
        self.startMockExamBtn.setVisible(False)
        self.restartMockExamBtn.setVisible(True)

        self.hideQuestionArea()

        self.submitBtn.setVisible(False)
        pass

    def submitExam(self):
        self.showExamOverLayout()

        errNo, score = self.mockExamUtil.calculateResults(self.errAnswers)
        isPassExam = self.mockExamUtil.isPassExam(score)
        LogUtil.d("submitExam", "做错：", errNo, "分数：", score, "通过：", isPassExam)
        if errNo > 0:
            if isPassExam:
                WidgetUtil.showQuestionDialog(message=f"恭喜您通过本轮考试，获得 {score} 分的好成绩，是否查看结果分析？",
                                              acceptFunc=self.seeErrQuestions)
            else:
                WidgetUtil.showQuestionDialog(message=f"很遗憾您未能通过本轮考试，获得 {score} 分，是否查看结果分析？",
                                              acceptFunc=self.seeErrQuestions)

        else:
            WidgetUtil.showAboutDialog(text="恭喜您获得满分的成绩，下次再接再厉！！！")

    def seeErrQuestions(self):
        LogUtil.d("seeErrQuestions")
        self.isShowErrQuestion = True
        # 按照字典的键进行排序
        self.reviewErrQuestionNoList = sorted(self.errAnswers.keys())
        self.curErrQuestionIndex = 0
        self.getErrQuestionObj()
        self.renderQuestion(self.curQuestionObj, self.errAnswers[self.curQuestionNo])
        LogUtil.d("seeErrQuestions", self.reviewErrQuestionNoList, self.curQuestionNo, self.curQuestionObj)
        pass

    def getErrQuestionObj(self):
        self.curQuestionNo = self.reviewErrQuestionNoList[self.curErrQuestionIndex]
        self.curQuestionObj = self.mockExamUtil.getQuestion(self.curQuestionNo - 1)
        pass

    def preErrQuestion(self):
        if self.curErrQuestionIndex < 1:
            return None
        self.curErrQuestionIndex -= 1
        self.getErrQuestionObj()

    def nextErrQuestion(self):
        if self.curErrQuestionIndex >= len(self.reviewErrQuestionNoList) - 1:
            return None
        self.curErrQuestionIndex += 1
        self.getErrQuestionObj()


class CustomPushButton(QPushButton):
    def __init__(self, no):
        QWidget.__init__(self)
        self.no = no
        self.setText(str(no))

    clicked = pyqtSignal(int)

    def mousePressEvent(self, ev: QMouseEvent):
        LogUtil.d('mousePressEvent')
        if ev.button() == Qt.LeftButton:
            # 鼠标左击
            self.clicked.emit(self.no)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockExamDialog()
    window.show()
    sys.exit(app.exec_())
