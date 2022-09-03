# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamUtil.py
# 定义一个MockExamUtil工具类处理模拟考试相关逻辑

from openpyxl.worksheet.worksheet import Worksheet

from util.LogUtil import LogUtil
from util.OpenpyxlUtil import OpenpyxlUtil
from util.RandomUtil import RandomUtil

QUESTION_TYPE_JUDGMENT = "judgment"
QUESTION_TYPE_ONE_CHOICE = "oneChoice"
QUESTION_TYPE_MULTI_CHOICE = "multiChoice"

KEY_ROW = "row"
KEY_REAL_QUESTION_NO = "realQuestionNo"
KEY_QUESTION_TYPE = "questionType"
KEY_QUESTION = "question"
KEY_ANSWER = "answer"
KEY_REMARK = "remark"
KEY_SOLUTION = "solution"


def getRequest(st: Worksheet, row=2, colNum=12, realQuestionNo=1, questionType=QUESTION_TYPE_JUDGMENT):
    request = {
        KEY_ROW: row,
        KEY_REAL_QUESTION_NO: realQuestionNo,
        KEY_QUESTION_TYPE: questionType,
        KEY_QUESTION: OpenpyxlUtil.getCell(st, row, 1),
        KEY_ANSWER: OpenpyxlUtil.getCell(st, row, 2),
        KEY_REMARK: OpenpyxlUtil.getCell(st, row, 3),
        KEY_SOLUTION: OpenpyxlUtil.getCell(st, row, 4)
    }
    for col in range(5, colNum + 1):
        request[chr(65 + col - 5)] = OpenpyxlUtil.getCell(st, row, col)
    return request


