# -*- coding: utf-8 -*-
# python 3.x
# Filename: OperaIni.py
# 定义一个OperaIni工具类实现ini相关的功能
import sys
import configparser
from util.LogUtil import *
from util.FileUtil import *

sys.path.append("../")


class OperaIni:
    def __init__(self, filePath=None):
        if filePath:
            self.filePath = filePath
        else:
            self.filePath = FileUtil.getProjectPath() + '/config/BaseConfig.ini'
        self.configParser = configparser.ConfigParser()
        self.data = self.readIni()

    def readIni(self):
        """
        读取ini配置文件
        :return: configparser
        """
        self.configParser.read(self.filePath)
        return self.configParser

    # 通过key获取对应的value
    def getValue(self, key, section=None):
        """
        获取指定key的配置值
        :param key: key
        :param section: section
        :return: value
        """
        if section is None:
            section = 'CommonConfig'
        try:
            value = self.data.get(section, key)
        except Exception as err:
            LogUtil.e('OperaIni getValue 错误信息：', err)
            value = None
        return value

    def addSection(self, section):
        """
        添加section
        :param section: section
        """
        if not self.configParser.has_section(section):
            self.configParser.add_section(section)

    def addItem(self, section, option, value):
        """
        添加配置item
        :param section: section
        :param option: option
        :param value: value
        """
        self.addSection(section)
        self.configParser.set(section, option, value)

    def removeItem(self, section, option):
        """
        移除指定的item
        :param section: section
        :param option: option
        """
        try:
            self.configParser.remove_option(section, option)
        except Exception as err:
            LogUtil.e('OperaIni removeItem 错误信息：', err)

    def clearIni(self):
        """
        清空配置
        """
        sections = self.configParser.sections()
        for item in sections:
            self.configParser.remove_section(item)

    def saveIni(self):
        """
        将配置写入文件
        """
        # Writing our configuration file to 'example.cfg'
        with open(self.filePath, 'w') as configfile:
            self.configParser.write(configfile)


if __name__ == '__main__':
    operaIni = OperaIni("../resources/config/BaseConfig.ini")
    # print(operaIni.getValue("password_et", "main_element"))
    # operaIni.clearIni()
    operaIni.addSection('android')
    operaIni.addItem('android', 'color_normal_res', 'ss')
    operaIni.addItem('android', 'color_dark_res', 'fff')
    operaIni.saveIni()

    print(FileUtil.getProjectPath())
