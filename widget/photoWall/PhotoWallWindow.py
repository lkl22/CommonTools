# -*- coding: utf-8 -*-
# python 3.x
# Filename: PhotoWallWindow.py
# 定义一个PhotoWallWindow类实现照片墙功能

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
from util.FileUtil import *
from util.WidgetUtil import *
from constant.WidgetConst import *

TAG = "PhotoWallWindow"


class PhotoWallWindow(QMainWindow):
    DISPLAYED_PHOTO_SIZES = [100, 150, 200]
    PHOTO_TYPE = '.*.((jpg)|(JPG)|(png)|(PNG)|(JPEG)|(jpeg))'

    windowList = []

    def __init__(self, filePath=None, photoType=None, previewFinishedFunc=None):
        QMainWindow.__init__(self)
        PhotoWallWindow.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        PhotoWallWindow.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.6)
        self.setObjectName("PhotoWallWindow")
        self.setWindowTitle(WidgetUtil.translate("PhotoWall", "照片墙"))
        self.resize(PhotoWallWindow.WINDOW_WIDTH, PhotoWallWindow.WINDOW_HEIGHT)

        self.filePath = filePath
        self.photoType = photoType if photoType else self.PHOTO_TYPE
        self.previewFinishedFunc = previewFinishedFunc
        self.isClosed = False
        self.photoFps = None

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setObjectName("layoutWidget")
        self.setCentralWidget(layoutWidget)

        self.scrollAres = QScrollArea(self)
        self.scrollAres.setWidgetResizable(True)

        self.scrollAreaWidget = WidgetUtil.createWidget(self, 'scrollAreaWidget')

        # 进行网络布局
        self.gridLayout = QGridLayout(self.scrollAreaWidget)
        # 设置间距
        self.gridLayout.setSpacing(const.PADDING)
        self.gridLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scrollAres.setWidget(self.scrollAreaWidget)

        self.vBox = WidgetUtil.createVBoxLayout()
        self.vBox.addWidget(self.scrollAres)
        layoutWidget.setLayout(self.vBox)
        self.createMenuBar()

        # 设置图片的预览尺寸；
        self.displayedPhotoSize = self.DISPLAYED_PHOTO_SIZES[0]
        self.showCount = -1

        # 图像列数
        self.maxColumns = 1

        QtCore.QMetaObject.connectSlotsByName(self)
        self.show()
        if filePath:
            self.startPhotoViewer()
        pass

    def changeEvent(self, event):
        LogUtil.d(TAG, "changeEvent", event)
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.isMinimized():
                LogUtil.d(TAG, "窗口最小化")
            elif self.isActiveWindow() or self.isFullScreen() or self.isMaximized():
                LogUtil.d(TAG, "活动窗口 or 全屏显示 or 窗口最大化")
                if self.filePath:
                    self.startPhotoViewer()
        pass

    def createMenuBar(self):
        # 底部状态栏
        self.statusBar().showMessage('状态栏')

        # 顶部菜单栏
        menuBar: QMenuBar = self.menuBar()
        menuBar.setNativeMenuBar(False)
        openAct = WidgetUtil.createAction(parent=menuBar, text='&Open', func=self.openDir, shortcut='Ctrl+O', statusTip='打开文件夹')
        menuBar.addAction(openAct)
        sizeMenu = menuBar.addMenu('&Size')
        sizeMenu.setStatusTip('设置预览图片尺寸大小')
        smallAct = WidgetUtil.createAction(parent=menuBar, text='&small', func=self.setSmallSize, statusTip='显示小图标')
        mediumAct = WidgetUtil.createAction(parent=menuBar, text='&medium', func=self.setMediumSize, statusTip='显示中图标')
        largeAct = WidgetUtil.createAction(parent=menuBar, text='&large', func=self.setLargeSize, statusTip='显示大图标')
        sizeMenu.addAction(smallAct)
        sizeMenu.addAction(mediumAct)
        sizeMenu.addAction(largeAct)

    # 重写关闭事件，回到第一界面
    def closeEvent(self, event):
        self.isClosed = True
        from widget.MainWidget import MainWidget
        window = MainWidget()
        # 注：没有这句，是不打开另一个主界面的
        self.windowList.append(window)
        window.show()
        if self.previewFinishedFunc:
            self.previewFinishedFunc()
        event.accept()

    def setSmallSize(self):
        if self.displayedPhotoSize != self.DISPLAYED_PHOTO_SIZES[0]:
            self.displayedPhotoSize = self.DISPLAYED_PHOTO_SIZES[0]
            self.startPhotoViewer()
        pass

    def setMediumSize(self):
        if self.displayedPhotoSize != self.DISPLAYED_PHOTO_SIZES[1]:
            self.displayedPhotoSize = self.DISPLAYED_PHOTO_SIZES[1]
            self.startPhotoViewer()
        pass

    def setLargeSize(self):
        if self.displayedPhotoSize != self.DISPLAYED_PHOTO_SIZES[2]:
            self.displayedPhotoSize = self.DISPLAYED_PHOTO_SIZES[2]
            self.startPhotoViewer()
        pass

    def openDir(self):
        filePath = WidgetUtil.getExistingDirectory(caption='选择文件夹', directory='./')
        if not filePath:
            QMessageBox.information(self, '提示', '文件夹为空，请重新操作')
            return
        self.filePath = filePath
        self.startPhotoViewer()

    def clearGridLayout(self):
        self.showCount = -1
        self.maxColumns = self.getMaxColumns()
        while self.gridLayout.count() > 0:
            layoutItem = self.gridLayout.itemAt(0)
            widget = layoutItem.widget()
            self.gridLayout.removeWidget(widget)
            widget.setParent(None)
            widget.deleteLater()

    def startPhotoViewer(self):
        self.clearGridLayout()
        if self.filePath:
            filePath = self.filePath
            LogUtil.d(TAG, 'file path为{}'.format(filePath))

            self.photoFps = FileUtil.findFilePathList(filePath, [self.photoType])
            LogUtil.d(TAG, '预览图片path', self.photoFps)

            if len(self.photoFps) > 0:
                for fp in self.photoFps:
                    if self.isClosed:
                        # 窗口关掉了需要结束循环
                        break
                    LogUtil.d(TAG, 'photo file path: ', fp)
                    pixmap = QPixmap(fp)
                    self.addImage(pixmap, fp.replace(os.path.join(filePath, ''), ''))
                    # 触发实时显示数据
                    QApplication.instance().processEvents()
            else:
                WidgetUtil.showErrorDialog(self, '错误', '生成图片文件为空')
        else:
            WidgetUtil.showErrorDialog(self, '错误', '文件路径为空，请稍后')

    def addImage(self, pixmap, fp):
        self.showCount += 1
        row = self.showCount // self.maxColumns
        col = self.showCount % self.maxColumns

        LogUtil.d(TAG, '行数: {} 列数: {} displayedPhotoSize: {}'.format(row, col, self.displayedPhotoSize))

        clickablePhoto = QClickableImage(self.showCount, self.displayedPhotoSize, self.displayedPhotoSize, pixmap, fp)
        clickablePhoto.clicked.connect(self.onLeftClicked)
        clickablePhoto.leftDoubleClicked.connect(self.onLeftDoubleClicked)
        clickablePhoto.rightClicked.connect(self.onRightClicked)
        self.gridLayout.addWidget(clickablePhoto, row, col)

    def onLeftClicked(self, index, photoFp):
        LogUtil.d(TAG, 'left clicked - index {} photoFp {}'.format(index, photoFp))
        self.statusBar().showMessage(photoFp)

    def onLeftDoubleClicked(self, index, photoFp):
        LogUtil.d(TAG, 'left double clicked - index {} photoFp {}'.format(index, photoFp))
        from widget.photoWall.PicturePreviewDialog import PicturePreviewDialog
        PicturePreviewDialog(self.photoFps, index)

    def onRightClicked(self, index, photoFp):
        LogUtil.d(TAG, 'right clicked - index {} photoFp {}'.format(index, photoFp))

    def getMaxColumns(self):
        # 展示图片的区域
        scrollAreaPhotoWidth = self.width() - const.PADDING * 2
        itemWidth = self.displayedPhotoSize + const.PADDING
        if scrollAreaPhotoWidth > itemWidth:
            # 计算出一行几列；
            picOfColumns = scrollAreaPhotoWidth // itemWidth
        else:
            picOfColumns = 1
        LogUtil.e(TAG, 'scrollAreaPhotoWidth: {} itemWidth: {} max col: {}'
                  .format(scrollAreaPhotoWidth, itemWidth, picOfColumns))
        return picOfColumns


