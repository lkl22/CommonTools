# -*- coding: utf-8 -*-
# python 3.x
# Filename: HarmonyOperator.py
# 定义一个HarmonyOperator工具类实现harmony cmd相关的功能
import os

from util.DateUtil import DateUtil, DATE_TIME_COMPACT
from util.FileUtil import FileUtil
from util.ShellUtil import ShellUtil
from util.phoneCmd.IPhoneOperator import IPhoneOperator


class HarmonyOperator(IPhoneOperator):
    @staticmethod
    def isDeviceConnect():
        """
        检查device是否连接成功
        :return: True 已经连接成功
        """
        return HarmonyOperator.getDeviceId() is not None

    @staticmethod
    def getDeviceId():
        """
        获取设备唯一标识
        :return: 设备唯一标识
        """
        # sn
        out, err = ShellUtil.exec("hdc list targets -v | findstr Connected")
        if out:
            return out.split('\t')[0]
        return None

    @staticmethod
    def killServer():
        """
        杀掉服务
        """
        ShellUtil.exec("hdc kill")
        pass

    @staticmethod
    def clearPhoneLog():
        """
        清除手机里缓存的日志文件
        """
        ShellUtil.exec("hdc shell hilog -w stop")
        ShellUtil.exec("hdc shell rm /data/log/hilog/*.gz")
        ShellUtil.exec("hdc shell hilog -w start -t kmsg -n 100")
        ShellUtil.exec("hdc shell hilog -w start -n 1000")

        ShellUtil.exec("hdc shell rm /data/log/eventlog")
        ShellUtil.exec("hdc shell rm /data/log/input-log")
        ShellUtil.exec("hdc shell rm /data/log/hitrace")
        ShellUtil.exec("hdc shell rm /data/log/faultlog")
        HarmonyOperator.closeSwitch()
        pass

    @staticmethod
    def closeSwitch():
        """
        关闭限流等开关
        """
        ShellUtil.exec("hdc shell hilog -r")
        ShellUtil.exec("hdc shell hilog -w start")
        ShellUtil.exec("hdc shell hilog -Q pidoff")
        ShellUtil.exec("hdc shell hilog -Q domainoff")
        ShellUtil.exec("hdc shell hilog -p off")
        ShellUtil.exec("hdc shell hilog -b d")
        ShellUtil.exec("hdc shell hilog -G 200M")
        ShellUtil.exec('hdc shell "power-shell setmode 602"')
        ShellUtil.exec('hdc shell param set persist.sys.hilog.debug.on true')
        pass

    @staticmethod
    def captureRealTimeLogs(pathPre: str):
        """
        实时抓取手机日志到指定文件
        @param pathPre 文件路径前缀
        """
        ShellUtil.exec("hdc shell hilog -r")
        fp = os.path.join(pathPre, "harmony/realtime", HarmonyOperator.getDeviceId(),
                          f'hilog.{DateUtil.nowTime(DATE_TIME_COMPACT)}.txt')
        FileUtil.mkFilePath(fp)
        logFile = open(fp, 'w')
        ShellUtil.run("hdc hilog", logFile)
        return logFile
