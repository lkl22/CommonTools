# -*- coding: utf-8 -*-
# python 3.x
# Filename: TinifyUtil.py
# 定义一个TLV类实现TLV数据解析及解析结果打印相关的功能
from collections import OrderedDict
from util.DictUtil import DictUtil
from util.EvalUtil import EvalUtil
from util.LogUtil import LogUtil

TAG = 'TLV'
KEY_L = 'L'
KEY_V = 'V'


class TLV:
    def __init__(self, tags=None, LLengthMap: dict[str, int] = None, VPrintFuncs: dict[str, any] = None):
        """
        构建TLV处理对象
        :param tags: tags列表
        :param LLengthMap: L长度映射，默认L占一个字节，占多个字节需要特殊字符来标识
        :param VPrintFuncs: V 打印输出函数
        """
        self.tags = {}
        self.LLengthMap = LLengthMap
        self.VPrintFuncs = VPrintFuncs
        if tags:
            if type(tags) == list:
                for tag in tags:
                    self.tags[tag] = tag
            elif type(tags) == dict:
                self.tags = tags
            else:
                LogUtil.e(TAG, 'Invalid tags dictionary given - use list of tags or dict as {tag: tag_name}')
        else:
            self.tags = {}

        self.tagLengths = set()
        for tag, tagName in self.tags.items():
            self.tagLengths.add(len(tag))

    def parse(self, tlvString):
        """
        将TLV格式的数据解析出来
        :param tlvString: TLV格式的数据
        :return 解析结果
        """
        parsedData = OrderedDict()
        i = 0
        while i < len(tlvString):
            tagFound = False

            for tagLength in self.tagLengths:
                for tag, tagName in self.tags.items():
                    if tlvString[i:i + tagLength] == tag:
                        LTagBytes, LLenBytes = self.__getLLength(tlvString[i + tagLength: i + tagLength + 2])
                        LTagStr = tlvString[i + tagLength: i + tagLength + LTagBytes]
                        valueStartPosition = i + tagLength + LTagBytes + LLenBytes
                        LLenStr = tlvString[i + tagLength + LTagBytes: valueStartPosition]
                        try:
                            vLength = int(LLenStr, 16)
                        except ValueError:
                            raise ValueError(f'Parse error: tag {tag} has incorrect data length')

                        valueEndPosition = valueStartPosition + vLength * 2
                        if valueEndPosition > len(tlvString):
                            raise ValueError('Parse error: tag ' + tag + ' declared data of length ' + str(
                                vLength) + ', but actual data length is ' + str(
                                int(len(tlvString[valueStartPosition - 1:-1]) / 2)))
                        value = tlvString[valueStartPosition:valueEndPosition]
                        parsedData[tag] = {KEY_L: f'{LTagStr} {LLenStr}'.strip(), KEY_V: self.parse(value)}
                        i = valueEndPosition
                        tagFound = True
            if not tagFound:
                return tlvString
        return parsedData

    def __getLLength(self, LTag: str):
        """
        获取L字符占用的字符数
        :param LTag: LTag字符，映射L所占字符数
        :return: (LTag字符数， L长度字符数)
        """
        LLen = DictUtil.get(self.LLengthMap, LTag)
        if LLen:
            return 2, LLen
        else:
            return 0, 2

    def toString(self, dataDict, depth=0):
        """
        打印TLV数据
        :param dataDict: TLV数据解析后的结果
        :param depth: 层级
        """
        tlvString = ''
        for tag, data in dataDict.items():
            if not data:
                return tlvString
            tlvString += '\n' + ''.rjust(depth * 3, ' ') + f'{tag} {data[KEY_L]} '
            value = DictUtil.get(data, KEY_V)
            if type(value) == OrderedDict:
                tlvString += self.toString(value, depth + 1)
            else:
                valueFunc = DictUtil.get(self.VPrintFuncs, tag)
                if valueFunc:
                    if type(valueFunc) == str:
                        myLocals = {'value': value, 'res': ''}
                        EvalUtil.exec(valueFunc, locals=myLocals)
                        tlvString += myLocals.get('res')
                    else:
                        tlvString += valueFunc(value)
                else:
                    tlvString += value
        return tlvString


def standout(data):
    # print(data)
    return 'hello'


if __name__ == "__main__":
    data = 'E002000A80030000016E02000187'
    tlv = TLV(['E0', '80', '6E'], LLengthMap={'02': 4}, VPrintFuncs={'6E': standout, '80': 'res = value + "word"'})
    LogUtil.d(TAG, '解析结果：', tlv.parse(data))
    LogUtil.d(TAG, '解析结果：', tlv.toString(tlv.parse(data)))
    pass
