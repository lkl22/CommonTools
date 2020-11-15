# -*- coding: utf-8 -*-
# python 3.x
# Filename: PicturePreviewDialog.py
# 定义一个PicturePreviewDialog类实现图片预览功能
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QFrame
import sys

from constant.WidgetConst import *
from util.DialogUtil import *
from util.FileUtil import *


class PicturePreviewDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 600

    def __init__(self, filePath=None):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init picture preview Dialog")
        self.setObjectName("PicturePreviewDialog")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="图片预览"))

        self.filePath = filePath

        w = QWidget(self)
        layout = WidgetUtil.createHBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        w.setLayout(layout)
        w.setFixedSize(550, 50)

        if not filePath:
            self.openFile = WidgetUtil.createPushButton(self, text="Open Image", toolTip="Open the image to view.", onClicked=self.openImage)
            self.openFile.setFixedSize(150, 30)
            layout.addWidget(self.openFile)

        self.zoomIn = self.createPushBtn(FileUtil.getIconFp('zoom_in.png'), self.largeClick)
        # self.zoomIn = self.createPushBtn('../../icons/zoom_in.png', self.largeClick)
        layout.addWidget(self.zoomIn)

        self.zoomOut = self.createPushBtn(FileUtil.getIconFp('zoom_out.png'), self.smallClick)
        # self.zoomOut = self.createPushBtn('../../icons/zoom_out.png', self.smallClick)
        layout.addWidget(self.zoomOut)

        self.rotateLeft = self.createPushBtn(FileUtil.getIconFp('rotateLeft.png'), self.rotateLeftClick)
        # self.rotateLeft = self.createPushBtn('../../icons/rotateLeft.png', self.rotateLeftClick)
        layout.addWidget(self.rotateLeft)

        self.rotateRight = self.createPushBtn(FileUtil.getIconFp('rotateRight.png'), self.rotateRightClick)
        # self.rotateRight = self.createPushBtn('../../icons/rotateRight.png', self.rotateRightClick)
        layout.addWidget(self.rotateRight)

        self.box = ImageBox()
        self.box.resize(960, 480)

        vbox = WidgetUtil.createVBoxLayout()
        vbox.addWidget(w)
        vbox.addWidget(self.box)
        self.setLayout(vbox)
        if filePath:
            self.box.setImage(filePath)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createPushBtn(self, icon, onClicked):
        btn = WidgetUtil.createPushButton(self, text="", onClicked=onClicked)
        btn.setFixedSize(30, 30)
        btn.setStyleSheet("background-color: white")
        btn.setIconSize(QSize(20, 20))
        btn.setIcon(QIcon(icon))
        return btn

    def openImage(self):
        """
        select image file and open it
        :return:
        """
        imgName = WidgetUtil.getOpenFileName(caption="Open Image File", filter="*.jpg;;*.png;;*.jpeg")
        self.box.setImage(imgName)

    def largeClick(self):
        """
        used to enlarge image
        :return:
        """
        self.box.zoomIn()

    def smallClick(self):
        """
        used to reduce image
        :return:
        """
        self.box.zoomOut()

    def rotateLeftClick(self):
        LogUtil.d('rotateLeftClick')
        self.box.rotateLeft()
        pass

    def rotateRightClick(self):
        LogUtil.d('rotateRightClick')
        self.box.rotateRight()
        pass


class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()
        self.img = None
        self.scaledImg = None
        self.point = QPoint(0, 0)
        self.startPos = None
        self.endPos = None
        self.leftClick = False
        self.scale = 0.5
        self.rotateAngle = 0
        self.setWindowTitle("ImageBox")
        LogUtil.d('ImageBox size {}'.format(self.size()))
        # self.setContentsMargins(2, 2, 2, 2)
        # self.setStyleSheet("border:2px solid #f00")

    def setImage(self, imgPath):
        """
        open image file
        :param imgPath: image file path
        :return:
        """
        self.scale = 0.5
        self.rotateAngle = 0
        self.img = QPixmap(imgPath)
        ow = self.img.width()
        oh = self.img.height()
        boxWidth = self.size().width()
        boxHeight = self.size().height()
        self.scaledImg = self.img.scaled(boxWidth * 2, boxHeight * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        scaledWidth = self.scaledImg.width()
        scaledHeight = self.scaledImg.height()
        self.point = QPoint(boxWidth - scaledWidth // 2, boxHeight - scaledHeight // 2)
        LogUtil.d('setImage image size ({}, {}) box size {} scaledImg size ({}, {})'
                  .format(ow, oh, self.size(), scaledWidth, scaledHeight))
        self.update()

    def zoomIn(self):
        if self.scale < 2:
            self.scale += 0.2
            self.adjustSize()
            self.update()
            LogUtil.d('zoomIn box size {}', self.size())

    def zoomOut(self):
        if self.scale > 0.1:
            self.scale -= 0.1
            self.adjustSize()
            self.update()
            LogUtil.d('zoomOut box size {}', self.size())

    def rotateLeft(self):
        self.rotateAngle -= 90
        self.update()

    def rotateRight(self):
        self.rotateAngle += 90
        self.update()

    def paintEvent(self, e):
        """
        receive paint events
        :param e: QPaintEvent
        :return:
        """
        if self.scaledImg:
            painter = QPainter()
            painter.begin(self)
            painter.translate(self.size().width() / 2, self.size().height() / 2)
            painter.rotate(self.rotateAngle)
            painter.translate(- self.size().width() / 2, - self.size().height() / 2)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(self.point, self.scaledImg)
            painter.end()

    def mouseMoveEvent(self, e):
        """
        mouse move events for the widget
        :param e: QMouseEvent
        :return:
        """
        if self.leftClick:
            self.endPos = e.pos() - self.startPos
            self.point = self.point + self.endPos
            self.startPos = e.pos()
            self.repaint()

    def mousePressEvent(self, e):
        """
        mouse press events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.leftClick = True
            self.startPos = e.pos()

    def mouseReleaseEvent(self, e):
        """
        mouse release events for the widget
        :param e: QMouseEvent
        :return:
        """
        if e.button() == Qt.LeftButton:
            self.leftClick = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PicturePreviewDialog()
    window.show()
    sys.exit(app.exec_())
