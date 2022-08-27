# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamUtil.py
# 定义一个MockExamUtil工具类处理模拟考试相关逻辑
import random

from openpyxl.worksheet.worksheet import Worksheet

from util.LogUtil import LogUtil
from util.OpenpyxlUtil import OpenpyxlUtil
from util.RandomUtil import RandomUtil


def getRequest(st: Worksheet, index=2):
    return {
        'index': index,
        'request': OpenpyxlUtil.getCell(st, index, 1),
        'answer': OpenpyxlUtil.getCell(st, index, 2),
        'remark': OpenpyxlUtil.getCell(st, index, 3),
        'solution': OpenpyxlUtil.getCell(st, index, 4),
        'A': OpenpyxlUtil.getCell(st, index, 5),
        'B': OpenpyxlUtil.getCell(st, index, 6),
        'C': OpenpyxlUtil.getCell(st, index, 7),
        'D': OpenpyxlUtil.getCell(st, index, 8),
        'E': OpenpyxlUtil.getCell(st, index, 9),
        'F': OpenpyxlUtil.getCell(st, index, 10),
        'G': OpenpyxlUtil.getCell(st, index, 11),
        'H': OpenpyxlUtil.getCell(st, index, 12),
    }


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

        self.judgmentNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 3)
        self.judgmentScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 4)
        self.judgmentRequestBankNums = OpenpyxlUtil.getRows(self.judgmentSheet)

        self.oneChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 5)
        self.oneChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 6)
        self.oneChoiceRequestBankNums = OpenpyxlUtil.getRows(self.oneChoiceSheet)

        self.multipleChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 7)
        self.multipleChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 8)
        self.multipleChoiceRequestBankNums = OpenpyxlUtil.getRows(self.multipleChoiceSheet)

        self.maxCol = OpenpyxlUtil.getColumns(self.oneChoiceSheet)

        LogUtil.w("MockExamUtil", "考试科目：", self.examName, "分数线：", self.scoreLine, "最大列数：", self.maxCol,
                  "\n判断题个数", self.judgmentNums, "\t判断题分值", self.judgmentScore, "\t判断题题库", self.judgmentRequestBankNums,
                  "\n单选题个数", self.oneChoiceNums, "\t单选题分值", self.oneChoiceScore, "\t单选题题库",
                  self.oneChoiceRequestBankNums, "\n多选题个数", self.multipleChoiceNums, "\t多选题分值",
                  self.multipleChoiceScore, "\t多选题题库", self.multipleChoiceRequestBankNums)
        pass

    def genExamPaper(self):
        self.judgmentRequestRows = []
        if self.judgmentRequestBankNums > 1 and self.judgmentNums > 0:
            self.judgmentRequestRows = RandomUtil.sample(self.judgmentNums, 2, self.judgmentRequestBankNums)
        self.realJudgmentRequestNum = len(self.judgmentRequestRows)

        self.oneChoiceRequestRows = []
        if self.oneChoiceRequestBankNums > 1 and self.oneChoiceNums > 0:
            self.oneChoiceRequestRows = RandomUtil.sample(self.oneChoiceNums, 2, self.oneChoiceRequestBankNums)
        self.realOneChoiceRequestNum = len(self.oneChoiceRequestRows)

        self.multipleChoiceRequestRows = []
        if self.multipleChoiceRequestBankNums > 1 and self.multipleChoiceNums > 0:
            self.multipleChoiceRequestRows = RandomUtil.sample(self.multipleChoiceNums, 2,
                                                               self.multipleChoiceRequestBankNums)
        self.realMultipleChoiceRequestNum = len(self.multipleChoiceRequestRows)

        self.totalRequestNums = self.realJudgmentRequestNum + self.realOneChoiceRequestNum + self.realMultipleChoiceRequestNum
        LogUtil.w("MockExamUtil genExamPaper:", "\n判断题题号：", self.judgmentRequestRows, self.realJudgmentRequestNum,
                  "\n单选题题号：", self.oneChoiceRequestRows, self.realOneChoiceRequestNum, "\n多选题题号：",
                  self.multipleChoiceRequestRows, self.realMultipleChoiceRequestNum, "\n总题数：", self.totalRequestNums)
        self.index = 0
        pass

    def nextRequest(self):
        if self.index >= self.totalRequestNums:
            return None
        if self.index < self.realJudgmentRequestNum:
            result = getRequest(self.judgmentSheet, self.judgmentRequestRows[self.index])
        elif self.index < self.realJudgmentRequestNum + self.realOneChoiceRequestNum:
            result = getRequest(self.oneChoiceSheet, self.oneChoiceRequestRows[self.index - self.realJudgmentRequestNum])
        else:
            result = getRequest(self.multipleChoiceSheet, self.multipleChoiceRequestRows[self.totalRequestNums - self.index - 1])
        self.index += 1
        return result


if __name__ == "__main__":
    mockExamUtil = MockExamUtil()

    mockExamUtil.genExamPaper()

    for i in range(mockExamUtil.totalRequestNums):
        print(mockExamUtil.nextRequest())
