# -*- coding: utf-8 -*-
# python 3.x
# Filename: TinifyUtil.py
# 定义一个TinifyUtil工具类实现图片压缩相关的功能

from util.LogUtil import LogUtil
import tinify
import threading


class TinifyUtil:
    @staticmethod
    def validate(apiKey: str):
        """
        验证用户的api key是否有效
        :param apiKey: 用户的api key
        :return: True 有效用户
        """
        try:
            tinify.key = apiKey
            return tinify.validate()
        except tinify.Error as e:
            # Validation of API key failed.
            LogUtil.e('TinifyUtil Validation of API key failed. 错误信息：', e)
            return False

    @staticmethod
    def compressing(apiKey: str, sourceFp: str, toFp: str, preserves: [] = None, resizeParams: {} = None):
        """
        获取指定账户当前剩余使用数量
        :param apiKey: 用户的api key
        :param sourceFp: 原文件
        :param toFp: 压缩后文件
        :param preserves: 需要保留的metadata 取值["copyright", "creation", "location"]; copyright 版权 creation 创建日期时间 location 位置信息
        :param resizeParams: Resizing images eg: {"method": "fit", "width": 150, "height": 100}
            method: scale -> Scales the image down proportionally. You must provide either a target width or a target height, but not both. The scaled image will have exactly the provided width or height.
                    fit -> Scales the image down proportionally so that it fits within the given dimensions. You must provide both a width and a height. The scaled image will not exceed either of these dimensions.
                    cover -> Scales the image proportionally and crops it if necessary so that the result has exactly the given dimensions. You must provide both a width and a height. Which parts of the image are cropped away is determined automatically. An intelligent algorithm determines the most important areas of your image.
                    thumb -> A more advanced implementation of cover that also detects cut out images with plain backgrounds. The image is scaled down to the width and height you provide. If an image is detected with a free standing object it will add more background space where necessary or crop the unimportant parts. This feature is new and we’d love to hear your feedback!
        :return: 处理结果
        """
        try:
            # Use the Tinify API client.
            tinify.key = apiKey
            source = tinify.from_file(sourceFp)
            if preserves:
                source = source.preserve(preserves)
            if resizeParams:
                source = source.resize(**resizeParams)
            LogUtil.d("compressing", "sourceFp {} toFp {} preserves {} resizeParams {}".format(sourceFp, toFp, preserves, resizeParams))
            source.to_file(toFp)
            return "Success"
            pass
        except tinify.AccountError as e:
            LogUtil.e("TinifyUtil compressing", "The error message is: %s" % e.message)
            return "Verify your API key and account limit. msg: {}".format(e.message)
        except tinify.ClientError as e:
            LogUtil.e("TinifyUtil compressing", "The error message is: %s" % e.message)
            return "Check your source image and request options. msg: {}".format(e.message)
            pass
        except tinify.ServerError as e:
            LogUtil.e("TinifyUtil compressing", "The error message is: %s" % e.message)
            return "Temporary issue with the Tinify API. msg: {}".format(e.message)
            pass
        except tinify.ConnectionError as e:
            LogUtil.e("TinifyUtil compressing", "The error message is: %s" % e.message)
            return "A network connection error occurred. msg: {}".format(e.message)
            pass
        except Exception as e:
            LogUtil.e("TinifyUtil compressing", "The error message is: %s" % e)
            return "Something else went wrong, unrelated to the Tinify API. msg: {}".format(e)
            pass

def compressingPic(pic: str):
    key = "N2Nm578kdlJfXbQqwCk9pHL9gmzHdJMv"
    print(TinifyUtil.compressing(key, pic, pic))
    print("compressingPic", pic)

if __name__ == "__main__":
    key = "N2Nm578kdlJfXbQqwCk9pHL9gmzHdJMv"
    # print(TinifyUtil.validate(key))
    # print(TinifyUtil.compressing(key, "0C1A8658.JPG", "2.jpg"))
    # print(TinifyUtil.compressing(key, "2.jpg", "3.jpg", ["copyright", "location"]))
    thread1 = threading.Thread(target=compressingPic, args=("0C1A8656.JPG",), kwargs={})
    thread2 = threading.Thread(target=compressingPic, args=('0C1A8658.JPG',))
    thread1.start()
    thread2.start()
    print("thread start.")
    thread1.join()
    thread2.join()
    print("exit")
    # print(TinifyUtil.compressing(key, "3.jpg", "4.jpg", resizeParams={"method": "fit", "width": 150, "height": 100}))
