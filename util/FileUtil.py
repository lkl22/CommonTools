# -*- coding: utf-8 -*-
# python 3.x
# Filename: FileUtil.py
# 定义一个FileUtil工具类实现文件相关的功能
import os
import shutil
import zipfile

from util.PlatformUtil import PlatformUtil
from util.ReUtil import *
from util.LogUtil import *
from util.ShellUtil import ShellUtil

TAG = "FileUtil"


class FileUtil:
    @staticmethod
    def findFilePathList(dirPath, findPatterns=[], excludeDirPatterns=[]):
        """
        查找指定目录下匹配文件名的文件路径
        :param dirPath: 查找目录path
        :param findPatterns: 文件名匹配正则，不传返回目录下所有文件
        :param excludeDirPatterns: 需要排除的目录，文件在排除的目录列表下的排除掉
        :return: 查找到的文件path列表
        """
        L = []
        # for循环自动完成递归枚举
        # 三个参数：分别返回1.父目录（当前路径） 2.所有文件夹名字（不含路径） 3.所有文件名字（不含路径）
        fileNames = os.listdir(dirPath)
        for fn in fileNames:
            fp = os.path.join(dirPath, fn).replace("\\", "/")
            if os.path.isfile(fp):
                if len(findPatterns) > 0 and not ReUtil.matchMore(fp, findPatterns):
                    LogUtil.i(TAG, f"findFilePathList {fp} not in {findPatterns}")
                    continue
                L.append(fp)
            else:
                if len(excludeDirPatterns) > 0 and ReUtil.matchMore(fp + "/", excludeDirPatterns):
                    LogUtil.i(TAG, f"findFilePathList {fp} in {excludeDirPatterns}")
                    continue
                L += FileUtil.findFilePathList(fp, findPatterns, excludeDirPatterns)
        return L

    @staticmethod
    def findFilePathListByExclude(dirPath, excludeExtPatterns=[], excludeDirPatterns=[]):
        """
        查找指定目录下排除了指定目录/后缀文件的文件路径
        :param dirPath: 查找目录path
        :param excludeExtPatterns: 需要排除的文件后缀，文件后缀包含在该列表的排除掉
        :param excludeDirPatterns: 需要排除的目录，文件在排除的目录列表下的排除掉
        :return: 查找到的文件path列表
        """
        L = []
        # for循环自动完成递归枚举
        # 三个参数：分别返回1.父目录（当前路径） 2.所有文件夹名字（不含路径） 3.所有文件名字（不含路径）
        for parent, dirnames, filenames in os.walk(dirPath):
            for fn in filenames:
                filePath = os.path.join(parent, fn).replace("\\", "/")
                fp, fn = os.path.split(filePath)
                _, fileExt = os.path.splitext(fn)

                if len(excludeDirPatterns) > 0 and ReUtil.matchMore(fp + "/", excludeDirPatterns):
                    LogUtil.i(TAG, f"findFilePathListByExclude {filePath} in {excludeDirPatterns}")
                    continue

                if len(excludeExtPatterns) > 0 and fileExt in excludeExtPatterns:
                    LogUtil.i(TAG, f"findFilePathListByExclude {fn} in {excludeExtPatterns}")
                    continue
                L.append(filePath)
        return L

    @staticmethod
    def mkFilePath(filePath):
        """
        创建文件目录
        :param filePath: 文件路径
        """
        try:
            fp, fn = os.path.split(filePath)  # 分离文件名和路径
            if not os.path.exists(fp):
                os.makedirs(fp)  # 创建路径
        except Exception as err:
            LogUtil.e(TAG, 'mkFilePath 错误信息：', err)

    @staticmethod
    def mkDirs(dirPath):
        """
        创建文件夹
        :param dirPath: 文件夹路径
        """
        try:
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)  # 创建路径
        except Exception as err:
            LogUtil.e(TAG, 'mkDirs 错误信息：', err)

    @staticmethod
    def existsFile(fp):
        """
        判断是否存在指定文件
        :param fp: 文件路径
        :return: true 存在
        """
        if os.path.exists(fp) and os.path.isfile(fp):
            return True
        else:
            return False

    @staticmethod
    def modifyFilePath(srcFile, dstFile, isCopy=True):
        """
        复制/移动文件到目标位置
        :param srcFile: 源文件
        :param dstFile: 目标文件
        :param isCopy: True 复制 False 移动
        """
        if not os.path.isfile(srcFile):
            LogUtil.e(TAG, "modifyFilePath", "%s not exist!" % srcFile)
            return False
        else:
            FileUtil.mkFilePath(dstFile)
            try:
                if isCopy:
                    shutil.copyfile(srcFile, dstFile)  # 复制文件
                    LogUtil.w(TAG, "copy %s ->\nto   %s" % (srcFile, dstFile))
                else:
                    shutil.move(srcFile, dstFile)  # 移动文件
                    LogUtil.w(TAG, "move %s ->\nto   %s" % (srcFile, dstFile))
                return True
            except Exception as err:
                LogUtil.e(TAG, 'modifyFilePath 错误信息：', err)
                return False
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
        # 查找需要复制/移动的文件列表
        srcFiles = FileUtil.findFilePathList(dirPath=srcFp, findPatterns=fnPatterns)
        for srcFile in srcFiles:
            dstFile = srcFile.replace(srcFp, dstFp)
            FileUtil.modifyFilePath(srcFile, dstFile, isCopy)
        pass

    @staticmethod
    def modifyFilesName(srcFns, dstFn):
        """
        批量修改文件名
        :param srcFns: 源文件path列表
        :param dstFn: 目标文件名
        :return: True 修改成功
        """
        try:
            for srcFn in srcFns:
                fp, fn = os.path.split(srcFn)  # 分离文件名和路径
                os.rename(srcFn, os.path.join(fp, dstFn))
            return True
        except Exception as err:
            LogUtil.e(TAG, 'modifyFilesName 错误信息：', err)
            return False

    @staticmethod
    def mergeFiles(srcFns, dstFn):
        """
        将多个文件合并到一个文件
        :param srcFns: 源文件path列表
        :param dstFn: 目标文件名
        :return: True 修改成功
        """
        try:
            FileUtil.mkFilePath(dstFn)
            with open(dstFn, mode='x') as dstFile:
                for srcFn in srcFns:
                    dstFile.write(f"\nfilePath: {srcFn}\n")
                    with open(srcFn) as file:
                        content = file.readlines()
                        dstFile.writelines(content)
            return True
        except Exception as err:
            LogUtil.e(TAG, 'mergeFiles 错误信息：', err)
            return False

    @staticmethod
    def getProjectPath():
        """
        获取项目根目录
        :return: 项目根目录
        """
        path = os.getcwd().replace("\\", "/")
        while not FileUtil.existsFile(os.path.join(path, 'CommonTools.spec')):
            path = os.path.split(path)[0]
        LogUtil.i(TAG, "getProjectPath：", path)
        return path

    @staticmethod
    def getConfigFp(fn):
        """
        获取项目下指定配置文件的path
        :param fn: 文件名
        :return: 项目下指定配置文件的path
        """
        path = FileUtil.getProjectPath() + "/resources/config/"
        if not os.path.isdir(path):
            os.mkdir(path)
        for fileName in os.listdir(path):
            if fn in fileName:
                return path + fileName
        return path + fn

    @staticmethod
    def getIconFp(fn):
        """
        获取项目下指定icons文件的path
        :param fn: 文件名
        :return: 项目下指定icon文件的path
        """
        path = FileUtil.getProjectPath() + "/resources/icons/"
        if not os.path.isdir(path):
            os.mkdir(path)
        return path + fn

    @staticmethod
    def getAlgorithmFp(fn):
        """
        获取项目下指定algorithm文件的path
        :param fn: 文件名
        :return: 项目下指定algorithm文件的path
        """
        path = FileUtil.getProjectPath() + "/resources/algorithm/"
        if not os.path.isdir(path):
            os.mkdir(path)
        return path + fn

    @staticmethod
    def clearPath(fp):
        """
        删除指定目录下所有的文件
        :param fp: 目录path
        """
        try:
            shutil.rmtree(fp)
        except Exception as e:
            LogUtil.e(TAG, 'FileUtil clearPath 错误信息：', e)

    @staticmethod
    def removeFile(fp):
        """
        删除指定的文件
        :param fp: 文件path
        """
        try:
            os.remove(fp)
        except Exception as e:
            LogUtil.e(TAG, 'FileUtil removeFile 错误信息：', e)

    @staticmethod
    def zipDir(dirPath, outFullName):
        """
        压缩指定文件夹
        :param dirPath: 目标文件夹路径
        :param outFullName: 压缩文件保存路径+xxxx.zip
        :return: 无
        """
        zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(dirPath):
            # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
            fpath = path.replace(dirPath, '')

            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    @staticmethod
    def unzipFile(zipFileName, unzipToDir):
        """
        解压文件到指定目录
        :param zipFileName: 压缩文件名
        :param unzipToDir: 解压文件保存路径
        """
        if not os.path.exists(unzipToDir):
            os.mkdir(unzipToDir)
        zfObj = zipfile.ZipFile(zipFileName)
        for name in zfObj.namelist():
            name = name.replace('\\', '/')
            if name.endswith('/'):
                os.mkdir(os.path.join(unzipToDir, name))
            else:
                extFileName = os.path.join(unzipToDir, name)
                extDir = os.path.dirname(extFileName)
                if not os.path.exists(extDir):
                    os.mkdir(extDir)
                outfile = open(extFileName, 'wb')
                outfile.write(zfObj.read(name))
                outfile.close()

    @staticmethod
    def readFile(fp, encoding='utf8'):
        """
        读取文件内容
        :param fp: 文件path
        :param encoding: 文件编码
        :return: 文件内容
        """
        try:
            with open(fp, encoding=encoding) as file:
                return file.read()
        except Exception as e:
            LogUtil.e(TAG, 'FileUtil readFile 错误信息：', e)
            return None

    @staticmethod
    def readFileSize(fn: str):
        """
        读取文件大小
        :param fn: 文件名
        :return: 大小
        """
        try:
            size = os.path.getsize(fn)
            LogUtil.d(TAG, "readFileSize", fn, size)
            return size
        except Exception as e:
            LogUtil.e(TAG, 'readFileSize 错误信息：', e)
            return -1

    @staticmethod
    def getFileName(fp: str):
        """
        获取文件名
        :param fp: 文件路径
        :return: 文件名
        """
        try:
            name = os.path.basename(fp)
            return name
        except Exception as e:
            LogUtil.e(TAG, 'getFileName 错误信息：', e)
            return ''

    @staticmethod
    def openFile(fp):
        """
        打开指定文件
        :param fp: 文件路径
        """
        LogUtil.d(TAG, "openFile", fp)
        if PlatformUtil.isMac():
            ShellUtil.exec(f"open {fp}")
        elif PlatformUtil.isWindows():
            ShellUtil.exec(f"start notepad {fp}")
        pass


