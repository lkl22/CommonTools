# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogUtil.py
# 定义一个DomXmlUtil工具类实现xml操作相关的功能
import os

from util.LogUtil import *
# 导入minidom
from xml.dom import minidom
from xml.dom.minidom import Document
from xml.dom.minidom import Element


# 解决"转义了的问题
def fix_write_data(writer, data):
    "Writes datachars to writer."
    if data:
        data = data.replace("&", "&amp;").replace("<", "&lt;"). \
            replace(">", "&gt;")
        writer.write(data)


# 解决xml文件头换行问题
def fix_dom_writexml(self, writer, indent="", addindent="", newl="", encoding=None):
    if encoding is None:
        writer.write('<?xml version="1.0" ?>\n')
    else:
        writer.write('<?xml version="1.0" encoding="%s"?>\n' % encoding)
    for node in self.childNodes:
        node.writexml(writer, indent, addindent, newl)


minidom._write_data = fix_write_data
minidom.Document.writexml = fix_dom_writexml


class DomXmlUtil:
    @staticmethod
    def readXml(fp, encoding='utf-8') -> Document:
        """
        读取xml文件
        :param fp: 文件path
        :param encoding: 文件编码格式
        :return: Document对象
        """
        try:
            with open(fp, 'r', encoding=encoding) as fh:
                # parse()获取DOM对象
                return minidom.parse(fh)
        except Exception as err:
            LogUtil.e('错误信息：', err)

    @staticmethod
    def writeXml(document: Document, fp, indent='', addindent='', newl='', encoding='utf-8'):
        """
        将Document写入xml文件
        :param document: document
        :param fp: 文件path
        :param indent: 根节点的缩进格式
        :param addindent: 其他子节点的缩进格式
        :param newl: 换行格式
        :param encoding: xml内容的编码
        """
        try:
            path, fn = os.path.split(fp)  # 分离文件名和路径
            if not os.path.exists(path):
                os.makedirs(path)  # 创建路径
            with open(fp, 'w', encoding=encoding) as fh:
                # writexml()第一个参数是目标文件对象，第二个参数是根节点的缩进格式，第三个参数是其他子节点的缩进格式，
                # 第四个参数制定了换行格式，第五个参数制定了xml内容的编码。
                document.writexml(fh, indent=indent, addindent=addindent, newl=newl, encoding=encoding)
                print('写入xml OK!')
        except Exception as err:
            LogUtil.e('错误信息：', err)


if __name__ == "__main__":
    dom = DomXmlUtil.readXml("/Users/likunlun/PycharmProjects/res/values/strings.xml")
    print(dom.toxml())

    DomXmlUtil.writeXml(dom, "/Users/likunlun/PycharmProjects/res/values/223/strings3.xml")
