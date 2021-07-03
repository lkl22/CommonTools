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
    DESC_GROUP_BOX_HEIGHT = 200

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

        descGroupBox = self.createDescGroupBox(layoutWidget)
        vbox.addWidget(descGroupBox)

        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        splitter.setSizePolicy(sizePolicy)
        vbox.addWidget(splitter)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createDescGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = SelectionSortDescDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="算法描述",
                                        minSize=QSize(width, SelectionSortDescDialog.DESC_GROUP_BOX_HEIGHT))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.PADDING * 2, SelectionSortDescDialog.DESC_GROUP_BOX_HEIGHT - const.PADDING * 4))

        desc = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        desc.insertHtml(r'''选择排序是一种简单直观的排序算法，无论什么数据进去都是 O(n²) 的时间复杂度。所以用到它的时候，数据规模越小越好。唯一的好处可能就是不占用额外的内存空间了吧。
<h3>算法步骤</h3>
首先在未排序序列中找到最小（大）元素，存放到排序序列的起始位置。<br>
再从剩余未排序元素中继续寻找最小（大）元素，然后放到已排序序列的末尾。<br>
重复第二步，直到所有元素均排序完毕。''')
        return box


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionSortDescDialog()
    window.show()
    sys.exit(app.exec_())
