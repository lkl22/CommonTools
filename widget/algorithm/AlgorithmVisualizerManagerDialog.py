# -*- coding: utf-8 -*-
# python 3.x
# Filename: AlgorithmVisualizerManagerDialog.py
# 定义一个AlgorithmVisualizerManagerDialog类实现算法可视化管理
import sys
from util.DialogUtil import *
from util.WeditorUtil import *


class AlgorithmVisualizerManagerDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AlgorithmVisualizerManagerDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.3)
        LogUtil.d("Init Algorithm Visualizer Manager Dialog")
        self.setObjectName("AlgorithmVisualizerManagerDialog")
        self.resize(AlgorithmVisualizerManagerDialog.WINDOW_WIDTH, AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AlgorithmVisualizerManagerDialog.WINDOW_WIDTH, AlgorithmVisualizerManagerDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="算法可视化管理"))

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        sortAlgorithmVisualizer = self.createSortAlgorithmVisualizer(self)
        vLayout.addWidget(sortAlgorithmVisualizer)

        self.setWindowModality(Qt.ApplicationModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createSortAlgorithmVisualizer(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="排序算法可视化管理")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        vbox.addWidget(WidgetUtil.createPushButton(box, text="选择排序", onClicked=self.selectionSortVisualizer))
        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def selectionSortVisualizer(self):
        LogUtil.i("selectionSortVisualizer")
        from widget.algorithm.sort.SelectionSortDialog import SelectionSortDialog
        SelectionSortDialog()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AlgorithmVisualizerManagerDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
