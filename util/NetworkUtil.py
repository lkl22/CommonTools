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
        context = ssl._create_unverified_context()
        with request.urlopen(url, context=context) as r:
            return r.read()

    @staticmethod
    def downloadFile(url, file=None):
        try:
            if not file:
                file = url.split('/')[-1]
            with open(file, 'wb') as f:
                f.write(NetworkUtil.get(url))
            return True
        except Exception as err:
            LogUtil.e('downloadFile 错误信息：', err)
            return False


if __name__ == "__main__":
    print(NetworkUtil.downloadFile("https://github.com/lkl22/AndroidTestAssistTool/releases/download/v1.0.1/app-release.apk", 'dd.apk'))
