# -*- coding: utf-8 -*-
# python 3.x
# Filename: SelectionSortDialog.py
# 定义一个SelectionSortDialog类实现选择排序算法可视化
from PyQt5.QtCore import QRectF, QPointF

from constant.ColorConst import ColorConst
from util.AutoTestUtil import *
from util.GraphicsUtil import GraphicsUtil
from util.RandomUtil import RandomUtil
from util.Uiautomator import *


class SelectionSortDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1360
    WINDOW_HEIGHT = 680
    GROUP_BOX_HEIGHT = 560

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Algorithm Visualizer Dialog")
        self.setObjectName("AlgorithmVisualizerDialog")
        self.resize(SelectionSortDialog.WINDOW_WIDTH, SelectionSortDialog.WINDOW_HEIGHT)
        self.setFixedSize(SelectionSortDialog.WINDOW_WIDTH, SelectionSortDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="选择算法可视化"))

        width = SelectionSortDialog.WINDOW_WIDTH - const.PADDING * 2

        vbox = WidgetUtil.createVBoxLayout()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       SelectionSortDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)

        self.minValue = 0
        self.maxValue = 200
        self.count = 15
        self.delay = 0.1
        self.numbers = []
        # 已经有序的元素下标
        self.orderedIndex = -1
        # 当前正在比较的元素下标
        self.currentCompareIndex = -1
        # 当前比较过程中数值最小的元素下标
        self.currentMinIndex = -1
        self.graphicsItems = []

        self.isStop = False

        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        vbox.addWidget(splitter)

        WidgetUtil.createLabel(splitter, text="排序数字个数：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(100, const.HEIGHT))
        self.numberCountSpinBox = WidgetUtil.createSpinBox(splitter, value=self.count, minValue=5, maxValue=80, step=5,
                                                           sizePolicy=sizePolicy)

        WidgetUtil.createLabel(splitter, text="数字最小值：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(100, const.HEIGHT))
        self.minValueSpinBox = WidgetUtil.createSpinBox(splitter, value=self.minValue, minValue=-1000, maxValue=50,
                                                        step=50, sizePolicy=sizePolicy)

        WidgetUtil.createLabel(splitter, text="数字最大值：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(100, const.HEIGHT))
        self.maxValueSpinBox = WidgetUtil.createSpinBox(splitter, value=self.maxValue, minValue=100, maxValue=1000,
                                                        step=50, sizePolicy=sizePolicy)

        WidgetUtil.createLabel(splitter, text="算法执行绘制间隔时长：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(100, const.HEIGHT))
        self.delaySpinBox = WidgetUtil.createSpinBox(splitter, value=self.delay * 1000, minValue=100, maxValue=10000,
                                                     step=100, sizePolicy=sizePolicy)

        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        vbox.addWidget(splitter)

        self.resetDataBtn = WidgetUtil.createPushButton(splitter, text="重置数据", onClicked=self.resetNumbers)
        self.startExecBtn = WidgetUtil.createPushButton(splitter, text="开始执行", onClicked=self.execAlgorithm)
        self.stopExecBtn = WidgetUtil.createPushButton(splitter, text="终止执行", onClicked=self.stopExecAlgorithm)
        WidgetUtil.createPushButton(splitter, text="算法解读", onClicked=self.jumpAlgoDesc)

        clickParamGroupBox = self.createAlgorithmVisualizerGroupBox(layoutWidget)
        vbox.addWidget(clickParamGroupBox)

        self.resetNumbers()

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def genRandomNumbers(self):
        self.minValue = self.minValueSpinBox.value()
        self.maxValue = self.maxValueSpinBox.value()
        self.count = self.numberCountSpinBox.value()
        self.delay = self.delaySpinBox.value() / 1000
        LogUtil.d("count: {} minValue: {} maxValue: {} ".format(self.count, self.minValue, self.maxValue))
        return RandomUtil.randIntArray(self.count, self.minValue, self.maxValue)

    def resetNumbers(self):
        self.numbers = self.genRandomNumbers()
        self.renderData()

    def createAlgorithmVisualizerGroupBox(self, parent):
        width = SelectionSortDialog.WINDOW_WIDTH - const.PADDING * 6
        box = WidgetUtil.createGroupBox(parent, title="可视化视图",
                                        minSize=QSize(width, SelectionSortDialog.GROUP_BOX_HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        box.setSizePolicy(sizePolicy)

        yPos = const.GROUP_BOX_MARGIN_TOP
        graphicsViewH = SelectionSortDialog.GROUP_BOX_HEIGHT - const.PADDING * 2
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, graphicsViewH))

        self.scene = GraphicsUtil.createGraphicsScene(ColorConst.White)
        GraphicsUtil.createGraphicsView(splitter, self.scene)

        self.sceneW = width - const.PADDING * 2
        self.sceneH = graphicsViewH - const.PADDING * 2

        legendColW = self.sceneW / 4
        legendTextList = ["未排序的元素", "排完序的元素", "当前比较的元素", "当前最小的元素"]
        legendColorList = [ColorConst.Grey, ColorConst.Red, ColorConst.LightBlue, ColorConst.Indigo]
        for i in range(0, 4):
            self.scene.addItem(
                GraphicsUtil.createGraphicsRectItem(QRectF(i * legendColW, 5, 20, 8), brush=QBrush(legendColorList[i])))
            self.scene.addItem(
                GraphicsUtil.createGraphicsSimpleTextItem(legendTextList[i], legendColorList[i],
                                                          QPointF(i * legendColW + 25, 0), 12))

        LogUtil.d("scene size", self.scene.width(), self.scene.height())
        return box

    def execAlgorithm(self):
        self.isStop = False
        self.resetDataBtn.setEnabled(False)
        self.setData(0, -1, -1)

        for i in range(0, self.count):
            # 寻找[i, n)区间里的最小值的索引
            minIndex = i
            self.setData(i, -1, minIndex)
            if self.isStop:
                break
            for j in range(i + 1, self.count):
                self.setData(i, j, minIndex)
                if self.isStop:
                    break
                if self.numbers[j] < self.numbers[minIndex]:
                    minIndex = j
                    self.setData(i, j, minIndex)

            self.swap(i, minIndex)
            self.setData(i + 1, -1, -1)

        if self.isStop:
            self.setData(0, -1, -1)
        else:
            self.setData(self.count, -1, -1)
        self.resetDataBtn.setEnabled(True)

    def stopExecAlgorithm(self):
        self.isStop = True

    def setData(self, orderedIndex=-1, currentCompareIndex=-1, currentMinIndex=-1):
        self.orderedIndex = orderedIndex
        self.currentCompareIndex = currentCompareIndex
        self.currentMinIndex = currentMinIndex

        self.renderData(False)
        self.pause(self.delay)

    def renderData(self, isReset=True):
        if isReset:
            # 清空上次的数据
            # self.scene.clear()
            if self.graphicsItems:
                for item in self.graphicsItems:
                    self.scene.removeItem(item)
            self.graphicsItems.clear()

        # 每条数据占据的总宽度
        w = self.sceneW / self.count
        # 数字的最大偏移量
        maxOffset = self.maxValue - self.minValue
        # 绘制的最大高度，最小值占据一个固定高度
        drawH = self.sceneH - const.PADDING * 5
        if isReset:
            LogUtil.e("w -> {} maxOffset -> {} sceneH -> {} drawH -> {}".format(w, maxOffset, self.sceneH, drawH))

        for i in range(0, self.count):
            h = (self.numbers[i] - self.minValue) / maxOffset * drawH + const.PADDING
            if isReset:
                LogUtil.e("i -> {} number -> {} h -> {}".format(i, self.numbers[i], h))
                rectItem = GraphicsUtil.createGraphicsRectItem(QRectF(i * w, self.sceneH - h, w / 2, h),
                                                               brush=QBrush(ColorConst.Grey))
                self.scene.addItem(rectItem)
                self.graphicsItems.append(rectItem)
            else:
                brush = ColorConst.Grey
                if i < self.orderedIndex:
                    brush = ColorConst.Red
                if i == self.currentCompareIndex:
                    brush = ColorConst.LightBlue
                if i == self.currentMinIndex:
                    brush = ColorConst.Indigo
                GraphicsUtil.updateGraphicsRectItem(self.graphicsItems[i], QRectF(i * w, self.sceneH - h, w / 2, h),
                                                    brush=QBrush(brush))
        # 触发实时显示数据
        QApplication.instance().processEvents()

    def swap(self, i: int, j: int):
        if i < 0 or i >= len(self.numbers) or j < 0 or j >= len(self.numbers):
            LogUtil.e("Invalid index to access Sort Data.")
            return
        t = self.numbers[i]
        self.numbers[i] = self.numbers[j]
        self.numbers[j] = t
        pass

    def pause(self, delay=0.1):
        time.sleep(delay)

    def jumpAlgoDesc(self):
        LogUtil.i("jumpAlgoDesc")
        from widget.algorithm.AlgorithmDescDialog import AlgorithmDescDialog
        basePath = FileUtil.getAlgorithmFp("SelectionSort/")
        LogUtil.e("basePath:", basePath)
        AlgorithmDescDialog("选择排序算法描述", FileUtil.readFile(basePath + "SelectionSort.html"),
                            FileUtil.readFile(basePath + "SelectionSort.java"),
                            FileUtil.readFile(basePath + "SelectionSort.js"),
                            FileUtil.readFile(basePath + "SelectionSort.py"),
                            FileUtil.readFile(basePath + "SelectionSort.c"),
                            FileUtil.readFile(basePath + "SelectionSort.cpp"),
                            FileUtil.readFile(basePath + "SelectionSort.swift"))
        pass
