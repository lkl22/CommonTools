# -*- coding: utf-8 -*-
# python 3.x
# Filename: JsonDialog.py
# 定义一个JsonDialog类实现Json树形结构展示的功能
from constant.WidgetConst import *
from util.JsonUtil import *
from util.DialogUtil import *
from util.LogUtil import *


class JsonDialog(QtWidgets.QDialog):
    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Json Format Dialog")
        self.setObjectName("JsonDialog")
        self.resize(1280, 720)
        self.setFixedSize(1280, 720)
        # self.setWindowFlags(QtCore.Qt.WindowMinimizeButtonHint)
        # self.setWindowFlags(QtCore.Qt.WindowMaximizeButtonHint)
        self.setWindowTitle(WidgetUtil.translate(text="JsonDialog"))

        self.jsonObj = None
        self.curOperateItem: QTreeWidgetItem = None

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
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, isVertical=True, geometry=QRect(const.PADDING, yPos, 450, 660))
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
        yPos = const.GROUP_BOX_MARGIN_TOP
        splitter = WidgetUtil.createSplitter(box, isVertical=True, geometry=QRect(const.PADDING, yPos, 685, 660))
        self.jsonTreeWidget = WidgetUtil.createTreeWidget(splitter)
        self.jsonTreeWidget.customContextMenuRequested.connect(self.customRightMenu)
        return box

    def customRightMenu(self, pos):
        print("customRightMenu")
        # 获取当前被点击的节点
        self.curOperateItem: QTreeWidgetItem = self.jsonTreeWidget.itemAt(pos)
        if self.curOperateItem:
            print(self.curOperateItem.text(0))
            isLeafNode = self.curOperateItem.data(0, Qt.UserRole)
            menu = None
            if isLeafNode:
                menu = WidgetUtil.createMenu("修改", func1=self.modifyItem, action2="删除", func2=self.delItem)
            else:
                if self.curOperateItem.text(0) == "[]":
                    menu = WidgetUtil.createMenu(func1=self.addItem, action2="删除", func2=self.delItem)
                else:
                    menu = WidgetUtil.createMenu(func1=self.addItem, action2="修改", func2=self.modifyItem, action3="删除", func3=self.delItem)
            menu.exec_(self.jsonTreeWidget.mapToGlobal(pos))
        else:
            print("这种情况是右键的位置不在treeItem的范围内，即在空白位置右击")
        pass

    def addItem(self):
        print("addItem")
        WidgetUtil.getTreeWidgetJsonData(self.jsonTreeWidget)

    def delItem(self):
        print("delItem")
        WidgetUtil.showQuestionDialog(message="你确定需要删除吗？", acceptFunc=self.delTreeWidgetItem)

    def modifyItem(self):
        print("modifyItem")
        DialogUtil.showLineEditDialog()
        pass

    def delTreeWidgetItem(self):
        print("delTreeWidgetItem")
        parent = self.curOperateItem.parent()
        # 循环删除没有子节点的item
        while parent:
            parent.removeChild(self.curOperateItem)
            childCount = parent.childCount()
            print("childCount %d" % childCount)
            if childCount > 0:
                break
            else:
                self.curOperateItem = parent
                parent = parent.parent()
        if not parent:
            if self.curOperateItem.childCount() == 0:
                # 清空整个树形控件数据
                self.jsonTreeWidget.clear()
        pass

    def decodeJsonFunc(self):
        self.getJsonData()
        if self.jsonObj is not None:
            WidgetUtil.setTreeWidgetJsonData(self.jsonTreeWidget, self.jsonObj)
        pass

    def encodeJsonFunc(self):
        self.getJsonData()
        if self.jsonObj:
            jsonData = JsonUtil.encode(self.jsonObj)
            self.jsonDataTextEdit.clear()
            self.jsonDataTextEdit.setText(jsonData)
        pass

    def getJsonData(self):
        jsonData = self.jsonDataTextEdit.toPlainText().strip()
        try:
            self.jsonObj = JsonUtil.decode(jsonData)
            print(self.jsonObj)
        except json.decoder.JSONDecodeError as err:
            WidgetUtil.showErrorDialog(message="%s" % err)
            self.jsonObj = None
