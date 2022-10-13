# -*- coding: utf-8 -*-
# python 3.x
# Filename: ListUtil.py
# 定义一个ListUtil工具类实现列表数据操作相关的功能
from util.LogUtil import *


class ListUtil:
    @staticmethod
    def swap(data: list, lIndex: int, rIndex: int):
        """
        交换列表里两个数据的位置
        :param data: data
        :param lIndex: 需要交换数据的索引
        :param rIndex: 需要交换数据的索引
        """
        if data:
            data[lIndex], data[rIndex] = data[rIndex], data[lIndex]
        pass

    @staticmethod
    def insert(data: list, oldIndex: int, newIndex: int):
        """
        将数据从 oldIndex 重新插入到指定的位置 newIndex
        :param data: data
        :param oldIndex: 旧的索引
        :param newIndex: 新的索引
        """
        if data:
            newIndex = (len(data) + newIndex) % len(data)
            if newIndex == oldIndex:
                return
            oldData = data[oldIndex]
            data.remove(oldData)
            if newIndex < oldIndex:
                data.insert(newIndex, oldData)
            else:
                data.insert(newIndex, oldData)
        pass

    @staticmethod
    def remove(listData: [], value):
        """
        从列表中删除指定数据
        :param listData: 列表
        :param value: 要删除的数据
        """
        if value in listData:
            listData.remove(value)
        pass

    @staticmethod
    def contain(listData: [dict], key: str, value):
        """
        判断指定的数据是否在字典列表里
        :param listData: 源数据
        :param key: 数据存在字典里的key
        :param value: 数据值
        :return: True 存在
        """
        if listData:
            for item in listData:
                if key in item and value == item[key]:
                    return True
        return False

    @staticmethod
    def find(listData: [dict], findKey: str, findValue):
        """
        从字典列表数据里查找指定字典数据
        :param listData: 源数据
        :param findKey: 查找目标数据的key
        :param findValue: 需要查找目标dict数据的判断数据值
        :return: 找到的数据
        """
        if listData:
            for item in listData:
                if findKey in item and findValue == item[findKey]:
                    return item
        return None

    @staticmethod
    def get(listData: [dict], filterKey: str, filterValue, findKey: str, default=None):
        """
        从字典列表数据里查找指定字典数据的某个值
        :param listData: 源数据
        :param filterKey: 需要查找目标dict数据的判断key
        :param filterValue: 需要查找目标dict数据的判断数据值
        :param findKey: 查找目标数据的key
        :param default: 查找失败，返回的默认值
        :return: 找到的数据
        """
        if listData:
            for item in listData:
                if filterKey in item and filterValue == item[filterKey] and findKey in item:
                    return item[findKey]
        return default

    @staticmethod
    def update(listData: list, oldData, newData):
        """
        更新列表数据
        :param listData: 源数据
        :param oldData: 需要从列表里删除的数据
        :param newData: 需要添加到列表里的数据
        """
        if listData:
            if oldData in listData:
                listData.remove(oldData)
            listData.append(newData)
        pass


if __name__ == "__main__":
    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.swap(data, 1, 2)
    LogUtil.d(data)

    ListUtil.swap(data, 1, -1)
    LogUtil.d(data)

    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.swap(data, 0, -1)
    LogUtil.d(data)

    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.insert(data, 2, 3)
    LogUtil.d(data)

    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.insert(data, 3, 2)
    LogUtil.d(data)

    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.insert(data, 3, 0)
    LogUtil.d(data)

    data = ["ss", "dd", "ee", "ww", "ll"]
    ListUtil.insert(data, 3, -1)
    LogUtil.d(data)

    LogUtil.d(ListUtil.contain([{"dd": 12}, {"dd": 23}], 'dd', 35))
    LogUtil.d(ListUtil.contain([{"dd": 12}, {"dd": 23}], 'dd', 12))
