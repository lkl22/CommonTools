# -*- coding: utf-8 -*-
# python 3.x
# Filename: HashUtil.py
# 定义一个HashUtil工具类实现计算文件hash的功能
import hashlib
import zlib
from util.LogUtil import *


class HashUtil:
    @staticmethod
    def calcFileHash(fp, hashType="MD5"):
        """
        查找指定目录下匹配文件名的文件路径
        :param fp: 文件路径
        :param hashType: MD5、SHA1、SHA256、CRC32
        :return: 文件hash值
        """
        with open(fp, 'rb') as f:
            if hashType == 'CRC32':
                return hex(zlib.crc32(f.read()))
            if hashType == "MD5":
                hashObj = hashlib.md5()
            elif hashType == "SHA1":
                hashObj = hashlib.sha1()
            elif hashType == "SHA256":
                hashObj = hashlib.sha256()
            hashObj.update(f.read())
            return hashObj.hexdigest()


if __name__ == "__main__":
    LogUtil.d("MD5", HashUtil.calcFileHash('GraphicsUtil.py'))
    LogUtil.d("MD5", HashUtil.calcFileHash('GraphicsUtil.py', 'SHA1'))
    LogUtil.d("MD5", HashUtil.calcFileHash('GraphicsUtil.py', 'SHA256'))
    LogUtil.d("MD5", HashUtil.calcFileHash('GraphicsUtil.py', 'CRC32'))
    LogUtil.d("MD5", HashUtil.calcFileHash('OpenpyxlUtil.py', 'CRC32'))
