# -*- coding: utf-8 -*-
# python 3.x
# Filename: MD5Util.py
# 定义一个MD5Util工具类实现数据的MD5加密的功能
from util.LogUtil import *
import hashlib


class MD5Util:
    @staticmethod
    def md5(data: str):
        """
        获取数据的md5加密值
        :param data: data
        :return: md5加密值
        """
        if not data:
            return None
        return hashlib.md5(data.encode('utf-8')).hexdigest()


if __name__ == "__main__":
    LogUtil.d(MD5Util.md5("ssss"))
    LogUtil.d(MD5Util.md5("ssss"))
    LogUtil.d(MD5Util.md5("sss"))
