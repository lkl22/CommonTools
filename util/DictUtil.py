# -*- coding: utf-8 -*-
# python 3.x
# Filename: DictUtil.py
# 定义一个DictUtil工具类实现字典操作相关的功能
import time
from util.LogUtil import *


class DictUtil:
    @staticmethod
    def get(data: dict, key: str):
        """
        从字典中获取指定的数据
        :param data: data
        :param key: key
        :return: value
        """
        if data and key in data:
            return data[key]
        return None


if __name__ == "__main__":
    LogUtil.d(DictUtil.get({"aa": 11, "bb": "dd"}, 'aa'))
    LogUtil.d(DictUtil.get({"aa": 11, "bb": "dd"}, 'aqa'))
    LogUtil.d(DictUtil.get(None, 'aqa'))
