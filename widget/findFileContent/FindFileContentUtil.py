# -*- coding: utf-8 -*-
# python 3.x
# Filename: FindFileContentUtil.py
# 定义一个FindFileContentUtil类实现批量查找文件内容相关的工具方法
import re

from util.DictUtil import DictUtil
from util.FileUtil import FileUtil
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
            return FileUtil.findFilePathListByExclude(dirPath=fp, excludeExtPatterns=excludeExtList, excludeDirPatterns=excludeDirs)
        pass

    @staticmethod
    def getPatternList(configInfo: {}):
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
        for fn in fileList:
            statusCallback(fn)
            fileSize = FileUtil.readFileSize(fn)
            if fileSize > MAX_FILE_SIZE:
                pass
            else:
                fileContent = FileUtil.readFile(fn)
                findContents = []
                for pattern in patternList:
                    it = re.finditer(pattern=pattern, string=fileContent, flags=re.I)
                    for match in it:
                        res = match.group()
                        if res not in findContents:
                            findContents.append(res)
                resCallback(fn, findContents)
        pass


if __name__ == '__main__':

    pass
