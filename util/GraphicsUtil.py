# -*- coding: utf-8 -*-
# python 3.x
# Filename: GraphicsUtil.py
# 定义一个GraphicsUtil工具类实现 Graphics 相关的功能
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsRectItem, \
    QGraphicsSimpleTextItem
from PyQt5.QtCore import QSize, QRectF, QLineF, QPointF


class GraphicsUtil:
    @staticmethod
    def createGraphicsView(parent: QWidget = None, scene: QGraphicsScene = None, fixedSize: QSize = None):
        """
        创建QGraphicsView，关联QGraphicsScene，用于显示画布
        :param parent: 父窗口
        :param scene: QGraphicsScene 场景 QGraphicsItem对象的容器
        :param fixedSize: 固定大小
        :return: QGraphicsView
        """
        qGraphicsView = QGraphicsView(parent)
        if scene:
            qGraphicsView.setScene(scene)
        if fixedSize:
            qGraphicsView.setFixedSize(fixedSize)
        return qGraphicsView

    @staticmethod
    def createGraphicsScene(bgColor: QColor = None):
        """
        创建QGraphicsScene场景，QGraphicsItem对象的容器
        A、提供管理大量图元的快速接口
        B、传播鼠标、键盘等事件给场景中的每个图元
        C、管理图元状态，如图元选择和焦点处理
        D、提供无变换的渲染功能，如打印
        :param bgColor: 背景色
        :return: QGraphicsScene
        """
        scene = QGraphicsScene()
        if bgColor:
            scene.setBackgroundBrush(bgColor)
        return scene

    @staticmethod
    def createGraphicsLineItem(lineF: QLineF = None, pen: QPen = None):
        """
        创建线 QGraphicsLineItem
        :param lineF: 线的坐标大小 相对于 QGraphicsScene 坐标系
        :param pen: 画笔
        :return: QGraphicsLineItem
        """
        line = QGraphicsLineItem()
        GraphicsUtil.updateGraphicsLineItem(line, lineF, pen)
        return line

    @staticmethod
    def updateGraphicsLineItem(line: QGraphicsLineItem, lineF: QLineF = None, pen: QPen = None):
        """
        更新线 QGraphicsLineItem属性
        :param line: QGraphicsLineItem
        :param lineF: 线的坐标大小
        :param pen: 画笔
        """
        if lineF:
            line.setLine(lineF)
        if pen:
            line.setPen(pen)

    @staticmethod
    def createGraphicsRectItem(rectF: QRectF = None, pen: QPen = None, brush: QBrush = None):
        """
        创建矩形GraphicsItem
        :param rectF: 矩形rect 相对于 QGraphicsScene 坐标系
        :param pen: 边框画笔
        :param brush: 填充画刷
        :return: QGraphicsRectItem
        """
        rect = QGraphicsRectItem()
        GraphicsUtil.updateGraphicsRectItem(rect, rectF, pen, brush)
        return rect

    @staticmethod
    def updateGraphicsRectItem(rect: QGraphicsRectItem, rectF: QRectF = None, pen: QPen = None, brush: QBrush = None):
        """
        更新QGraphicsRectItem属性
        :param rect: QGraphicsRectItem
        :param rectF: 矩形rect
        :param pen: 边框画笔
        :param brush: 填充画刷
        """
        if rectF:
            rect.setRect(rectF)
        if pen:
            rect.setPen(pen)
        if brush:
            rect.setBrush(brush)

    @staticmethod
    def createGraphicsSimpleTextItem(text: str = None, color: QColor = None, pos: QPointF = None, fontSize: int = 18):
        """
        创建普通文本 QGraphicsSimpleTextItem
        :param text: 显示文字
        :param color: 文字颜色
        :param pos: 文字位置
        :param fontSize: 字体大小
        :return: QGraphicsSimpleTextItem
        """
        textItem = QGraphicsSimpleTextItem()
        GraphicsUtil.updateGraphicsSimpleTextItem(textItem, text, color, pos, fontSize)
        return textItem

    @staticmethod
    def updateGraphicsSimpleTextItem(textItem: QGraphicsSimpleTextItem, text: str = None, color: QColor = None,
                                     pos: QPointF = None, fontSize: int = 18):
        """
        更新普通文本QGraphicsSimpleTextItem属性
        :param textItem: QGraphicsSimpleTextItem
        :param text: 显示文字
        :param color: 文字颜色
        :param pos: 文字位置
        :param fontSize: 字体大小
        """
        if text:
            textItem.setText(text)
        if fontSize:
            font = QFont()
            font.setPointSize(fontSize)
            textItem.setFont(font)
        if color:
            textItem.setBrush(color)
        if pos:
            textItem.setPos(pos)