class QClickableImage(QFrame):
    photoFp = ''

    def __init__(self, index, width=0, height=0, pixmap=None, photoFp=''):
        QWidget.__init__(self)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.index = index
        self.width = width
        self.height = height
        self.pixmap = pixmap

        self.setStyleSheet("QWidget{background:#00000000;} QWidget:hover{background:#00ff00;}")

        if self.width and self.height:
            self.setFixedWidth(self.width)
            self.setMinimumHeight(self.height)
        if self.pixmap:
            pixmap = self.pixmap.scaled(QSize(self.width, self.height), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmapLabel = WidgetUtil.createLabel(self, objectName='pixmapLabel', alignment=Qt.AlignCenter)
            self.pixmapLabel.setPixmap(pixmap)
            self.layout.addWidget(self.pixmapLabel)
        if photoFp:
            self.photoFp = photoFp
            self.descLabel = WidgetUtil.createLabel(self, objectName='descLabel', text=photoFp,
                                                    alignment=Qt.AlignHCenter | Qt.AlignBottom)
            self.descLabel.setMaximumWidth(self.width)
            # 让文字自适应大小
            self.descLabel.adjustSize()
            self.descLabel.setWordWrap(True)
            # 设置透明背景
            self.descLabel.setStyleSheet("QWidget{background:#00000000;}")
            self.layout.addWidget(self.descLabel)
        self.setLayout(self.layout)
        # self.adjustSize()
        # self.setContentsMargins(1, 1, 1, 1)
        # self.setStyleSheet("border:1px solid #f00")
        LogUtil.d(TAG, 'size: {}'.format(self.size()))

    clicked = pyqtSignal(int, str)
    leftDoubleClicked = pyqtSignal(int, str)
    rightClicked = pyqtSignal(int, str)

    def mousePressEvent(self, ev: QMouseEvent):
        LogUtil.d(TAG, 'mousePressEvent')
        if ev.button() == Qt.RightButton:
            # 鼠标右击
            self.rightClicked.emit(self.index, self.photoFp)
        else:
            self.clicked.emit(self.index, self.photoFp)
        # super().mousePressEvent(ev)

    def mouseDoubleClickEvent(self, ev: QMouseEvent):
        LogUtil.d(TAG, 'mouseDoubleClickEvent')
        if ev.button() == Qt.LeftButton:
            self.leftDoubleClicked.emit(self.index, self.photoFp)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = PhotoWallWindow()
    window = PhotoWallWindow('/Users/likunlun/Pictures/生活照/Macao', None, lambda: {
        LogUtil.d(TAG, 'preview finished')
    })
    window.show()
    sys.exit(app.exec_())