if __name__ == "__main__":
    # print(FileUtil.findFilePathList("/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res", ["ic_launcher.png", "colors.xml", "strings.xml"]))
    # print(FileUtil.findFilePathList("/Users/likunlun/Pictures/生活照/泽林/", [".*.png", ".*.jpg", ".*.JPEG"], False))
    # print(FileUtil.findFilePathList("/Users/likunlun/Pictures/生活照/泽林/", ['.*.((jpg)|(JPG)|(png)|(PNG)|(JPEG)|(jpeg))'], False))
    #     FileUtil.modifyFilePath("/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res/values/strings.xml",
    #                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res/values/11/22/strings.xml", False)
    #     FileUtil.modifyFilesPath(["strings.xml", "colors.xml"],
    #                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/res",
    #                             "/Users/likunlun/PycharmProjects/CarAssist/app/src/main/bb", True)
    # print(FileUtil.getProjectPath())
    # print(FileUtil.getConfigFp('BaseConfig.ini'))
    #
    # print(FileUtil.getIconFp('zoom_in.jpg'))

    # FileUtil.zipDir('./testZip', './testZip1.zip')
    # FileUtil.unzipFile('./testZip.zip', './testZip3')

    # print(FileUtil.readFile('../resources/algorithm/SelectionSort/SelectionSort.java'))
    # print(FileUtil.readFileSize('0C1A8658.JPG'))
    # print(FileUtil.getFileName('/aa/ad/../d/0C1A8658.JPG'))

    # print(FileUtil.existsFile('/aa/ad/../d/0C1A8658.JPG'))
    # print(FileUtil.existsFile('../resources/mockExam/题库模版.xlsx'))

    print(FileUtil.findFilePathListByExclude('./', [".JPG", ".py"], [".*/111/.*", ".*/__pycache__/.*"]))
