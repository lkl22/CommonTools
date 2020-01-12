# -*- coding: utf-8 -*-
# python 3.x
# Filename: JsonDialog.py
# 定义一个JsonDialog类实现Json树形结构展示的功能
from util.WidgetUtil import *
from constant.WidgetConst import *
from util.JsonUtil import *


class JsonDialog(QtWidgets.QDialog):
    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        print("init json dialog")
        self.setObjectName("JsonDialog")
        self.resize(1280, 720)
        self.setWindowTitle(WidgetUtil.translate(text="JsonDialog"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(10, 10, 1260, 700))
        layoutWidget.setObjectName("layoutWidget")

        hLayout = WidgetUtil.createHBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(hLayout)

        jsonStrGroupBox = self.createJsonStrGroupBox(layoutWidget)
        splitter = self.createChangeBtnSplitter(layoutWidget)
        treeGroupBox = self.createTreeGroupBox(layoutWidget)

        hLayout.addWidget(jsonStrGroupBox)
        hLayout.addWidget(splitter)
        hLayout.addWidget(treeGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createJsonStrGroupBox(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy(hStretch=2)
        box = WidgetUtil.createGroupBox(parent, title="请输入json数据", sizePolicy=sizePolicy)
        splitter = WidgetUtil.createSplitter(box, isVertical=True, geometry=QRect(const.PADDING, 30, 450, 660))
        self.jsonDataTextEdit = WidgetUtil.createTextEdit(splitter, text='{"a":false, "b":[["b"],["a"]]}')
        return box

    def createChangeBtnSplitter(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy(hPolicy=QSizePolicy.Fixed)
        splitter = WidgetUtil.createSplitter(parent, isVertical=True, geometry=QRect(0, 0, 100, 200), sizePolicy=sizePolicy)
        sizePolicy = WidgetUtil.createSizePolicy(vPolicy=QSizePolicy.Fixed)
        WidgetUtil.createLabel(splitter, sizePolicy=sizePolicy)
        WidgetUtil.createPushButton(splitter, text=" >> ", onClicked=self.decodeJsonFunc)
        WidgetUtil.createPushButton(splitter, text=" << ", onClicked=self.encodeJsonFunc)
        WidgetUtil.createLabel(splitter, sizePolicy=sizePolicy)
        return splitter

    def createTreeGroupBox(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy(hStretch=3)
        box = WidgetUtil.createGroupBox(parent, title="格式化后数据", sizePolicy=sizePolicy)
        splitter = WidgetUtil.createSplitter(box, isVertical=True, geometry=QRect(const.PADDING, 30, 685, 660))
        self.jsonTreeWidget = WidgetUtil.createTreeWidget(splitter)
        return box

    def decodeJsonFunc(self):
        jsonData = self.jsonDataTextEdit.toPlainText().strip()
        try:
            jsonObj = JsonUtil.decode(jsonData)
            print(jsonObj)
            WidgetUtil.setTreeWidgetData(self.jsonTreeWidget, jsonObj)
        except json.decoder.JSONDecodeError as err:
            WidgetUtil.showErrorDialog(message="%s" % err)
        pass

    def encodeJsonFunc(self):
        pass