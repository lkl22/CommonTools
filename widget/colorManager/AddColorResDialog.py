# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddColorResDialog.py
# 定义一个AddColorResDialog类实现添加android color资源
from constant.WidgetConst import *
from util.DialogUtil import *
from util.OperaIni import *


class AddColorResDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 350
    WINDOW_HEIGHT = 180

    def __init__(self, callbackFunc, srcFindColorRes=[{}]):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Add color Res Dialog")
        self.setObjectName("AddColorResDialog")
        self.resize(AddColorResDialog.WINDOW_WIDTH, AddColorResDialog.WINDOW_HEIGHT)
        self.setFixedSize(AddColorResDialog.WINDOW_WIDTH, AddColorResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="添加color资源"))

        self.callbackFunc = callbackFunc
        self.srcFindColorRes = srcFindColorRes

        vbox = WidgetUtil.createVBoxLayout()
        width = AddColorResDialog.WINDOW_WIDTH - const.PADDING * 2
        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="资源名称：", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(100, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.colorNameLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="normal color：", minSize=QSize(100, const.HEIGHT), onClicked=self.normalColorSelected)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.normalColorLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="dark color：", minSize=QSize(100, const.HEIGHT), onClicked=self.darkColorSelected)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.darkColorLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy)
        vbox.addWidget(splitter)

        splitter, _, _, _ = DialogUtil.createBottomBtn(self, okCallback=self.acceptFunc, cancelBtnText="Cancel")
        vbox.addLayout(splitter)

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       AddColorResDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)
        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def normalColorSelected(self):
        color = WidgetUtil.getColor()
        if color:
            self.normalColorLineEdit.setText(color)

    def darkColorSelected(self):
        color = WidgetUtil.getColor()
        if color:
            self.darkColorLineEdit.setText(color)

    def acceptFunc(self):
        colorName = self.colorNameLineEdit.text().strip()
        if not colorName:
            WidgetUtil.showErrorDialog(message="请输入color资源名称")
            return False
        normalColor = self.normalColorLineEdit.text().strip().upper()
        if not normalColor:
            WidgetUtil.showErrorDialog(message="请输入normal color颜色值（#FFFFFFFF、#FFF、#FFFFFF）")
            return False
        if not ReUtil.matchColor(normalColor):
            WidgetUtil.showErrorDialog(message="normal color请输入正确的颜色值（#FFF、#FFFFFF、#FFFFFFFF、666、666666、66666666）")
            return False
        for colorRes in self.srcFindColorRes:
            if colorRes:
                if colorRes['colorName'] == colorName:
                    WidgetUtil.showErrorDialog(message=colorName + "已经存在了，请输入不一样的color name")
                    return False

        darkColor = self.darkColorLineEdit.text().strip().upper()
        if darkColor and not ReUtil.matchColor(darkColor):
            WidgetUtil.showErrorDialog(message="dark color请输入正确的颜色值（#FFF、#FFFFFF、#FFFFFFFF、666、666666、66666666）")
            return False
        if not normalColor.startswith('#'):
            normalColor = '#' + normalColor
        if not darkColor.startswith('#'):
            darkColor = '#' + darkColor
        if self.callbackFunc:
            self.callbackFunc(colorName, normalColor, darkColor)
        return True