class MockExamUtil:
    def __init__(self, fp='../resources/mockExam/题库模版.xlsx'):
        # 考试题目文件路径
        self.examFile = fp
        self.bk = OpenpyxlUtil.getBook(fp)
        self.infoSheet = OpenpyxlUtil.getSheet(self.bk, '考试信息')
        self.judgmentSheet = OpenpyxlUtil.getSheet(self.bk, '判断题')
        self.oneChoiceSheet = OpenpyxlUtil.getSheet(self.bk, '单选题')
        self.multipleChoiceSheet = OpenpyxlUtil.getSheet(self.bk, '多选题')
        self.examName = OpenpyxlUtil.getCell(self.infoSheet, 2, 1)
        self.scoreLine = OpenpyxlUtil.getCell(self.infoSheet, 2, 2)
        self.examTime = OpenpyxlUtil.getCell(self.infoSheet, 2, 3)

        self.judgmentNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 4)
        self.judgmentScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 5)
        self.judgmentRequestBankNums = OpenpyxlUtil.getRows(self.judgmentSheet)

        self.oneChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 6)
        self.oneChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 7)
        self.oneChoiceRequestBankNums = OpenpyxlUtil.getRows(self.oneChoiceSheet)

        self.multiChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 8)
        self.multiChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 9)
        self.multiChoiceRequestBankNums = OpenpyxlUtil.getRows(self.multipleChoiceSheet)

        self.maxCol = OpenpyxlUtil.getColumns(self.oneChoiceSheet)

        LogUtil.w("MockExamUtil", "考试科目：", self.examName, "分数线：", self.scoreLine, "考试时长：", self.examTime, "最大列数：", self.maxCol,
                  "\n判断题个数", self.judgmentNums, "\t判断题分值", self.judgmentScore, "\t判断题题库", self.judgmentRequestBankNums,
                  "\n单选题个数", self.oneChoiceNums, "\t单选题分值", self.oneChoiceScore, "\t单选题题库",
                  self.oneChoiceRequestBankNums, "\n多选题个数", self.multiChoiceNums, "\t多选题分值",
                  self.multiChoiceScore, "\t多选题题库", self.multiChoiceRequestBankNums)

    def genExamPaperByReal(self):
        self.genExamPaper(self.judgmentNums, self.oneChoiceNums, self.multiChoiceNums)
        pass

    def genExamPaperByAll(self):
        self.genExamPaper(self.judgmentRequestBankNums, self.oneChoiceRequestBankNums,
                          self.multiChoiceRequestBankNums)
        pass

    def genExamPaper(self, judgmentNums, oneChoiceNums, multipleChoiceNums):
        self.judgmentRequestRows = []
        if self.judgmentRequestBankNums > 1 and judgmentNums > 0:
            self.judgmentRequestRows = RandomUtil.sample(judgmentNums, 2, self.judgmentRequestBankNums)
        self.realJudgmentRequestNum = len(self.judgmentRequestRows)

        self.oneChoiceRequestRows = []
        if self.oneChoiceRequestBankNums > 1 and oneChoiceNums > 0:
            self.oneChoiceRequestRows = RandomUtil.sample(oneChoiceNums, 2, self.oneChoiceRequestBankNums)
        self.realOneChoiceRequestNum = len(self.oneChoiceRequestRows)

        self.multipleChoiceRequestRows = []
        if self.multiChoiceRequestBankNums > 1 and multipleChoiceNums > 0:
            self.multipleChoiceRequestRows = RandomUtil.sample(multipleChoiceNums, 2,
                                                               self.multiChoiceRequestBankNums)
        self.realMultipleChoiceRequestNum = len(self.multipleChoiceRequestRows)

        self.totalQuestionNums = self.realJudgmentRequestNum + self.realOneChoiceRequestNum + self.realMultipleChoiceRequestNum
        self.totalScore = self.judgmentScore * self.realJudgmentRequestNum + self.oneChoiceScore * self.realOneChoiceRequestNum + \
                          self.multiChoiceScore * self.realMultipleChoiceRequestNum
        LogUtil.w("MockExamUtil genExamPaper:", "\n判断题题号：", self.judgmentRequestRows, self.realJudgmentRequestNum,
                  "\n单选题题号：", self.oneChoiceRequestRows, self.realOneChoiceRequestNum, "\n多选题题号：",
                  self.multipleChoiceRequestRows, self.realMultipleChoiceRequestNum, "\n总题数：", self.totalQuestionNums,
                  "总分数：", self.totalScore)
        pass

    def getQuestion(self, index):
        """
        获取考题信息
        :param index: 考题下标索引，[0, totalQuestionNums)
        :return: 考题信息
        """
        if index < self.realJudgmentRequestNum:
            result = getRequest(self.judgmentSheet, self.judgmentRequestRows[index], self.maxCol, index + 1)
        elif index < self.realJudgmentRequestNum + self.realOneChoiceRequestNum:
            result = getRequest(self.oneChoiceSheet, self.oneChoiceRequestRows[index - self.realJudgmentRequestNum],
                                self.maxCol, index + 1, QUESTION_TYPE_ONE_CHOICE)
        else:
            result = getRequest(self.multipleChoiceSheet,
                                self.multipleChoiceRequestRows[index - self.totalQuestionNums],
                                self.maxCol, index + 1, QUESTION_TYPE_MULTI_CHOICE)
        return result

    def maxOptionNum(self):
        return self.maxCol - 4

    def calculateResults(self, errAnswers):
        score = self.totalScore
        for no in errAnswers.keys():
            index = no - 1
            if index < self.realJudgmentRequestNum:
                score -= self.judgmentScore
            elif index < self.realJudgmentRequestNum + self.realOneChoiceRequestNum:
                score -= self.oneChoiceScore
            else:
                score -= self.multiChoiceScore
        return len(errAnswers), score

    def isPassExam(self, score):
        return score >= self.totalScore * self.scoreLine / 100


if __name__ == "__main__":
    mockExamUtil = MockExamUtil()
    mockExamUtil.genExamPaperByAll()
    mockExamUtil.genExamPaperByReal()
    for i in range(mockExamUtil.totalQuestionNums):
        print(mockExamUtil.getQuestion(i))

