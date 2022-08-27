# -*- coding: utf-8 -*-
# python 3.x
# Filename: Word2Excel.py
# 定义一个Word2Excel类实现word题库转Excel文件

import re
from docx import Document
from collections import OrderedDict
from util.OpenpyxlUtil import OpenpyxlUtil

questionDescRule = re.compile("(\d+[．.])(.*)")
answerRule = re.compile("[\S\s]*([(（][ABCDEFGHIJK ]+[)）])[\S\s]*")

optionRule = re.compile("([ABCDEFGHIJK ]{1,2}[.、])")

solutionRule = re.compile("(解析[：:])(.*)")


class Word2Excel:
    def __init__(self, filePath='../../resources/mockExam/题库.docx', isDebug=True):
        self.doc = Document(filePath)
        self.questionDataDict = self.getWordTxt()
        self.genExcel()

    def getWordTxt(self):
        # 保存最终的结构化数据
        questionDataDict = OrderedDict()

        questionNo = 0
        questionObj = None
        answer = None
        txtType = None
        curOption = None
        for paragraph in self.doc.paragraphs:
            text = paragraph.text
            # 对于空白行就直接跳过
            if not text:
                continue

            matchObj = questionDescRule.match(text)
            if matchObj:
                questionDesc = matchObj.group(2).strip()
                # print(matchObj.group(1)[:-1], questionDesc)
                if questionObj:
                    questionDataDict[questionNo] = questionObj

                txtType = 'questionDesc'
                questionNo += 1
                questionObj = OrderedDict()
                questionObj['question'] = questionDesc
                answer = None
                continue

            matchObj = optionRule.match(text)
            if matchObj:
                txtType = 'option'
                matchObj = optionRule.split(text)
                if not answer:
                    answer = answerRule.match(questionObj['question']).group(1)[1:-1].strip()
                    questionObj['answer'] = answer
                    questionObj['question'] = re.sub("[(（][ABCDEFGHIJK ]+[)）]", "()", questionObj['question'])
                # print(matchObj)
                for txt in matchObj:
                    txt = txt.strip()
                    if txt:
                        if optionRule.match(txt):
                            curOption = txt[:1]
                            continue
                        else:
                            questionObj[curOption] = txt
                continue

            matchObj = solutionRule.match(text)
            if matchObj:
                txtType = 'solution'
                questionObj['solution'] = matchObj.group(2).strip()
                continue

            if txtType == 'questionDesc':
                questionObj['question'] += "\n" + text
            elif txtType == 'option':
                questionObj[curOption] += "\n" + text
            elif txtType == 'solution':
                questionObj['solution'] += "\n" + text

        print(questionDataDict)
        return questionDataDict

    @staticmethod
    def writeSheet(st, row, col, dict, key):
        if key in dict.keys():
            OpenpyxlUtil.writeSheet(st, row, col, dict[key])

    def genExcel(self):
        bk = OpenpyxlUtil.createBook()
        oneChoiceSheet = OpenpyxlUtil.addSheet(bk, "单选题")
        multiChoiceSheet = OpenpyxlUtil.addSheet(bk, "多选题", 1)
        for st in [oneChoiceSheet, multiChoiceSheet]:
            OpenpyxlUtil.writeSheet(st, 1, 1, "题干")
            OpenpyxlUtil.writeSheet(st, 1, 2, "答案")
            OpenpyxlUtil.writeSheet(st, 1, 3, "备注")
            OpenpyxlUtil.writeSheet(st, 1, 4, "解析")
            for index, ch in enumerate("ABCDEFGHIJK"):
                OpenpyxlUtil.writeSheet(st, 1, 5 + index, "选项" + ch)

        oneChoiceRow = 1
        multiChoiceRow = 1
        for no, questionObj in self.questionDataDict.items():
            if len(questionObj['answer']) > 1:
                st = multiChoiceSheet
                multiChoiceRow += 1
                row = multiChoiceRow
            else:
                st = oneChoiceSheet
                oneChoiceRow += 1
                row = oneChoiceRow

            Word2Excel.writeSheet(st, row, 1, questionObj, "question")
            Word2Excel.writeSheet(st, row, 2, questionObj, "answer")
            Word2Excel.writeSheet(st, row, 4, questionObj, "solution")
            for index, ch in enumerate("ABCDEFGHIJK"):
                Word2Excel.writeSheet(st, row, 5 + index, questionObj, ch)

        bk.save("题库.xlsx")
        bk.close()

if __name__ == '__main__':
    Word2Excel()
    # print(answerRule.match('类Test1定义如下：\npublic class Test1{\npublic float aMethod（float a，float b）{ return 0;}\n}\n将以下哪种方法插入行3 是不合法的。 (B )  '))
    print(re.sub("[(（][ABCDEFGHIJK ]+[)）]", "()", '网络安全是在分布网络环境中对（ D ）'))
    pass
