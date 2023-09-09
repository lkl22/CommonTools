# -*- coding: utf-8 -*-
# python 3.x
# Filename: DictUtil.py
# 定义一个DictUtil工具类实现字典操作相关的功能
from util.LogUtil import *


class DictUtil:
    @staticmethod
    def get(data: dict, key: str, default=None):
        """
        从字典中获取指定的数据
        :param data: data
        :param key: key
        :param default: 默认值
        :return: value
        """
        if data and key in data:
            return data[key]
        return default

    @staticmethod
    def join(data: list[dict]):
        """
        将列表中的字典项合并为一个大字典
        :param data: data
        :return: 合并结果
        """
        result = {}
        if data:
            for item in data:
                result = {**result, **item}
        return result


if __name__ == "__main__":
    LogUtil.d(DictUtil.get({"aa": 11, "bb": "dd"}, 'aa'))
    LogUtil.d(DictUtil.get({"aa": 11, "bb": "dd"}, 'aqa'))
    LogUtil.d(DictUtil.get(None, 'aqa'))
