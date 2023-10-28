# -*- coding: utf-8 -*-
# python 3.x
# Filename: DateUtil.py
# 定义一个DateUtil工具类实现时间相关的功能
import time
from util.LogUtil import *

DATE_TIME = "%Y-%m-%d %H:%M:%S"
DATE_TIME_COMPACT = "%Y%m%d%H%M%S"
DATE = "%Y%m%d"


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
        try:
            # 转换成时间数组
            timeArray = time.strptime(timeStr, timeFormat)
            # 转换成时间戳
            timestamp = time.mktime(timeArray)
            return int(timestamp)
        except ValueError as err:
            LogUtil.e("time2Timestamp", err)
            return None

    @staticmethod
    def isValidDate(timeStr, timeFormat=DATE_TIME, needTransform=False):
        """
        判断str是不是有效的时间格式
        :param timeStr: 要判断的字符串
        :param timeFormat: 时间格式 比如：%y-%m-%d %H:%M:%S
        :param needTransform: True 需要转换格式，yyyy-MM-dd HH:mm:ss -> %y-%m-%d %H:%M:%S
        :return: True 正确的时间格式
        """
        try:
            if needTransform:
                timeFormat = DateUtil.__formatStringTransform(timeFormat)
                # 转换成时间数组
            time.strptime(timeStr, timeFormat)
            return True
        except Exception as err:
            LogUtil.e("isValidDate", err)
            return False

    @staticmethod
    def reFormat(timeStr, oldFormat=DATE_TIME, newFormat=DATE_TIME, needTransform=False):
        """
        时间格式转化
        :param timeStr: 时间str
        :param oldFormat: 旧的时间格式
        :param newFormat: 新的时间格式
        :param needTransform: True 需要转换格式，yyyy-MM-dd HH:mm:ss -> %y-%m-%d %H:%M:%S
        :return: 新格式化的时间
        """
        # 转换成时间数组
        timeArray = time.strptime(timeStr, DateUtil.__formatStringTransform(oldFormat) if needTransform else oldFormat)
        # 转换成新的时间格式
        return time.strftime(DateUtil.__formatStringTransform(newFormat) if needTransform else newFormat, timeArray)

    @staticmethod
    def __formatStringTransform(oldFormat):
        return oldFormat.replace('yyyy', '%Y').replace('MM', '%m'). \
            replace('dd', '%d').replace('HH', '%H').replace('mm', '%M').replace('ss', '%S')

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

    @staticmethod
    def nowTimeMs():
        """
        获取当前的时间 "%Y-%m-%d %H:%M:%S.%s"
        :return: 时间str
        """
        ms = DateUtil.nowTimestamp(isMilliSecond=True)
        return "%s.%03d" % (DateUtil.timestamp2Time(ms / 1000, DATE_TIME), ms % 1000)

    @staticmethod
    def timestampStr2Seconds(timestampStr):
        """
        将时间戳字符串转化为int型 (s, ms)
        :param timestampStr: 时间戳字符串（s/ms）
        :return: (s, ms)
        """
        try:
            length = len(timestampStr)
            if length == 10:
                return int(timestampStr), 0
            elif length == 13:
                return int(timestampStr[:10]), int(timestampStr[10:])
            else:
                LogUtil.e("输入的时间戳: {0}, 长度不对".format(timestampStr))
                return None
        except ValueError as err:
            print(err)
            return None


if __name__ == "__main__":
    # print(DateUtil.nowTimestamp(True))
    # print(DateUtil.nowTime())
    # print(DateUtil.time2Timestamp("2020-01-10 10:23:53"))

    # print(DateUtil.timestampStr2Seconds("1578740129"))

    print(DateUtil.isValidDate("12-12 12:23:12", '%m-%d %H:%M:%S'))
    print(DateUtil.isValidDate("12-12 12:23:12", 'MM-dd HH:mm:ss', True))

    print(DateUtil.reFormat("12-12 12:23:12", '%m-%d %H:%M:%S', '%m%d%H%M%S'))
    print(DateUtil.reFormat("12-12 12:23:12", 'MM-dd HH:mm:ss', 'MMddHHmmss', True))
    print(DateUtil.nowTimeMs())
