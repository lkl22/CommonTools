# -*- coding: utf-8 -*-
# python 3.x
# Filename: ModuleDependencyDialog.py
# 定义一个ModuleDependencyDialog类实现模块间依赖关系显示功能

from __future__ import unicode_literals
import sys
import matplotlib
# Make sure that we are using QT5
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QDialogButtonBox
from util.LogUtil import LogUtil
from util.PlatformUtil import PlatformUtil
from util.WidgetUtil import WidgetUtil

matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, G=None, width=5, height=4, dpi=100):
        fig = plt.figure(1, facecolor='white')
        fig.clf()
        self.axes = fig.add_subplot(111)

        nx.draw_networkx(G, pos=nx.planar_layout(G), ax=self.axes, node_color='w', edge_color='b')

        ax = plt.gca()
        ax.margins(0.20)
        plt.axis("off")
        # plt.show()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class ModuleDependencyDialog(QtWidgets.QDialog):
    def __init__(self, G, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.G = G
        self.isDebug = isDebug

        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        ModuleDependencyDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        ModuleDependencyDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d("Add Or Edit Module Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/修改模块配置"))
        self.setObjectName("AddOrEditModuleDialog")
        self.resize(ModuleDependencyDialog.WINDOW_WIDTH, ModuleDependencyDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        sc = MyMplCanvas(self, self.G, width=5, height=4, dpi=100)
        vLayout.addWidget(sc)

        btnBox = WidgetUtil.createDialogButtonBox(standardButton=QDialogButtonBox.Ok, parent=self,
                                                  acceptedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()


if __name__ == '__main__':
    qApp = QtWidgets.QApplication(sys.argv)
    aw = ModuleDependencyDialog(isDebug=True)
    aw.show()
    sys.exit(qApp.exec_())
