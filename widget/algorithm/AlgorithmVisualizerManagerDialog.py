# -*- coding: utf-8 -*-
# python 3.x
# Filename: AlgorithmVisualizerManagerDialog.py
# 定义一个AlgorithmVisualizerManagerDialog类实现算法可视化管理
import sys

from constant.WidgetConst import *
from util.DialogUtil import *
from util.WeditorUtil import *


class AlgorithmVisualizerManagerDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Algorithm Visualizer Manager Dialog")
        self.setObjectName("AlgorithmVisualizerManagerDialog")
        self.resize(AlgorithmVisualizerManagerDialog.WINDOW_WIDTH, AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT)
        self.setFixedSize(AlgorithmVisualizerManagerDialog.WINDOW_WIDTH, AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="算法可视化管理"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, AlgorithmVisualizerManagerDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        sortAlgorithmVisualizer = self.createSortAlgorithmVisualizer(layoutWidget)
        vLayout.addWidget(sortAlgorithmVisualizer)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createSortAlgorithmVisualizer(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AlgorithmVisualizerManagerDialog.WINDOW_WIDTH - const.PADDING * 4
        box = WidgetUtil.createGroupBox(parent, title="排序算法可视化管理", minSize=QSize(width, 300))
        sizePolicy = WidgetUtil.createSizePolicy()

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="选择排序", onClicked=self.selectionSortVisualizer)

        return box

    def selectionSortVisualizer(self):
        LogUtil.i("selectionSortVisualizer")
        from widget.algorithm.sort.SelectionSortDialog import SelectionSortDialog
        SelectionSortDialog()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AlgorithmVisualizerManagerDialog()
    window.show()
    sys.exit(app.exec_())
