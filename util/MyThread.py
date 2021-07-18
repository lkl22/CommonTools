# -*- coding: utf-8 -*-
# python 3.x
# Filename: MyThread.py
# 定义一个MyThread工具类实现线程相关的功能

import threading
from time import ctime

from util.LogUtil import LogUtil


class MyThread(threading.Thread):
    def __init__(self, func, args: (), name=''):
        threading.Thread.__init__(self)
        self.res = -1
        self.func = func
        self.name = name
        self.args = args

    def run(self):
        LogUtil.d('开始执行', self.name, ' 在：', ctime())
        self.res = self.func(*self.args)
        LogUtil.d(self.name, '结束于：', ctime())

    def getResult(self):
        return self.res
