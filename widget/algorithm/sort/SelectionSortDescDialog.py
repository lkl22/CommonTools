# -*- coding: utf-8 -*-
# python 3.x
# Filename: SelectionSortDescDialog.py
# 定义一个SelectionSortDescDialog类实现选择排序算法描述
from PyQt5.QtCore import QRectF, QPointF

from constant.ColorConst import ColorConst
from util.AutoTestUtil import *
from util.GraphicsUtil import GraphicsUtil
from constant.WidgetConst import *
from util.Uiautomator import *


class SelectionSortDescDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    GROUP_BOX_HEIGHT = 560

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Algorithm Visualizer Dialog")
        self.setObjectName("AlgorithmVisualizerDialog")
        self.resize(SelectionSortDescDialog.WINDOW_WIDTH, SelectionSortDescDialog.WINDOW_HEIGHT)
        self.setFixedSize(SelectionSortDescDialog.WINDOW_WIDTH, SelectionSortDescDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="选择排序算法描述"))

        width = SelectionSortDescDialog.WINDOW_WIDTH - const.PADDING * 2

        vbox = WidgetUtil.createVBoxLayout()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       SelectionSortDescDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)


        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        vbox.addWidget(splitter)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionSortDescDialog()
    window.show()
    sys.exit(app.exec_())
