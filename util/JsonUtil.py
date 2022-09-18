# -*- coding: utf-8 -*-
# python 3.x
# Filename: JsonUtil.py
# 定义一个JsonUtil工具类实现Json相关的功能
import json

from util.LogUtil import LogUtil


class JsonUtil:
    @staticmethod
    def encode(obj, ensureAscii=True, indent=4, separators=(',', ': '), sort_keys=True):
        """
        将 Python 数据编码为 JSON 格式数据
        :param obj: Python 数据
        :param ensureAscii: 是否使用ascii编码
        :param indent: 空格缩进
        :param separators: 分隔符
        :param sort_keys: 是否对key排序
        :return: Json数据
        """
        return json.dumps(obj, ensure_ascii=ensureAscii, indent=indent, separators=separators, sort_keys=sort_keys)

    @staticmethod
    def decode(jsonData):
        """
        将 JSON 格式数据解析为 Python 数据
        :param jsonData: JSON 格式数据
        :return: Python 数据
        """
        try:
            return json.loads(jsonData)
        except Exception as err:
            LogUtil.e('JsonUtil decode 错误信息：', err)
            return None


# if __name__ == "__main__":
#     print(JsonUtil.encode([{'a': 1, 'e': 5, 'b': 2, 'c': 3, 'd': 4}]))
#     print(JsonUtil.decode("{\"a\":\"5\"}"))
