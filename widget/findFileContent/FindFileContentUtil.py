# -*- coding: utf-8 -*-
# python 3.x
# Filename: FindFileContentUtil.py
# 定义一个FindFileContentUtil类实现批量查找文件内容相关的工具方法
import re

import chardet

from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
from util.LogUtil import LogUtil
from widget.findFileContent.FindFileContentManager import *

TAG = "FindFileContentUtil"
MAX_FILE_SIZE = 1024 * 1024


class FindFileContentUtil:
    @staticmethod
    def findFileList(fp: str, configInfo: {}):
        """
        查找需要处理的文件列表
        :param fp: 工作目录
        :param configInfo: 配置信息
        :return: 文件列表
        """
        matchType = DictUtil.get(configInfo, KEY_MATCH_TYPE, MATCH_TYPE_EXCLUDE)
        excludeDirStr = DictUtil.get(configInfo, KEY_EXCLUDE_DIR, "")
        excludeDirs = excludeDirStr.split(";")
        if matchType == MATCH_TYPE_INCLUDE:
            includePatternStr = DictUtil.get(configInfo, KEY_INCLUDE_PATTERN, "")
            includePatterns = includePatternStr.split(";")
            return FileUtil.findFilePathList(dirPath=fp, findPatterns=includePatterns, excludeDirPatterns=excludeDirs)
        else:
            excludeExtStr = DictUtil.get(configInfo, KEY_EXCLUDE_EXT, "")
            excludeExtList = excludeExtStr.split(";")
            return FileUtil.findFilePathListByExclude(dirPath=fp, excludeExtPatterns=excludeExtList,
                                                      excludeDirPatterns=excludeDirs)
        pass

    @staticmethod
    def getPatternList(configInfo: {}):
        """
        获取匹配正则表达式列表
        :param configInfo: 配置信息
        :return: 正则表达式列表
        """
        patternList = []
        patternConfigs = DictUtil.get(configInfo, KEY_LIST, [])
        pattern = ""
        for patternConfig in patternConfigs:
            patternReg = DictUtil.get(patternConfig, KEY_PATTERN, "")
            if not patternReg:
                continue
            if DictUtil.get(patternConfig, KEY_IS_REG, DEFAULT_VALUE_IS_REG):
                patternList.append(f"({patternReg})")
            else:
                pattern += f"|{patternReg}"
        if pattern:
            patternList.append(f"({pattern[1:]})")
        return patternList

    @staticmethod
    def findFileContent(fileList: [], patternList: [], statusCallback, resCallback):
        """
        查找文件内容
        :param fileList: 文件列表
        :param patternList: 正则表达式列表
        :param statusCallback: 处理状态回调
        :param resCallback: 处理结果回调
        """
        for fn in fileList:
            statusCallback(fn)
            fileSize = FileUtil.readFileSize(fn)
            if fileSize == 0:
                continue
            findContents = []
            encoding = None
            with open(fn, mode="rb") as file:
                data = file.read(1024)
                detectRes = chardet.detect(data)
                if detectRes["confidence"] > 0.9:
                    encoding = detectRes["encoding"]
            if encoding:
                try:
                    with open(fn, encoding=encoding) as file:
                        lineNo = 1
                        while True:
                            content = file.readline()
                            if not content:
                                break
                            FindFileContentUtil.matchContent(content=content, findContents=findContents, patternList=patternList, lineNo=lineNo)
                            lineNo += 1
                except Exception as e:
                    LogUtil.e(TAG, 'findFileContent错误信息：', e)
            else:
                with open(fn, mode="rb") as file:
                    while True:
                        content = file.read(1024)
                        if not content:
                            break
                        FindFileContentUtil.matchContent(content=str(content), findContents=findContents, patternList=patternList)
            if findContents:
                resCallback(fn, findContents)
        pass

    @staticmethod
    def matchContent(content, findContents: [], patternList: [], lineNo=-1):
        """
        从指定字符串文本中查找匹配的字符，并将结果添加进结果集
        :param content: 源文本
        :param findContents: 结果集
        :param patternList: 匹配规则
        :param lineNo: 当前文本在文件中的行号 -1，无效行号
        """
        for pattern in patternList:
            it = re.finditer(pattern=pattern, string=content, flags=re.I)
            for match in it:
                res = match.group()
                if lineNo > 0:
                    res = f"{lineNo}: {res}"
                if res not in findContents:
                    findContents.append(res)


if __name__ == '__main__':
    pass
