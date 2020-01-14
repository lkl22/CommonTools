# -*- coding: utf-8 -*-
# python 3.x
# Filename: FileUtil.py
# 定义一个FileUtil工具类实现文件相关的功能
import os
import shutil
from util.ReUtil import *
from util.LogUtil import *


class FileUtil:
    @staticmethod
    def findFilePathList(dirPath, findPatterns=[]):
        """
        查找指定目录下匹配文件名的文件路径
        :param dirPath: 查找目录path
        :param findPatterns: 文件名匹配正则
        :return: 查找到的文件path列表
        """
        L = []
        # for循环自动完成递归枚举
        # 三个参数：分别返回1.父目录（当前路径） 2.所有文件夹名字（不含路径） 3.所有文件名字（不含路径）
        for parent, dirnames, filenames in os.walk(dirPath):
            for fn in filenames:
                filePath = os.path.join(parent, fn).replace("\\", "/")
                if len(findPatterns) > 0:
                    if ReUtil.matchMore(fn, findPatterns):
                        L.append(filePath)
                else:
                    L.append(filePath)
        return L

    @staticmethod
    def modifyFilePath(srcFile, dstFile, isCopy=True):
        """
        复制/移动文件到目标位置
        :param srcFile: 源文件
        :param dstFile: 目标文件
        :param isCopy: True 复制 False 移动
        """
        if not os.path.isfile(srcFile):
            LogUtil.e("modifyFilePath", "%s not exist!" % srcFile)
        else:
            fp, fn = os.path.split(dstFile)  # 分离文件名和路径
            if not os.path.exists(fp):
                os.makedirs(fp)  # 创建路径
            if isCopy:
                shutil.copyfile(srcFile, dstFile)  # 复制文件
                LogUtil.w("copy %s ->\nto   %s" % (srcFile, dstFile))
            else:
                shutil.move(srcFile, dstFile)  # 移动文件
                LogUtil.w("move %s ->\nto   %s" % (srcFile, dstFile))
        pass

    @staticmethod
    def modifyFilesPath(fnPatterns, srcFp, dstFp, isCopy=True):
        """
        从源目录查找匹配的文件，复制/移动文件到目标目录下，保持相对于源目录的相对路径
        :param fnPatterns: 文件名匹配正则
        :param srcFp: 源目录路径
        :param dstFp: 目标目录路径
        :param isCopy: True 复制 False 移动
        """
        # 查找需求复制/移动的文件列表
        srcFiles = FileUtil.findFilePathList(srcFp, fnPatterns)
        for srcFile in srcFiles:
            dstFile = srcFile.replace(srcFp, dstFp)
            FileUtil.modifyFilePath(srcFile, dstFile, isCopy)
        pass


# if __name__ == "__main__":
#     print(FileUtil.findFilePathList("/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res", ["ic_launcher.png", "colors.xml", "strings.xml"]))
#     FileUtil.modifyFilePath("/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res/values/strings.xml",
#                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res/values/11/22/strings.xml", False)
#     FileUtil.modifyFilesPath(["strings.xml", "colors.xml"],
#                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res",
#                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/bb", True)
