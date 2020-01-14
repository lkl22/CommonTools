# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogUtil.py
# 定义一个LogUtil工具类实现Log相关的功能


class LogUtil:
    @staticmethod
    def log(color, tag, *args, **kwargs):
        log = "\033[1;%dm" % color
        log += "*****************************************************************************************************"
        log += "\n{0}"
        i = 1
        for arg in args:
            log += " {%d}" % i
            i += 1
        if kwargs:
            log += " {%d}" % i

        log += "\n*****************************************************************************************************"
        log += "\n\033[0m"
        print(log.format(tag, *args, **kwargs))

    @staticmethod
    def i(tag, *args, **kwargs):
        LogUtil.log(30, tag, *args, **kwargs)

    @staticmethod
    def d(tag, *args, **kwargs):
        LogUtil.log(34, tag, *args, **kwargs)

    @staticmethod
    def w(tag, *args, **kwargs):
        LogUtil.log(35, tag, *args, **kwargs)

    @staticmethod
    def e(tag, *args, **kwargs):
        LogUtil.log(31, tag, *args, **kwargs)


if __name__ == "__main__":
    LogUtil.i("hello:", 12, 56, {"d": 12})
    LogUtil.d("hello:", 12, 56, {"d": 12})
    LogUtil.w("hello:", 12, 56, {"d": 12})
    LogUtil.e("hello:", 12, 56, {"d": 12})
