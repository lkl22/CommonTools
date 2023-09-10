# -*- coding: utf-8 -*-
# python 3.x
# Filename: AsyncFuncManager.py
# 定义一个AsyncFuncManager类实现异步执行函数管理
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from widget.custom.LoadingDialog import LoadingDialog


class AsyncFuncManager(QObject):
    __hideLoadingSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__loadingDialog = None
        self.__hideLoadingSignal.connect(self.__hideLoading)

    def asyncExec(self, target=None, name=None, args=(), kwargs=None):
        # 必须放到线程执行，否则加载框要等指令执行完才会弹
        threading.Thread(target=target, name=name, args=args, kwargs=kwargs).start()
        if not self.__loadingDialog:
            self.__loadingDialog = LoadingDialog()
        pass

    def __hideLoading(self):
        if self.__loadingDialog:
            self.__loadingDialog.close()
            self.__loadingDialog = None
        pass

    def hideLoading(self):
        self.__hideLoadingSignal.emit()
        pass
