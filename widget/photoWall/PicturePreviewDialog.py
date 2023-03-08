# -*- coding: utf-8 -*-
# python 3.x
# Filename: PicturePreviewDialog.py
# 定义一个PicturePreviewDialog类实现图片预览功能
from PyQt5.QtCore import QPoint, QEvent
from PyQt5.QtGui import QPixmap, QPainter, QKeyEvent
import sys
from util.DialogUtil import *
from util.FileUtil import *

TAG = "PicturePreviewDialog"


def getIconFp(iconName, isDebug=False):
    if isDebug:
        return f'../../resources/icons/previewImage/{iconName}'
    else:
        return FileUtil.getIconFp(f'previewImage/{iconName}')
    pass


class PicturePreviewDialog(QtWidgets.QDialog):
    MAX_SCALE = 2
    MIN_SCALE = 0.1

    def __init__(self, filePathList=None, index=0, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        PicturePreviewDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        PicturePreviewDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.8)
        LogUtil.d(TAG, "Init picture preview Dialog")
        self.setObjectName("PicturePreviewDialog")
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="图片预览"))

        self.filePathList = filePathList
        self.index = index

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(5, 10, 5, 10), spacing=5)
        layout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 0, 0, 0), spacing=30, alignment=Qt.AlignCenter)
        if not filePathList:
            self.openFile = WidgetUtil.createPushButton(self, text="Open Image", toolTip="Open the image to view.",
                                                        onClicked=self.openImage)
            self.openFile.setFixedSize(100, 30)
            layout.addWidget(self.openFile)
        self.zoomIn = self.createPushBtn(getIconFp('zoom_in.png', isDebug), self.largeClick)
        layout.addWidget(self.zoomIn)
        self.zoomOut = self.createPushBtn(getIconFp('zoom_out.png', isDebug), self.smallClick)
        layout.addWidget(self.zoomOut)
        self.rotateLeft = self.createPushBtn(getIconFp('rotateLeft.png', isDebug), self.rotateLeftClick)
        layout.addWidget(self.rotateLeft)
        self.rotateRight = self.createPushBtn(getIconFp('rotateRight.png', isDebug), self.rotateRightClick)
        layout.addWidget(self.rotateRight)
        vbox.addLayout(layout)

        layout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=20, alignment=Qt.AlignCenter)
        self.box = ImageBox()
        self.box.setFixedSize(int(PicturePreviewDialog.WINDOW_WIDTH * 0.9),
                              int(PicturePreviewDialog.WINDOW_HEIGHT * 0.88))
        self.backBtn = self.createPushBtn(getIconFp('back.png', isDebug), self.backClick)
        layout.addWidget(self.backBtn)
        layout.addWidget(self.box)
        self.nextBtn = self.createPushBtn(getIconFp('next.png', isDebug), self.nextClick)
        layout.addWidget(self.nextBtn)
        vbox.addLayout(layout)

        layout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 15, 10, 5), alignment=Qt.AlignCenter)
        self.titleLabel = WidgetUtil.createLabel(self, alignment=Qt.AlignCenter,
                                                 sizePolicy=WidgetUtil.createSizePolicy())
        layout.addWidget(self.titleLabel)
        vbox.addLayout(layout)

        self.setLayout(vbox)

        if filePathList:
            if len(filePathList) <= index or index < 0:
                self.index = 0
            self.filePath = filePathList[index]
            self.openNextImage()
        else:
            self.backBtn.setEnabled(False)
            self.nextBtn.setEnabled(False)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec()

    def createPushBtn(self, icon, onClicked):
        return WidgetUtil.createPushButton(self, text="", fixedSize=QSize(30, 30), styleSheet="background-color: white",
                                           iconSize=QSize(20, 20), icon=QIcon(icon), onClicked=onClicked)

    def openImage(self):
        """
        select image file and open it
        :return:
        """
        imgName = WidgetUtil.getOpenFileName(caption="Open Image File", filter="*.jpg;;*.png;;*.jpeg")
        self.titleLabel.setText(imgName)
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
        LogUtil.d(TAG, 'rotateLeftClick')
        self.box.rotateLeft()
        pass

    def rotateRightClick(self):
        LogUtil.d(TAG, 'rotateRightClick')
        self.box.rotateRight()
        pass

    def backClick(self):
        LogUtil.d(TAG, 'backClick')
        self.index -= 1 + len(self.filePathList)
        self.index %= len(self.filePathList)
        self.openNextImage()
        pass

    def nextClick(self):
        LogUtil.d(TAG, 'nextClick')
        self.index += 1
        self.index %= len(self.filePathList)
        self.openNextImage()
        pass

    def openNextImage(self):
        self.filePath = self.filePathList[self.index]
        self.titleLabel.setText("[{}/{}]  {}".format(self.index + 1, len(self.filePathList), self.filePath))
        self.box.setImage(self.filePath)


