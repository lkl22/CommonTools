# -*- coding: utf-8 -*-
# python 3.x
# Filename: ClipboardUtil.py
# 定义一个ClipboardUtil工具类实现数据copy到剪切板相关的功能
import pyperclip
from util.LogUtil import LogUtil


class ClipboardUtil:
    @staticmethod
    def copyToClipboard(data: str):
        """
        向剪切板复制文本
        :param data: 文本数据
        """
        pyperclip.copy(data)

    @staticmethod
    def pasteFromClipboard() -> str:
        """
        从剪切板复制文本
        :return: 复制的文本
        """
        return pyperclip.paste()


if __name__ == "__main__":
    ClipboardUtil.copyToClipboard("1234567812345678")
    ClipboardUtil.copyToClipboard("qwerr")
    LogUtil.d(ClipboardUtil.pasteFromClipboard())
    pass
