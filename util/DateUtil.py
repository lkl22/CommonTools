# -*- coding: utf-8 -*-
# python 3.x
# Filename: DateUtil.py
# 定义一个DateUtil工具类实现时间相关的功能
import time

DATE_TIME = "%Y-%m-%d %H:%M:%S"


class DateUtil:
    @staticmethod
    def timestamp2Time(timeStamp, timeFormat=DATE_TIME):
        """
        时间戳转化为指定格式的时间str
        :param timeStamp: 时间戳 [seconds]
        :param timeFormat: 时间格式
        :return: 格式化时间str
        """
        # 转换成localtime
        timeLocal = time.localtime(timeStamp)
        # 转换成新的时间格式(2016-05-05 20:28:54)
        return time.strftime(timeFormat, timeLocal)

    @staticmethod
    def time2Timestamp(timeStr, timeFormat=DATE_TIME):
        """
        指定格式的时间str转化为时间戳
        :param timeStr: 时间str
        :param timeFormat: 时间格式
        :return: 时间戳 [seconds]
        """
        # 转换成时间数组
        timeArray = time.strptime(timeStr, timeFormat)
        # 转换成时间戳
        timestamp = time.mktime(timeArray)
        return int(timestamp)

    @staticmethod
    def nowTimestamp(isMilliSecond=False):
        """
        获取当前的时间戳
        :param isMilliSecond: True 返回 ms False 返回 s
        :return: 时间戳
        """
        # 获取当前时间
        timeNow = time.time_ns()
        if isMilliSecond:
            return int(timeNow / 1000000)
        else:
            return int(timeNow / 1000000000)

    @staticmethod
    def nowTime(timeFormat=DATE_TIME):
        """
        获取当前的时间（指定格式）
        :param timeFormat: 时间格式
        :return: 时间str
        """
        return DateUtil.timestamp2Time(DateUtil.nowTimestamp(), timeFormat)


if __name__ == "__main__":
    print(DateUtil.nowTimestamp(True))
    print(DateUtil.nowTime())
    print(DateUtil.time2Timestamp("2020-01-10 10:23:53"))
