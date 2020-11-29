# -*- coding: utf-8 -*-
# python 3.x
# Filename: ImageUtil.py
# 定义一个ImageUtil工具类实现图片相关的功能

from util.DateUtil import *
from util.LogUtil import *
from PIL import Image


class ImageUtil:
    @staticmethod
    def convert(src, dst):
        """
        转换图片格式
        :param src: 待转换的源图片文件名
        :param dst: 转换后的目标文件名
        :return: True 转换成功
        """
        try:
            t = DateUtil.nowTimestamp(True)
            im = Image.open(src)
            im.save(dst)
            LogUtil.d('convert {} to {} time: {}ms'.format(src, dst, DateUtil.nowTimestamp(True) - t))
            return True
        except Exception as err:
            LogUtil.e('convert 错误信息：', err)
            return False


if __name__ == "__main__":
    ImageUtil.convert('./test.jpg', './test11.png')
    ImageUtil.convert('./test11.png', './test22.jpg')
    pass