class ImageBox(QWidget):
    def __init__(self):
        super(ImageBox, self).__init__()
        self.controlPress = False
        self.img = None
        self.scaledImg = None
        self.point = QPoint(0, 0)
        self.startPos = None
        self.endPos = None
        self.leftClick = False
        self.scale = 0.5
        self.rotateAngle = 0
        self.setWindowTitle("ImageBox")
        # 控件开始捕获键盘，只有控件开始捕获键盘，控件的键盘事件才能收到消息
        self.grabKeyboard()
        LogUtil.d(TAG, 'ImageBox size {}'.format(self.size()))
        # self.setContentsMargins(2, 2, 2, 2)
        # self.setStyleSheet("border:2px solid #f00")

    def setImage(self, imgPath):
        """
        open image file
        :param imgPath: image file path
        :return:
        """
        self.controlPress = False
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
        self.point = QPoint(boxWidth, boxHeight)
        LogUtil.d(TAG, 'setImage image size ({}, {}) box size {} scaledImg size ({}, {})'
                  .format(ow, oh, self.size(), scaledWidth, scaledHeight))
        self.update()

    def zoomIn(self):
        if self.scale < PicturePreviewDialog.MAX_SCALE:
            self.scale += 0.2
            self.point = self.point * (self.scale - 0.2) / self.scale
            self.adjustSize()
            self.update()
            LogUtil.d(TAG, 'zoomIn box size {}', self.size())

    def zoomOut(self):
        if self.scale > PicturePreviewDialog.MIN_SCALE:
            self.scale -= 0.1
            self.point = self.point * (self.scale + 0.1) / self.scale
            self.adjustSize()
            self.update()
            LogUtil.d(TAG, 'zoomOut box size {}', self.size())

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
            painter.translate(-self.size().width() / 2, -self.size().height() / 2)
            painter.scale(self.scale, self.scale)
            painter.translate(-self.scaledImg.width() / 2, -self.scaledImg.height() / 2)
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

    def keyPressEvent(self, e: QKeyEvent):
        LogUtil.d(TAG, 'keyPressEvent', e.key())
        if e.key() == Qt.Key_Control:
            LogUtil.d(TAG, 'Control press')
            self.controlPress = True

    def keyReleaseEvent(self, e: QKeyEvent):
        LogUtil.d(TAG, 'keyReleaseEvent', e.key())
        if e.key() == Qt.Key_Control:
            LogUtil.d(TAG, 'Control release')
            self.controlPress = False

    def wheelEvent(self, e: QtGui.QWheelEvent):
        if self.controlPress:
            # if event.delta() > 0:  # 滚轮上滚,PyQt4
            # This function has been deprecated, use pixelDelta() or angleDelta() instead.
            angle = e.angleDelta() / 8  # 返回QPoint对象，为滚轮转过的数值，单位为1/8度
            LogUtil.d(TAG, 'wheelEvent', e.pos(), e.x(), e.y())
            angleX = angle.x()  # 水平滚过的距离(此处用不上)
            angleY = angle.y()  # 竖直滚过的距离
            step = 0.005
            if self.scale > 1.5:
                step = 0.01
            if angleY > 0:  # 滚轮上滚
                if self.scale < PicturePreviewDialog.MAX_SCALE:
                    self.scale += step
                    self.point = self.point * (self.scale - step) / self.scale
                    self.update()  # 重绘
            elif angleY < 0:  # 滚轮下滚
                if self.scale > PicturePreviewDialog.MIN_SCALE:
                    self.scale -= step
                    self.point = self.point * (self.scale + step) / self.scale
                    self.update()
        LogUtil.d(TAG, 'wheelEvent', e.pos(), e.x(), e.y())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = PicturePreviewDialog(isDebug=True)
    window = PicturePreviewDialog(['/Users/likunlun/Pictures/生活照/Macao/IMG_20170403_175221.jpg'], isDebug=True)
    window.show()
    sys.exit(app.exec_())
