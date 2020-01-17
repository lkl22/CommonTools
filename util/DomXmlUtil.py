# -*- coding: utf-8 -*-
# python 3.x
# Filename: DomXmlUtil.py
# 定义一个DomXmlUtil工具类实现xml操作相关的功能
import os

from util.LogUtil import *
from util.DataTypeUtil import *
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
        合并两个element下的child nodes
        :param srcElement: 源element
        :param dstDom: 目标dom
        :param dstElement: 目标element
        """
        DomXmlUtil.elementAddChildNodes(srcElement.childNodes, dstDom, dstElement)

    @staticmethod
    def mergeDocument(srcDom: Document, dstDom: Document):
        """
        合并两个dom根节点下的nodes
        :param srcDom: 源dom
        :param dstDom: 目标dom
        """
        DomXmlUtil.mergeElementChildNodes(srcDom.documentElement, dstDom, dstDom.documentElement)

    @staticmethod
    def mergeXml(srcFp, dstFp):
        """
        合并两个xml文件中documentElement下的所有子nodes
        :param srcFp: 源xml文件
        :param dstFp: 目标xml文件
        """
        srcDom = DomXmlUtil.readXml(srcFp)
        dstDom = DomXmlUtil.readXml(dstFp)
        if srcDom and dstDom:
            DomXmlUtil.mergeDocument(srcDom, dstDom)
            DomXmlUtil.writeXml(dstDom, dstFp)

    @staticmethod
    def createDom(rootTag='resources', qualifiedName='xmlns:android',
                  value='http://schemas.android.com/apk/res/android'):
        """
        创建一个只有root tag的空Document
        :param rootTag: rootTag
        :param qualifiedName: qualifiedName
        :param value: value
        :return: Document
        """
        # 1.创建DOM树对象
        document = Document()
        # 2.创建根节点。每次都要用DOM对象来创建任何节点。
        rootNode = document.createElement(rootTag)
        rootNode.setAttributeNS("", qualifiedName, value)
        # 3.用DOM对象添加根节点
        document.appendChild(rootNode)
        return document

    @staticmethod
    def findElements(document: Document, tagName, attrName='', attrValue=''):
        """
        查找document下的Elements
        :param document: document
        :param tagName: tagName
        :param attrName: attrName
        :param attrValue: attrValue
        :return: 查找到到元素列表
        """
        elements: [Element] = document.getElementsByTagName(tagName)
        res = []
        if elements:
            for element in elements:
                if attrName:
                    attribute = element.getAttribute(attrName)
                    if attribute:
                        if attrValue:
                            if attribute == attrValue:
                                res.append(element)
                        else:
                            res.append(element)
                else:
                    res.append(element)
        return res

    @staticmethod
    def removeElements(document: Document, tagName, attrName='', attrValue=''):
        """
        删除document根节点下指定到元素，并返回删除的元素列表
        :param document: document
        :param tagName: tagName
        :param attrName: attrName
        :param attrValue: attrValue
        :return: 删除的元素列表
        """
        removeElements = DomXmlUtil.findElements(document, tagName, attrName, attrValue)
        res = []
        if removeElements:
            for element in removeElements:
                if element.previousSibling.nodeType == Node.TEXT_NODE:
                    res.append(document.documentElement.removeChild(element.previousSibling))
                res.append(document.documentElement.removeChild(element))
        return res

    @staticmethod
    def modifyElements(srcDom: Document, dstDom: Document, tagName, attrName, attrValue, isCopy=True):
        """
        复制/移动srcDom中指定的Elements到目标dom
        :param srcDom: srcDom
        :param dstDom: dstDom
        :param tagName: tagName
        :param attrName: attrName
        :param attrValue: attrValue []处理一批tag，attrName相同attrValue不同的数据
        :param isCopy: True 复制 False 移动
        """
        nodes = []
        if isCopy:
            elements = []
            if DataTypeUtil.isList(attrValue):
                for attr in attrValue:
                    es = DomXmlUtil.findElements(srcDom, tagName, attrName, attr)
                    elements.extend(es)
            else:
                elements = DomXmlUtil.findElements(srcDom, tagName, attrName, attrValue)
            if elements:
                for element in elements:
                    if element.previousSibling.nodeType == Node.TEXT_NODE:
                        nodes.append(element.previousSibling)
                    nodes.append(element)
        else:
            nodes = []
            if DataTypeUtil.isList(attrValue):
                for attr in attrValue:
                    es = DomXmlUtil.removeElements(srcDom, tagName, attrName, attr)
                    nodes.extend(es)
            else:
                nodes = DomXmlUtil.removeElements(srcDom, tagName, attrName, attrValue)
        if nodes:
            nodes.append(dstDom.createTextNode('\n'))
            DomXmlUtil.elementAddChildNodes(nodes, dstDom, dstDom.documentElement)

    @staticmethod
    def modifyDomElements(srcFp, dstFp, tagName, attrName, attrValue, isCopy=True):
        """
        复制/移动src xml中指定的Elements到目标xml
        :param srcFp: src xml path
        :param dstFp: dst xml path
        :param tagName: tagName
        :param attrName: attrName
        :param attrValue: attrValue []处理一批tag，attrName相同attrValue不同的数据
        :param isCopy: True 复制 False 移动
        """
        srcDom = DomXmlUtil.readXml(srcFp)
        dstDom = None
        if os.path.exists(dstFp):
            dstDom = DomXmlUtil.readXml(dstFp)
        else:
            root = srcDom.documentElement
            dstDom = Document()
            newNode = dstDom.createElement(root.tagName)
            attrs = root._get_attributes()
            for a_name in attrs.keys():
                newNode.setAttribute(a_name, attrs[a_name].value)
            dstDom.appendChild(newNode)
        DomXmlUtil.modifyElements(srcDom, dstDom, tagName, attrName, attrValue, isCopy)
        if not isCopy:
            DomXmlUtil.writeXml(srcDom, srcFp)
        DomXmlUtil.writeXml(dstDom, dstFp)



if __name__ == "__main__":
    # dom = DomXmlUtil.readXml("/Users/likunlun/PycharmProjects/res/values/strings.xml")
    # dom1 = DomXmlUtil.readXml("/Users/likunlun/PycharmProjects/res/values/colors.xml")
    # print(dom.toxml())
    #
    # DomXmlUtil.writeXml(dom, "/Users/likunlun/PycharmProjects/res/values/223/strings2.xml")

    # DomXmlUtil.mergeXml("/Users/likunlun/PycharmProjects/res/values/strings.xml",
    #                     "/Users/likunlun/PycharmProjects/res/values/223/strings3.xml")

    # dom = DomXmlUtil.createDom()
    # DomXmlUtil.writeXml(dom, "/Users/likunlun/PycharmProjects/res/values/223/strings2.xml")
    # list = DomXmlUtil.findElements(dom, "string", 'name', 'ok')
    # for e in list:
    #     print(e.toxml())

    # list = DomXmlUtil.removeElements(dom, "string", 'name')
    # for e in list:
    #     print(e.toxml())
    # print(dom.toxml())

    # DomXmlUtil.modifyElements(dom, dom1, 'string', 'name', ['app_name', 'loaction'], False)
    # print(dom.toxml())
    # print(dom1.toxml())

    DomXmlUtil.modifyDomElements('/Users/likunlun/PycharmProjects/res/values/strings.xml',
                                 '/Users/likunlun/PycharmProjects/res/values/strings1.xml',
                                 'string', 'name', ['app_name', 'loaction'], True)
