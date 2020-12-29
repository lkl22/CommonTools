# -*- coding: utf-8 -*-
# python 3.x
# Filename: ImageUtil.py
# 定义一个ImageUtil工具类实现图片相关的功能

from util.DateUtil import *
from util.LogUtil import *
from PIL import Image, ImageChops


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
            img = Image.open(src)
            img.save(dst)
            LogUtil.d('convert {} to {} time: {}ms'.format(src, dst, DateUtil.nowTimestamp(True) - t))
            return True
        except Exception as err:
            LogUtil.e('convert 错误信息：', err)
            return False

    @staticmethod
    def isAllBackPic(srcFp, mode=2):
        """
        判断是否全黑图片
        :param srcFp: 图片路径
        :param mode: 检查方式
        :return: True 全黑图片
        """
        img = Image.open(srcFp)
        if mode == 1:
            if not img.getbbox():
                return True
        else:
            extrema = img.convert("L").getextrema()
            if extrema == (0, 0):
                return True
        return False

    @staticmethod
    def isAllWhitePic(srcFp, mode=2):
        """
        判断是否全白图片
        :param srcFp: 图片路径
        :param mode: 检查方式
        :return: True 全白图片
        """
        img = Image.open(srcFp)
        if mode == 1:
            if not ImageChops.invert(img).getbbox():
                return True
        else:
            extrema = img.convert("L").getextrema()
            if extrema == (1, 1):
                return True
        return False

    @staticmethod
    def isAllBackOrWhitePic(srcFp):
        """
        判断是否全黑/白图片
        :param srcFp: 图片路径
        :return: True 全黑/白图片
        """
        img = Image.open(srcFp)
        if sum(img.convert("L").getextrema()) in (0, 2):
            return True
        return False


if __name__ == "__main__":
    ImageUtil.convert('./test.jpg', './test11.png')
    ImageUtil.convert('./test11.png', './test22.jpg')
    pass
