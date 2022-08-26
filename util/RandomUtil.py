# -*- coding: utf-8 -*-
# python 3.x
# Filename: RandomUtil.py
# 定义一个RandomUtil工具类实现随机数生成
import random

from util.LogUtil import LogUtil


class RandomUtil:
    @staticmethod
    def randInt(minValue: int = 0, maxValue: int = 9):
        """
        随机生成一个int整数 【min，max】
        :param minValue: 最小值
        :param maxValue: 最大值
        :return: 生成的随机数
        """
        return random.randint(minValue, maxValue)

    @staticmethod
    def randIntArray(num: int = 10, minValue: int = 1, maxValue: int = 100):
        """
        随机生成一组num数量的范围在【min，max】的int整数列表
        :param num: 数量
        :param minValue: 最小值
        :param maxValue: 最大值
        :return: 数字列表
        """
        data = []
        while num > 0:
            num -= 1
            data.append(random.randint(minValue, maxValue))
        LogUtil.i("Random Int Array: ", data)
        return data

    @staticmethod
    def sample(num: int = 10, minValue: int = 1, maxValue: int = 100):
        """
        随机生成一组num数量的范围在【min，max】的int整数列表（不包含重复数字）
        :param num: 数量
        :param minValue: 最小值
        :param maxValue: 最大值
        :return: 数字列表
        """
        sampleNum = num
        if num > maxValue - minValue + 1:
            sampleNum = maxValue - minValue + 1
        return random.sample(range(minValue, maxValue + 1), sampleNum)


if __name__ == "__main__":
    LogUtil.i(RandomUtil.randInt(-10, 9))
    LogUtil.i(RandomUtil.randIntArray()[0])

    LogUtil.i(RandomUtil.sample(15, 1, 10))
