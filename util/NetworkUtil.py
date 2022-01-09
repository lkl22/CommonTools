# -*- coding: utf-8 -*-
# python 3.x
# Filename: NetworkUtil.py
# 定义一个NetworkUtil工具类实现网络操作相关的功能

from util.LogUtil import LogUtil
from urllib import request
import ssl


class NetworkUtil:
    @staticmethod
    def get(url):
        """
        获取URL的内容
        :param url: URL地址
        :return: 网址内容
        """
        context = ssl._create_unverified_context()
        with request.urlopen(url, context=context) as r:
            return r.read()

    @staticmethod
    def downloadFile(url, file=None):
        """
        下载文件
        :param url: 文件URL地址
        :param file: 本地文件路径
        :return: True 下载成功
        """
        try:
            if not file:
                file = url.split('/')[-1]
            with open(file, 'wb') as f:
                f.write(NetworkUtil.get(url))
            return True
        except Exception as err:
            LogUtil.e('downloadFile 错误信息：', err)
            return False

    @staticmethod
    def downloadPackage(url, downloadFile=None, retryTimes: int = 3):
        """
        下载文件，失败可以重试几次
        :param url: 文件URL地址
        :param downloadFile: 本地文件路径
        :param retryTimes: 重试次数
        :return: True 下载成功
        """
        LogUtil.d("downloadPackage", "start download {} to {}".format(url, downloadFile))
        while not NetworkUtil.downloadFile(url, downloadFile):
            retryTimes -= 1
            LogUtil.e("downloadPackage", "download failed retry.")
            if retryTimes < 1:
                return False
        return True


if __name__ == "__main__":
    print(NetworkUtil.downloadFile("https://github.com/lkl22/AndroidTestAssistTool/releases/download/v1.0.1/app-release.apk", 'dd.apk'))
