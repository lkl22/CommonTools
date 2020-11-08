# -*- coding: utf-8 -*-
# python 3.x
# Filename: Uiautomator.py
# 定义一个Uiautomator类实现自动化测试相关的功能
import sys
from typing import Union, Optional

from uiautomator2 import Direction, Selector, UiObject

from util.FileUtil import *
import uiautomator2 as u2

sys.path.append("../")


class Uiautomator:
    def __init__(self, addr=None):
        try:
            self.addr = addr
            self.d: u2.Device = None
            self.info = None
            self.d = u2.connect(addr)
            self.info = self.d.info
            LogUtil.d("设备信息：", self.info)
        except Exception as err:
            self.info = None
            LogUtil.e('Uiautomator init 错误信息：', err)

    def checkDevice(self):
        """
        检查是否连接上设备，未连接上尝试重新连接一次
        :return: True 连接成功
        """
        if self.d:
            return True
        LogUtil.e("checkDevice", "cant find device reInit.")
        self.__init__(self.addr)
        if self.d:
            return True
        return False

    def deviceInfo(self):
        """
        设备信息
        :return: deviceInfo {'currentPackageName': 'com.miui.home',
                             'displayHeight': 1920,
                             'displayRotation': 0,
                             'displaySizeDpX': 360,
                             'displaySizeDpY': 640,
                             'displayWidth': 1080,
                             'productName': 'cancro_wc_lte',
                             'screenOn': True, 'sdkInt': 23,
                             'naturalOrientation': True}
        """
        if self.checkDevice() and self.info:
            return self.info
        return 'None'

    def windowSize(self):
        """
        获取屏幕size
        :return: {w, h}
        """
        if self.checkDevice():
            return self.d.window_size()
        return None

    def reConnect(self, addr=None):
        """
        重新连接设备
        :param addr: 设备addr
        """
        self.__init__(addr)

    def serial(self):
        """
        获取连接设备的serial
        :return: 连接设备的serial
        """
        if self.checkDevice():
            return self.d.serial
        return ''

    def appInfo(self, packageName: str):
        """
        Get app info
        :param packageName: package name
        :return: example: {'packageName': 'com.lkl.androidstudy', 'mainActivity': 'com.lkl.androidstudy.MainActivity', 'label': 'AndroidStudy', 'versionName': '1.0.1', 'versionCode': 1, 'size': 4176416}
        """
        if self.checkDevice():
            try:
                return self.d.app_info(packageName)
            except Exception as err:
                LogUtil.e('appInfo 错误信息：', err)

    def push(self, src, dst: str, mode=0o644):
        """
        Push file into device
        :param src: (path or fileobj): source file
        :param dst: (str): destination can be folder or file path
        :param mode: file access mode
        :return: True push success
        """
        if self.checkDevice():
            try:
                res = self.d.push(src, dst, mode)
                LogUtil.d("push result: ", res)
                return True
            except Exception as err:
                LogUtil.e('push 错误信息：', err)
        return False

    def pull(self, src: str, dst: str):
        """
        Pull file from device to local
        :param src: 手机设备上的源文件
        :param dst: 电脑上本地目标文件
        :return: True pull success False pull failed
        """
        if self.checkDevice():
            try:
                self.d.pull(src, dst)
                return True
            except Exception as err:
                LogUtil.e('pull 错误信息：', err)
        return False

    def press(self, key: Union[int, str], meta=None):
        """
        press key via name or key code. Supported key name includes:
            home, back, left, right, up, down, center, menu, search, enter,
            delete(or del), recent(recent apps), volume_up, volume_down,
            volume_mute, camera, power.
        :param key: press key via name or key code.
        :param meta: META
        :return: True press success
        """
        if self.checkDevice():
            try:
                res = self.d.press(key, meta)
                LogUtil.d("press result: ", res)
                return res
            except Exception as err:
                LogUtil.e('press 错误信息：', err)
        return False

    def click(self, x: Union[float, int] = 0, y: Union[float, int] = 0, xpath=None):
        """
        click 屏幕坐标（x，y）
        :param x: x坐标
        :param y: y坐标
        :param xpath: xpath
        :return: True click success
        """
        if self.checkDevice():
            try:
                if xpath:
                    XPath = self.d.xpath(xpath)
                    if XPath.exists:
                        XPath.click()
                        return True
                self.d.click(x, y)
                return True
            except Exception as err:
                LogUtil.e('click 错误信息：', err)
        return False

    def doubleClick(self, x: Union[float, int] = 0, y: Union[float, int] = 0, duration=0.1, xpath=None):
        """
        double click position
        :param x: x坐标
        :param y: y坐标
        :param duration: 两次点击间隔时间
        :param xpath: xpath
        :return: True doubleClick success
        """
        if self.checkDevice():
            try:
                if xpath:
                    XPath = self.d.xpath(xpath)
                    if XPath.exists:
                        (x, y) = XPath.get_last_match().center()
                        self.d.double_click(x, y, duration)
                        return True
                self.d.double_click(x, y, duration)
                return True
            except Exception as err:
                LogUtil.e('doubleClick 错误信息：', err)
        return False

    def longClick(self, x: Union[float, int] = 0, y: Union[float, int] = 0, duration: float = .5, xpath=None):
        """
        long click at arbitrary coordinates
        :param x: x坐标
        :param y: y坐标
        :param duration: seconds of pressed
        :param xpath: xpath
        :return: True longClick success
        """
        if self.checkDevice():
            try:
                if xpath:
                    XPath = self.d.xpath(xpath)
                    if XPath.exists:
                        XPath.long_click()
                        return True
                self.d.long_click(x, y, duration)
                return True
            except Exception as err:
                LogUtil.e('longClick 错误信息：', err)
        return False

    def swipe(self, fx, fy, tx, ty, duration: Optional[float] = None, steps: Optional[int] = None):
        """
        滑动
        :param fx: from position x
        :param fy: from position y
        :param tx: to position x
        :param ty: to position y
        :param duration: seconds of swipe
        :param steps: 1 steps is about 5ms, if set, duration will be ignore
        :return: True swipe success
        """
        if self.checkDevice():
            try:
                res = self.d.swipe(fx, fy, tx, ty, duration, steps)
                LogUtil.d("swipe result: ", res)
                return res
            except Exception as err:
                LogUtil.e('swipe 错误信息：', err)
        return False

    def swipeExt(self, direction: Union[Direction, str], scale: float = 0.9, box: Union[None, tuple] = None):
        """
        滑动
        :param direction: (str) one of "left", "right", "up", "bottom" or Direction.LEFT
        :param scale: percent of swipe, range (0, 1.0]
        :param box: None or [lx, ly, rx, ry]
        :return: True swipeExt success
        """
        if self.checkDevice():
            try:
                self.d.swipe_ext(direction, scale, box)
                return True
            except Exception as err:
                LogUtil.e('swipe_ext 错误信息：', err)
        return False

    def screenshot(self, filename: Optional[str] = None, format="pillow"):
        """
        Take screenshot of device
        :param filename: saved filename, if filename is set then return None
        :param format: used when filename is empty. one of ["pillow", "opencv", "raw"]
        :return: PIL.Image.Image, np.ndarray (OpenCV format) or None

        Examples:
            screenshot("saved.jpg")
            screenshot().save("saved.png")
            cv2.imwrite('saved.jpg', screenshot(format='opencv'))
        """
        if self.checkDevice():
            try:
                return self.d.screenshot(filename, format)
            except Exception as err:
                LogUtil.e('screenshot 错误信息：', err)
        return None

    def existsByXpath(self, xpath):
        """
        通过xpath方式判断界面元素是否存在
        :param xpath: xpath
        :return: True 存在
        """
        if self.checkDevice():
            try:
                XPath = self.d.xpath(xpath)
                return XPath.exists
            except Exception as err:
                LogUtil.e('existsByXpath 错误信息：', err)
        return False

    def selector(self, className=None, text=None, resourceId=None) -> UiObject:
        if self.checkDevice():
            try:
                # return self.d(text="SECOND")
                if resourceId and text and className:
                    return self.d(className=className, text=text, resourceId=resourceId)
                elif resourceId and text:
                    return self.d(text=text, resourceId=resourceId)
                elif resourceId and className:
                    return self.d(className=className, resourceId=resourceId)
                elif className and text:
                    return self.d(className=className, text=text)
                elif className:
                    return self.d(className=className)
                elif text:
                    return self.d(text=text)
                elif resourceId:
                    return self.d(resourceId=resourceId)
            except Exception as err:
                LogUtil.e('selector 错误信息：', err)
        return None


if __name__ == '__main__':
    u = Uiautomator()
    # print(u.appInfo('com.lkl.androidstudy'))
    # print(u.push("/Users/likunlun/PycharmProjects/CommonTools/tem.txt", "/sdcard/tmp.txt"))
    # print(u.pull("/sdcard/tmp.txt", "tmp.txt"))
    # print(u.press("home"))
    # print(u.press("recent"))
    # print(u.click(2, 5))
    print(u.longClick(
        xpath='//*[@content-desc="设置"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]'))

    # print(u.swipe(10, 50, 100, 50))
    # print(u.swipeExt("right"))
    # print(u.swipeExt("right", 0.8))
    # print(u.swipeExt("right", box=(0, 0, 100, 100)))
    # print(u.swipeExt(Direction.FORWARD))  # 页面下翻, 等价于 d.swipe_ext("up")

    # u.screenshot('test.jpg')
    # print(u.selector(text='next').exists)
    # print(u.selector(resourceId='com.lkl.androidstudy:id/button_first').info)

    # print(u.deviceInfo())
    # print(u.serial())
    print('finished')
    pass
