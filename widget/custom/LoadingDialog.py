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
    WINDOW_WIDTH = 300
    WINDOW_HEIGHT = 150

    def __init__(self, showText: str = '正在加载中。。。', btnText="Cancel", rejectedFunc=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Loading Dialog")

        self.setFixedSize(LoadingDialog.WINDOW_WIDTH, LoadingDialog.WINDOW_HEIGHT)
        self.setObjectName("LoadingDialog")
        self.setStyleSheet("LoadingDialog{background-color:rgb(0,255,255)}")
        # 设置透明度
        # self.setWindowOpacity(0.8)

        # 取消对话框标题
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setAutoFillBackground(True)

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, LoadingDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       LoadingDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0), spacing=10)
        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        vLayout.setAlignment(Qt.AlignCenter)
        layoutWidget.setLayout(vLayout)

        label = WidgetUtil.createLabel(self, alignment=Qt.AlignCenter)
        movie = QMovie("../../resources/icons/loading.gif" if isDebug else FileUtil.getIconFp("loading.gif"))
        label.setMovie(movie)
        movie.start()

        vLayout.addWidget(label)
        label = WidgetUtil.createLabel(self, text=showText, alignment=Qt.AlignCenter)
        label.setContentsMargins(0, 0, 0, 0)
        vLayout.addWidget(label)

        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(standardButton=QDialogButtonBox.Cancel, parent=self,
                                                  rejectedFunc=lambda: self.close())
        btnBox.button(QDialogButtonBox.Cancel).setText(btnText)
        vLayout.addWidget(btnBox)

        if rejectedFunc:
            self.rejected.connect(rejectedFunc)

        # 要使用非模态对话框
        self.setModal(False)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoadingDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
