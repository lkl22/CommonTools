# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamDialog.py
# 定义一个MockExamDialog类实现考试刷题
import random

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QScrollArea, QPushButton, QAbstractButton
from util.DialogUtil import *
from util.OperaIni import *
from widget.custom.ChoiceButton import ChoiceButton
from widget.mockExam.Word2Excel import *
from widget.mockExam.Excel2Word import *

OPTION_CHAR = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ANSWER_CARD_MAX_COL = 20
TAG = "MockExamDialog"


def delDictData(key, dicts):
    if key in dicts:
        del dicts[key]
    pass


def getDictData(key, dicts):
    if key in dicts:
        return dicts[key]
    return None


class MockExamDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        MockExamDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        MockExamDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Mock Exam Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="模拟考试"))

        self.examFilePath = None
        self.mockExamUtil = None

        self.genExamPaperByRealBtn = None
        self.genExamPaperByAllBtn = None
        self.startMockExamBtn = None
        self.restartMockExamBtn = None
        self.examInfoLabel = None
        self.examTime = None
        self.timerLabel = None
        self.timer = None

        self.questionDescLabel = None
        self.oneChoiceGroup = None
        self.choiceBtnList = None
        self.answerLabel = None
        self.solutionLabel = None
        self.remarkLabel = None
        self.label = None

        self.curQuestionObj = None
        self.curQuestionNo = 1
        self.isAllMock = False

        self.yourAnswers = {}
        self.errAnswers = {}
        self.realOptionsDict = {}
        self.realAnswerDict = {}
        self.isShowErrQuestion = False
        self.isLayout = False

        self.setObjectName("MockExamDialog")
        self.resize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)
        # self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        hbox = WidgetUtil.createHBoxLayout()
        self.word2ExcelToolBtn = WidgetUtil.createPushButton(self, text="显示Word转Excel工具",
                                                             onClicked=self.toggledWord2ExcelTool)
        hbox.addWidget(self.word2ExcelToolBtn)
        self.excel2WordToolBtn = WidgetUtil.createPushButton(self, text="显示Excel转Word工具",
                                                             onClicked=self.toggledExcel2WordTool)
        hbox.addWidget(self.excel2WordToolBtn)
        vLayout.addLayout(hbox)

        self.word2ExcelGroupBox = self.createWord2ExcelGroupBox(self)
        vLayout.addWidget(self.word2ExcelGroupBox)

        self.excel2WordGroupBox = self.createExcel2WordGroupBox(self)
        vLayout.addWidget(self.excel2WordGroupBox)

        mockExamGroupBox = self.createGenMockExamGroupBox(self)
        vLayout.addWidget(mockExamGroupBox)

        answerCardArea = self.createAnswerCardArea()
        vLayout.addWidget(answerCardArea)

        questionArea = self.createQuestionArea()
        vLayout.addWidget(questionArea)

        btnBox = WidgetUtil.createDialogButtonBox(standardButton=QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Ignore,
                                                  parent=self,
                                                  clickedFunc=self.clickedFunc)
        self.preBtn = btnBox.button(QDialogButtonBox.Ignore if PlatformUtil.isMac() else QDialogButtonBox.Ok)
        self.nextBtn = btnBox.button(QDialogButtonBox.Cancel if PlatformUtil.isMac() else QDialogButtonBox.Ignore)
        self.submitBtn = btnBox.button(QDialogButtonBox.Ok if PlatformUtil.isMac() else QDialogButtonBox.Cancel)
        self.preBtn.setText("上一题")
        self.nextBtn.setText("下一题")
        self.submitBtn.setText("交卷")
        vLayout.addWidget(btnBox)

        self.prepareMockExam()
        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def closeEvent(self, event):
        LogUtil.d(TAG, "MockExamDialog", "closeEvent")
        if self.mockExamUtil:
            self.mockExamUtil.close()
        pass

    def createWord2ExcelGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="将Word题库转化为Excel格式")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="选择题库模版（Word）", minSize=QSize(120, const.HEIGHT),
                                                   onClicked=self.getWordExamFilePath))
        self.wordExamFilePathLineEdit = WidgetUtil.createLineEdit(box, text="", isEnable=False)
        hbox.addWidget(self.wordExamFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="选择Excal文件保存路径", minSize=QSize(120, const.HEIGHT),
                                                   onClicked=self.getSaveExcelExamFilePath))
        self.saveExcelExamFilePathLineEdit = WidgetUtil.createLineEdit(box,
                                                                       holderText="请输入要保存的文件路径，默认应用程序当前目录下的(题库.xlsx)文件")
        hbox.addWidget(self.saveExcelExamFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="设置科目名称：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.examNameLineEdit = WidgetUtil.createLineEdit(box)
        hbox.addWidget(self.examNameLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="设置通过分数线：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.scoreLineSpinBox = WidgetUtil.createSpinBox(box, value=80, minValue=50, maxValue=100, step=5, suffix="%")
        hbox.addWidget(self.scoreLineSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="设置考试时长：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.examTimeSpinBox = WidgetUtil.createSpinBox(box, value=90, minValue=50, maxValue=180, step=10, suffix="分钟")
        hbox.addWidget(self.examTimeSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="判断题分值：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.judgmentScoreSpinBox = WidgetUtil.createSpinBox(box, value=2, minValue=1, maxValue=20, step=1, suffix="分")
        hbox.addWidget(self.judgmentScoreSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="单选题分值：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.oneChoiceScoreSpinBox = WidgetUtil.createSpinBox(box, value=3, minValue=1, maxValue=20, step=1, suffix="分")
        hbox.addWidget(self.oneChoiceScoreSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="多选题分值：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.multiChoiceScoreSpinBox = WidgetUtil.createSpinBox(box, value=5, minValue=1, maxValue=20, step=1,
                                                                suffix="分")
        hbox.addWidget(self.multiChoiceScoreSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="判断题个数：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.judgmentNumsSpinBox = WidgetUtil.createSpinBox(box, value=10, minValue=1, maxValue=50, step=5, suffix="道题")
        hbox.addWidget(self.judgmentNumsSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="单选题个数：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.oneChoiceNumsSpinBox = WidgetUtil.createSpinBox(box, value=10, minValue=1, maxValue=50, step=5,
                                                             suffix="道题")
        hbox.addWidget(self.oneChoiceNumsSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="多选题个数：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.multiChoiceNumsSpinBox = WidgetUtil.createSpinBox(box, value=5, minValue=1, maxValue=50, step=5,
                                                               suffix="道题")
        hbox.addWidget(self.multiChoiceNumsSpinBox)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.startWord2ExcelBtn = WidgetUtil.createPushButton(box, text="转换题库", onClicked=self.startWord2Excel)
        hbox.addWidget(self.startWord2ExcelBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        box.setVisible(False)
        return box

    def toggledWord2ExcelTool(self):
        self.word2ExcelGroupBox.setVisible(not self.word2ExcelGroupBox.isVisible())
        if self.word2ExcelGroupBox.isVisible():
            self.excel2WordGroupBox.setVisible(False)
        self.word2ExcelToolBtn.setText(f"{'隐藏' if self.word2ExcelGroupBox.isVisible() else '显示'}Word转Excel工具")
        self.excel2WordToolBtn.setText(f"{'隐藏' if self.excel2WordGroupBox.isVisible() else '显示'}Excel转Word工具")
        pass

    def startWord2Excel(self):
        wordFp = self.wordExamFilePathLineEdit.text().strip()
        if not wordFp:
            WidgetUtil.showErrorDialog(message="请优先选择您的Word题库文件")
            return
        examName = self.examNameLineEdit.text().strip()
        if not examName:
            WidgetUtil.showErrorDialog(message="请输入考试科目名称")
            return
        self.startWord2ExcelBtn.setEnabled(False)
        scoreLine = self.scoreLineSpinBox.value()
        examTime = self.examTimeSpinBox.value()
        judgmentScore = self.judgmentScoreSpinBox.value()
        judgmentNums = self.judgmentNumsSpinBox.value()
        oneChoiceScore = self.oneChoiceScoreSpinBox.value()
        oneChoiceNums = self.oneChoiceNumsSpinBox.value()
        multiChoiceScore = self.multiChoiceScoreSpinBox.value()
        multiChoiceNums = self.multiChoiceNumsSpinBox.value()

        excelExamFp = self.saveExcelExamFilePathLineEdit.text().strip()
        if not excelExamFp:
            excelExamFp = "题库.xlsx"
        if not excelExamFp.endswith(".xlsx"):
            FileUtil.mkFilePath(excelExamFp)
            excelExamFp = os.path.join(excelExamFp, "题库.xlsx")
        LogUtil.d(TAG, "Word题库路径", wordFp, "\n保存路径", excelExamFp, "\n科目名称", examName, "scoreLine", scoreLine,
                  "考试时长", examTime, "\n判断题分值", judgmentScore, "判断题个数", judgmentNums, "\n单选题分值", oneChoiceScore,
                  "单选题个数", oneChoiceNums, "\n多选题分值", multiChoiceScore, "多选题个数", multiChoiceNums)
        try:
            Word2Excel(wordFp, excelExamFp, {
                "examNam": examName, "scoreLine": scoreLine, "examTime": examTime, "judgmentNums": judgmentNums,
                "judgmentScore": judgmentScore,
                "oneChoiceNums": oneChoiceNums, "oneChoiceScore": oneChoiceScore, "multiChoiceNums": multiChoiceNums,
                "multiChoiceScore": multiChoiceScore
            })
        except Exception as e:
            LogUtil.e(TAG, 'Word2Excel init 错误信息：', e)
            WidgetUtil.showErrorDialog(message="请选择正确格式的题库文档")
        self.startWord2ExcelBtn.setEnabled(True)
        LogUtil.d(TAG, "Word2Excel finished.")
        pass

    def createExcel2WordGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="将Excel题库转化为Word格式")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="选择题库模版（Excel）", minSize=QSize(120, const.HEIGHT),
                                                   onClicked=self.getExcelExamFilePath))
        self.excelExamFilePathLineEdit = WidgetUtil.createLineEdit(box, text="", isEnable=False)
        hbox.addWidget(self.excelExamFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="选择Word文件保存路径", minSize=QSize(120, const.HEIGHT),
                                                   onClicked=self.getSaveWordExamFilePath))
        self.saveWordExamFilePathLineEdit = WidgetUtil.createLineEdit(box,
                                                                      holderText="请输入要保存的文件路径，默认应用程序当前目录下的(题库.docx)文件")
        hbox.addWidget(self.saveWordExamFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.startExcel2WordByRealBtn = WidgetUtil.createPushButton(box, text="生成真实模拟考卷",
                                                                    onClicked=self.startExcel2WordByReal)
        hbox.addWidget(self.startExcel2WordByRealBtn)
        self.startExcel2WordByAllBtn = WidgetUtil.createPushButton(box, text="生成全量模拟考卷",
                                                                   onClicked=self.startExcel2WordByAll)
        hbox.addWidget(self.startExcel2WordByAllBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        box.setVisible(False)
        return box

    def toggledExcel2WordTool(self):
        self.excel2WordGroupBox.setVisible(not self.excel2WordGroupBox.isVisible())
        if self.excel2WordGroupBox.isVisible():
            self.word2ExcelGroupBox.setVisible(False)
        self.excel2WordToolBtn.setText(f"{'隐藏' if self.excel2WordGroupBox.isVisible() else '显示'}Excel转Word工具")
        self.word2ExcelToolBtn.setText(f"{'隐藏' if self.word2ExcelGroupBox.isVisible() else '显示'}Word转Excel工具")
        pass

    def getExcelExamFilePath(self):
        fn = WidgetUtil.getOpenFileName(caption='选择模拟考试题库Excel文件', filter='*.xlsx', initialFilter='*.xlsx')
        if fn:
            self.excelExamFilePathLineEdit.setText(fn)
        pass

    def getSaveWordExamFilePath(self):
        fp = WidgetUtil.getExistingDirectory(caption='选择模拟考试题库Word文件保存路径', directory="./")
        if fp:
            self.saveWordExamFilePathLineEdit.setText(fp)
        pass

    def startExcel2WordByReal(self):
        self.startExcel2Word(False)
        pass

    def startExcel2WordByAll(self):
        self.startExcel2Word(True)
        pass

    def startExcel2Word(self, isAllMock):
        LogUtil.d(TAG, "startExcel2Word", isAllMock)
        excelFp = self.excelExamFilePathLineEdit.text().strip()
        if not excelFp:
            WidgetUtil.showErrorDialog(message="请优先选择您的Excel题库文件")
            return

        wordExamFp = self.saveWordExamFilePathLineEdit.text().strip()
        if not wordExamFp:
            wordExamFp = "题库.docx"
        if not wordExamFp.endswith(".docx"):
            FileUtil.mkFilePath(wordExamFp)
            wordExamFp = os.path.join(wordExamFp, "题库.docx")

        self.startExcel2WordByRealBtn.setEnabled(False)
        self.startExcel2WordByAllBtn.setEnabled(False)
        Excel2Word.genWord(excelFp, wordExamFp, isAllMock)
        self.startExcel2WordByRealBtn.setEnabled(True)
        self.startExcel2WordByAllBtn.setEnabled(True)
        LogUtil.d(TAG, "startExcel2Word", "finished.")
        pass

    def createGenMockExamGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")

        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="选择题库模版", minSize=QSize(120, const.HEIGHT),
                                                   onClicked=self.getExamFilePath))
        self.examFilePathLineEdit = WidgetUtil.createLineEdit(box,
                                                              text="/Users/likunlun/PycharmProjects/CommonTools/resources/mockExam/题库模版.xlsx",
                                                              isEnable=False)
        hbox.addWidget(self.examFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.genExamPaperByRealBtn = WidgetUtil.createPushButton(box, text="生成试卷",
                                                                 onClicked=self.genExamPaperByReal)
        hbox.addWidget(self.genExamPaperByRealBtn)
        self.genExamPaperByAllBtn = WidgetUtil.createPushButton(box, text="全量模拟", onClicked=self.genExamPaperByAll)
        hbox.addWidget(self.genExamPaperByAllBtn)
        self.startMockExamBtn = WidgetUtil.createPushButton(box, text="开始", isEnable=False,
                                                            onClicked=self.startMockExam)
        hbox.addWidget(self.startMockExamBtn)
        self.restartMockExamBtn = WidgetUtil.createPushButton(box, text="重新开始", onClicked=self.restartMockExam)
        hbox.addWidget(self.restartMockExamBtn)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.examInfoLabel = WidgetUtil.createLabel(box, text="")
        hbox.addWidget(self.examInfoLabel)
        self.timerLabel = WidgetUtil.createLabel(box, text="", alignment=Qt.AlignVCenter | Qt.AlignRight)
        hbox.addWidget(self.timerLabel)
        vbox.addLayout(hbox)
        return box

    def createAnswerCardArea(self):
        self.answerCardScrollAres = QScrollArea(self)
        self.answerCardScrollAres.setWidgetResizable(True)

        self.answerCardScrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')
        self.answerCardScrollAres.setMaximumHeight(60)
        self.answerCardGrid = QtWidgets.QGridLayout(self.answerCardScrollAreaWidget)
        # 设置间距
        self.answerCardGrid.setSpacing(const.PADDING * 2)
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
        self.examInfoLabel.setText("")
        self.timerLabel.setText("")
        self.stopTimer()

        self.hideAnswerCard()
        self.hideQuestionArea()

        self.preBtn.setVisible(True)
        self.preBtn.setEnabled(False)
        self.nextBtn.setVisible(True)
        self.nextBtn.setEnabled(False)
        self.submitBtn.setVisible(True)
        self.submitBtn.setEnabled(False)

        self.errAnswers = {}
        self.yourAnswers = {}
        self.realOptionsDict = {}
        self.realAnswerDict = {}
        self.isAllMock = False
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

    def getWordExamFilePath(self):
        fn = WidgetUtil.getOpenFileName(caption='选择模拟考试题库Word文件', filter='*.docx', initialFilter='*.docx')
        if fn:
            self.wordExamFilePathLineEdit.setText(fn)
        pass

    def getSaveExcelExamFilePath(self):
        fp = WidgetUtil.getExistingDirectory(caption='选择模拟考试题库Excel文件保存路径', directory="./")
        if fp:
            self.saveExcelExamFilePathLineEdit.setText(fp)
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

    def genExamPaperMethod(self, isAllMock):
        self.isAllMock = isAllMock
        if isAllMock:
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
            LogUtil.e(TAG, 'genExamPaper 错误信息：', err)
            self.examFilePath = None
            WidgetUtil.showErrorDialog(message="请选择正确的模拟考试的题库文件（按照指定规范提供）")
            return
        pass

    def updateAnswerCardColor(self, index, color="grey"):
        if 0 <= index < self.answerCardGrid.count():
            self.answerCardGrid.itemAt(index).widget().setStyleSheet(f"background: {color};")  # 设置背景色
        pass

    def resetAnswerCardStatus(self):
        for index in range(self.answerCardGrid.count()):
            widget = self.answerCardGrid.itemAt(index).widget()
            widget.setStyleSheet(f"background: grey;")  # 设置背景色
            widget.setEnabled(True)
            widget.setVisible(True)
        pass

    def hideAnswerCard(self):
        for index in range(self.answerCardGrid.count()):
            widget = self.answerCardGrid.itemAt(index).widget()
            widget.setVisible(False)
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
                btn.setFixedSize(QSize(36, 20))
                btn.clicked.connect(self.answerCardClicked)
                self.answerCardGrid.addWidget(btn, (no - 1) // ANSWER_CARD_MAX_COL, (no - 1) % ANSWER_CARD_MAX_COL)

        self.resetAnswerCardStatus()
        pass

    def prepareLayout(self):
        if not self.questionDescLabel:
            self.questionDescLabel = WidgetUtil.createTextEdit(self.questionScrollAreaWidget, isReadOnly=True)
            self.questionDescLabel.setMinimumHeight(160)
            self.questionVBox.addWidget(self.questionDescLabel)

        if not self.choiceBtnList:
            self.choiceBtnList = []
            self.oneChoiceGroup = WidgetUtil.createButtonGroup()
            multiChoiceGroup = WidgetUtil.createButtonGroup()
            multiChoiceGroup.setExclusive(False)
            for option in range(self.maxOptionNum + 1):
                choiceButton = ChoiceButton(f"{OPTION_CHAR[option]}.", "", option, onToggled=self.choiceButtonToggled)
                self.choiceBtnList.append(choiceButton)
                self.oneChoiceGroup.addButton(choiceButton.getButton(ChoiceButton.Radio), option)
                multiChoiceGroup.addButton(choiceButton.getButton(ChoiceButton.CheckBox), option)
                self.questionVBox.addWidget(choiceButton)

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
        LogUtil.e(TAG, "startMockExam")
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
        self.curQuestionObj = self.mockExamUtil.getQuestion(0)
        self.renderQuestion(self.curQuestionObj, None)
        self.examTime = self.mockExamUtil.examTime * 60
        judgmentNum = self.mockExamUtil.realJudgmentRequestNum
        oneChoiceNum = self.mockExamUtil.realOneChoiceRequestNum
        multiChoiceNum = self.mockExamUtil.realMultiChoiceRequestNum

        self.examInfoLabel.setText(
            f'''本轮考试<span style='color:red;'>{"" if self.isAllMock else f"时长{self.mockExamUtil.examTime}分钟，"
            }</span>总共有 <span style='color:red;'>{self.mockExamUtil.totalQuestionNums}</span> 道题（{
            f"<span style='color:red;'>{judgmentNum}</span> 道判断题" if judgmentNum > 0 else ''} {
            f"<span style='color:red;'>{oneChoiceNum}</span> 道单选题" if oneChoiceNum > 0 else ''} {
            f"<span style='color:red;'>{multiChoiceNum}</span> 道多选题" if multiChoiceNum > 0 else ''}）''')
        self.submitBtn.setEnabled(True)
        if not self.isAllMock:
            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.refreshTimer)
            self.timer.start()
        pass

    def restartMockExam(self):
        self.prepareMockExam()
        pass

    def updateChangeQuestionBtn(self):
        self.preBtn.setEnabled(self.curQuestionNo > 1)
        self.nextBtn.setEnabled(self.curQuestionNo < self.mockExamUtil.totalQuestionNums)

    def renderQuestion(self, questionObj, yourAnswer):
        self.questionDescLabel.setText(f"{questionObj[KEY_REAL_QUESTION_NO]}. " + questionObj[KEY_QUESTION])

        if questionObj[KEY_QUESTION_TYPE] == QUESTION_TYPE_MULTI_CHOICE:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.choiceBtnList, ChoiceButton.CheckBox)
        else:
            self.updateChoiceOptionBtn(questionObj, yourAnswer, self.choiceBtnList, ChoiceButton.Radio)

        if self.isShowErrQuestion:
            self.answerLabel.setText(
                f'''<p style="color:#80ff00ff">正确答案：{self.realAnswerDict[questionObj[KEY_REAL_QUESTION_NO]]}</p><p style="color:#800000ff">您的选择：{yourAnswer if yourAnswer else ""}</p>''')
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

    def choiceButtonToggled(self, id):
        LogUtil.d(TAG, "choiceButtonToggled", id)
        if self.choiceBtnList[id].getMode() == ChoiceButton.Radio:
            self.oneChoiceToggled(id)
        else:
            self.multiChoiceToggled()
        pass

    def oneChoiceToggled(self, id):
        option = OPTION_CHAR[id]
        self.yourAnswers[self.curQuestionNo] = option
        if option in self.realAnswerDict[self.curQuestionNo]:
            delDictData(self.curQuestionNo, self.errAnswers)
        else:
            self.errAnswers[self.curQuestionNo] = option
        self.updateAnswerCardColor(self.curQuestionNo - 1, "green")
        LogUtil.e(TAG, "oneChoiceToggled", self.yourAnswers, self.errAnswers)
        pass

    def multiChoiceToggled(self):
        LogUtil.e(TAG, "multiChoiceToggled")
        checkedOptions = []
        for index, checkBox in enumerate(self.choiceBtnList):
            if checkBox.isChecked():
                checkedOptions.append(OPTION_CHAR[index])

        if len(checkedOptions) > 0:
            self.yourAnswers[self.curQuestionNo] = checkedOptions
            self.errAnswers[self.curQuestionNo] = checkedOptions
            if len(checkedOptions) == len(self.realAnswerDict[self.curQuestionNo]):
                isCorrect = True
                for correctAnswer in self.realAnswerDict[self.curQuestionNo]:
                    if correctAnswer not in checkedOptions:
                        isCorrect = False
                        break
                if isCorrect:
                    delDictData(self.curQuestionNo, self.errAnswers)
            self.updateAnswerCardColor(self.curQuestionNo - 1, "green")
        else:
            # 多选没有选择
            self.errAnswers[self.curQuestionNo] = None
            delDictData(self.curQuestionNo, self.yourAnswers)
            self.updateAnswerCardColor(self.curQuestionNo - 1)
        LogUtil.e(TAG, "multiChoiceToggled", self.yourAnswers, self.errAnswers)
        pass

    def hideOptionBtn(self):
        """
        隐藏所有的选项按钮
        """
        # 为了消除按钮选中状态
        self.oneChoiceGroup.setExclusive(False)
        for choiceButton in self.choiceBtnList:
            choiceButton.setVisible(False)
            choiceButton.setChecked(False)
        self.oneChoiceGroup.setExclusive(True)
        pass

    def updateChoiceOptionBtn(self, questionObj, yourAnswer, choiceOptionBtnList, mode: ChoiceButton.Mode):
        # 清除选项卡的状态
        self.hideOptionBtn()
        realAnswer = getDictData(questionObj[KEY_REAL_QUESTION_NO], self.realAnswerDict)
        realOptions = getDictData(questionObj[KEY_REAL_QUESTION_NO], self.realOptionsDict)
        if not realOptions:
            realAnswer = []
            realOptions = []
            for optionIndex in range(self.maxOptionNum):
                optionX = chr(65 + optionIndex)
                optionDesc = questionObj[optionX]
                if optionDesc:
                    realOptions.append(optionX)
                else:
                    break
            realOptions = random.sample(realOptions, len(realOptions))
            for index, option in enumerate(realOptions):
                if option in questionObj[KEY_ANSWER]:
                    realAnswer.append(OPTION_CHAR[index])
            self.realOptionsDict[questionObj[KEY_REAL_QUESTION_NO]] = realOptions
            self.realAnswerDict[questionObj[KEY_REAL_QUESTION_NO]] = realAnswer
        for index, option in enumerate(realOptions):
            optionDesc = questionObj[option]
            choiceOptionBtnList[index].setMode(mode)
            choiceOptionBtnList[index].setText(text=optionDesc)
            choiceOptionBtnList[index].setVisible(True)
            choiceOptionBtnList[index].setEnabled(not self.isShowErrQuestion)

        if yourAnswer:
            for optionX in yourAnswer:
                choiceOptionBtnList[ord(optionX) - 65].setChecked(True)
        pass

    def clickedFunc(self, btn: QAbstractButton):
        LogUtil.d(TAG, "clickedFunc", btn.text())
        if btn == self.preBtn:
            self.preQuestionFunc()
        elif btn == self.nextBtn:
            self.nextQuestionFunc()
        elif btn == self.submitBtn:
            self.submitFunc()
        pass

    def preQuestionFunc(self):
        LogUtil.d(TAG, "preQuestionFunc")
        if self.curQuestionNo < 2:
            return False
        self.curQuestionNo -= 1
        self.curQuestionObj = self.mockExamUtil.getQuestion(self.curQuestionNo - 1)
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        return False

    def nextQuestionFunc(self):
        LogUtil.d(TAG, "nextQuestionFunc")
        if self.curQuestionNo >= self.mockExamUtil.totalQuestionNums:
            return False
        self.curQuestionNo += 1
        self.curQuestionObj = self.mockExamUtil.getQuestion(self.curQuestionNo - 1)
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        return False

    def answerCardClicked(self, no):
        LogUtil.d(TAG, "answerCardClicked", no)
        self.curQuestionNo = no
        self.curQuestionObj = self.mockExamUtil.getQuestion(no - 1)
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        pass

    def submitFunc(self):
        LogUtil.d(TAG, "submitFunc")
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
        self.stopTimer()
        self.showExamOverLayout()

        errNo, score = self.mockExamUtil.calculateResults(self.errAnswers)
        isPassExam = self.mockExamUtil.isPassExam(score)
        LogUtil.d(TAG, "submitExam", "做错：", errNo, "分数：", score, "通过：", isPassExam)
        if errNo > 0:
            if isPassExam:
                WidgetUtil.showQuestionDialog(message=f"恭喜您通过本轮考试，获得 {score} 分的好成绩，是否查看结果分析？",
                                              acceptFunc=self.seeErrQuestions)
            else:
                WidgetUtil.showQuestionDialog(message=f"很遗憾您未能通过本轮考试，获得 {score} 分，是否查看结果分析？",
                                              acceptFunc=self.seeErrQuestions)

        else:
            WidgetUtil.showQuestionDialog(message="恭喜您获得满分的成绩，下次再接再厉！！！是否查看结果分析？",
                                          acceptFunc=self.seeErrQuestions)

    def seeErrQuestions(self):
        LogUtil.d(TAG, "seeErrQuestions")
        self.isShowErrQuestion = True
        self.curQuestionNo = 1
        self.curQuestionObj = self.mockExamUtil.getQuestion(0)
        self.renderQuestion(self.curQuestionObj, getDictData(self.curQuestionNo, self.yourAnswers))
        self.reviewAnswerCardUpdate()
        pass

    def reviewAnswerCardUpdate(self):
        for index in range(self.answerCardGrid.count()):
            widget = self.answerCardGrid.itemAt(index).widget()
            if index + 1 in self.errAnswers:
                widget.setStyleSheet(f"background: red;")
            else:
                widget.setStyleSheet(f"background: green;")
        pass

    def refreshTimer(self):
        if self.examTime > 0:
            minute = self.examTime // 60
            second = self.examTime % 60
            if self.examTime < 600:
                self.timerLabel.setText(
                    f'''还有最后 <span style="color:red;">{f"{minute} 分钟" if minute > 0 else ''} {f"{second} 秒" if second > 0 else ''}</span>''')
            else:
                self.timerLabel.setText(
                    f'''<span style="color:red;">{f"{minute} 分钟" if minute > 0 else ''} {f"{second} 秒" if second > 0 else ''}</span> 后考试结束''')
            self.examTime -= 1
        else:
            self.timerLabel.setText("")
            self.submitExam()
        pass

    def stopTimer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        pass


class CustomPushButton(QPushButton):
    def __init__(self, no):
        QWidget.__init__(self)
        self.no = no
        self.setText(str(no))

    clicked = pyqtSignal(int)

    def mousePressEvent(self, ev: QMouseEvent):
        LogUtil.d(TAG, 'mousePressEvent')
        if ev.button() == Qt.LeftButton:
            # 鼠标左击
            self.clicked.emit(self.no)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockExamDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
