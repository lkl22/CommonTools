# -*- coding: utf-8 -*-
# python 3.x
# Filename: LogUtil.py
# 定义一个DomXmlUtil工具类实现xml操作相关的功能
import os

from util.LogUtil import *
# 导入minidom
from xml.dom import minidom
from xml.dom.minidom import Document, Node
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
    def readXml(fp, encoding='utf-8'):
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
            LogUtil.e('readXml 错误信息：', err)
            return None

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
                document.writexml(fh, indent=indent, addindent=addindent, newl=newl, encoding=encoding)
                LogUtil.d('xml写入{0} OK!'.format(fp))
        except Exception as err:
            LogUtil.e('writeXml 错误信息：', err)

    @staticmethod
    def cloneNode(srcNode: Node, dstDom: Document) -> Node:
        """
        从源node克隆一个到目标dom
        :param srcNode: 源node
        :param dstDom: 目标dom
        :return: 新node
        """
        if srcNode.nodeType == Node.TEXT_NODE:
            return dstDom.createTextNode(srcNode.data)
        elif srcNode.nodeType == Node.COMMENT_NODE:
            return dstDom.createComment(srcNode.data)
        elif srcNode.nodeType == Node.ELEMENT_NODE:
            newNode = dstDom.createElement(srcNode.tagName)
            attrs = srcNode._get_attributes()
            for a_name in attrs.keys():
                newNode.setAttribute(a_name, attrs[a_name].value)
            DomXmlUtil.elementAddChildNodes(srcNode.childNodes, dstDom, newNode)
            return newNode
        pass

    @staticmethod
    def elementAddChildNodes(srcNodes: [Node], dstDom: Document, dstElement: Element):
        """
        向element中添加child nodes
        :param srcNodes: 源nodes
        :param dstDom: 目标dom
        :param dstElement: 目标element
        """
        lastNode: minidom.Node = None
        dstChildNodes = dstElement.childNodes
        if dstChildNodes:
            # 获取最后一个node
            lastNode = dstChildNodes[-1]
        for srcNode in srcNodes:
            newNode = DomXmlUtil.cloneNode(srcNode, dstDom)
            # 建立新的链表关系
            if lastNode:
                lastNode.nextSibling = newNode
                newNode.previousSibling = lastNode
            else:
                newNode.previousSibling = None
            newNode.nextSibling = None
            lastNode = newNode
            # node添加进element
            dstElement.appendChild(newNode)
        pass

    @staticmethod
    def mergeElementChildNodes(srcElement, dstDom: Document, dstElement):
        """
        合并两个element下到child nodes
        :param srcElement: 源element
        :param dstDom: 目标dom
        :param dstElement: 目标element
        """
        DomXmlUtil.elementAddChildNodes(srcElement.childNodes, dstDom, dstElement)

    @staticmethod
    def mergeDocument(srcDom: Document, dstDom: Document):
        """
        合并两个dom根节点下到nodes
        :param srcDom: 源dom
        :param dstDom: 目标dom
        """
        DomXmlUtil.mergeElementChildNodes(srcDom.documentElement, dstDom, dstDom.documentElement)

    @staticmethod
    def mergeXml(srcFp, dstFp):
        """
        合并两个xml文件
        :param srcFp: 源xml文件
        :param dstFp: 目标xml文件
        """
        srcDom = DomXmlUtil.readXml(srcFp)
        dstDom = DomXmlUtil.readXml(dstFp)
        if srcDom and dstDom:
            DomXmlUtil.mergeDocument(srcDom, dstDom)
            DomXmlUtil.writeXml(dstDom, dstFp)


if __name__ == "__main__":
    # dom = DomXmlUtil.readXml("/Users/likunlun/PycharmProjects/res/values/strings.xml")
    # print(dom.toxml())
    #
    # DomXmlUtil.writeXml(dom, "/Users/likunlun/PycharmProjects/res/values/223/strings2.xml")

    DomXmlUtil.mergeXml("/Users/likunlun/PycharmProjects/res/values/strings.xml",
                        "/Users/likunlun/PycharmProjects/res/values/223/strings3.xml")
