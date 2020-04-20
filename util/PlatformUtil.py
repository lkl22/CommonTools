# -*- coding: utf-8 -*-
# python 3.x
# Filename: PlatformUtil.py
# 定义一个PlatformUtil工具类实现平台相关的功能
import platform


class PlatformUtil:
    @staticmethod
    def isMac():
        """
        判断是否是mac操作系统
        :return: true Mac 操作系统
        """
        if platform.platform().startswith('macOS'):
            return True
        return False


# if __name__ == "__main__":
#     print(platform.system())
#     print(platform.architecture())
#     print(platform.mac_ver())
#     print(platform.platform())
#     print(PlatformUtil.isMac())
