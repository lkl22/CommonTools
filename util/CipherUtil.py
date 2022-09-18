# -*- coding: utf-8 -*-
# python 3.x
# Filename: CipherUtil.py
# 定义一个CipherUtil工具类实现数据加解密相关的功能
from Cryptodome.Cipher import DES, AES
import binascii
from util.LogUtil import *


class CipherUtil:
    @staticmethod
    def encrypt(data, key: str, encryptType="AES"):
        """
        对数据进行加密
        :param data: 原始数据
        :param key: 加解密数据时的key
        :param encryptType: 加解密类型，可选值 AES、DES
        :return: 加密后的数据
        """
        try:
            if encryptType == "AES":
                encryptObj = AES.new(key.encode('utf-8'), AES.MODE_ECB)  # ECB模式
                k = 16
            else:
                encryptObj = DES.new(key.encode('utf-8'), DES.MODE_ECB)  # ECB模式
                k = 8
            padSize = k - len(data) % k
            data += padSize * chr(padSize)
            # LogUtil.d(padSize, data, data[:-ord(data[-1])])
            encryptText = encryptObj.encrypt(data.encode('utf-8'))
            encryptResult = binascii.b2a_hex(encryptText)  # b2a_hex
            return encryptResult.decode('utf-8')
        except Exception as err:
            LogUtil.e('encrypt 错误信息：', err)
            return None

    @staticmethod
    def decrypt(data, key: str, decryptType="AES"):
        """
        对数据进行解密
        :param data: 加密后的数据
        :param key: 加解密数据时的key
        :param decryptType: 加解密类型，可选值 AES、DES
        :return: 原始数据
        """
        try:
            if decryptType == "AES":
                decryptObj = AES.new(key.encode('utf-8'), AES.MODE_ECB)  # ECB模式
            else:
                decryptObj = DES.new(key.encode('utf-8'), DES.MODE_ECB)  # ECB模式
            encryptoText = binascii.a2b_hex(data)  # a2b_hex
            decryptResult = decryptObj.decrypt(encryptoText).decode('utf-8')
            return decryptResult[:-ord(decryptResult[-1])]
        except Exception as err:
            LogUtil.e('decrypt 错误信息：', err)
            return None


if __name__ == "__main__":
    LogUtil.d(CipherUtil.encrypt("addfaaaaaddfaddd", "1234567812345678"))
    LogUtil.d(CipherUtil.decrypt('f653392b65fa6795c2ac83d4b4acef3bd96aa42b59151a9e9b5925fc9d95adaf',
                                 "1234567812345678"))

    LogUtil.d(CipherUtil.encrypt("addfaaaaaddfaddd", "12345678", "DES"))
    LogUtil.d(CipherUtil.decrypt('cf63c95c39b8d93d547c0c485f7c0856feb959b7d4642fcb',
                                 "12345678", "DES"))
    pass
