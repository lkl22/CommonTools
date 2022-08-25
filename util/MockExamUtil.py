# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamUtil.py
# 定义一个MockExamUtil工具类处理模拟考试相关逻辑
import random

from util.LogUtil import LogUtil
from util.OpenpyxlUtil import OpenpyxlUtil


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
        self.oneChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 5)
        self.oneChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 6)
        self.multipleChoiceNums = OpenpyxlUtil.getCell(self.infoSheet, 2, 7)
        self.multipleChoiceScore = OpenpyxlUtil.getCell(self.infoSheet, 2, 8)
        LogUtil.w("MockExamUtil", "考试科目：", self.examName, "分数线：", self.scoreLine, "判断题个数：", self.judgmentNums,
                  "判断题分值", self.judgmentScore, "单选题个数", self.oneChoiceNums, "单选题分值", self.oneChoiceScore,
                  "多选题个数", self.multipleChoiceNums, "多选题分值", self.multipleChoiceScore)


if __name__ == "__main__":
    mockExamUtil = MockExamUtil()
    print()
