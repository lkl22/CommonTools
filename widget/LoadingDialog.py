# -*- coding: utf-8 -*-
# python 3.x
# Filename: LoadingDialog.py
# 定义一个LoadingDialog类实现加载等待弹框
import sys

from PyQt5.QtGui import QMovie

from constant.WidgetConst import *
from util.DialogUtil import *
from util.FileUtil import FileUtil
from util.LogUtil import *


class LoadingDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 200
    WINDOW_HEIGHT = 120

    def __init__(self, showText: str = '正在加载中。。。'):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Loading Dialog")

        self.setFixedSize(LoadingDialog.WINDOW_WIDTH, LoadingDialog.WINDOW_HEIGHT)
        # 设置透明用
        self.setWindowOpacity(0.5)
        self.setWindowFlags(Qt.Dialog or Qt.CustomizeWindowHint)

        # 取消对话框标题
        self.setWindowFlags(Qt.Dialog or Qt.FramelessWindowHint)

        # 取消对话框标题和边框
        self.setAutoFillBackground(True)

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, LoadingDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       LoadingDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        vLayout.setAlignment(Qt.AlignCenter)
        layoutWidget.setLayout(vLayout)

        label = WidgetUtil.createLabel(self, alignment=Qt.AlignCenter)
        movie = QMovie(FileUtil.getIconFp("loading.gif"))
        label.setMovie(movie)
        movie.start()

        vLayout.addWidget(label)

        label = WidgetUtil.createLabel(self, text=showText, alignment=Qt.AlignCenter)
        label.setContentsMargins(0, 0, 0, 0)
        vLayout.addWidget(label)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoadingDialog()
    window.show()
    sys.exit(app.exec_())
