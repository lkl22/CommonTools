# -*- coding: utf-8 -*-
# python 3.x
# Filename: JsonDialog.py
# 定义一个JsonDialog类实现Json树形结构展示的功能
import sys

from constant.WidgetConst import *
from util.JsonUtil import *
from util.DialogUtil import *
from util.LogUtil import *


class JsonDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        JsonDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        JsonDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.8)
        LogUtil.d("Init Json Format Dialog")
        self.setObjectName("JsonDialog")
        self.resize(JsonDialog.WINDOW_WIDTH, JsonDialog.WINDOW_HEIGHT)
        # self.setFixedSize(JsonDialog.WINDOW_WIDTH, JsonDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="JsonDialog"))

        self.jsonObj = None
        self.curOperateItem: QTreeWidgetItem = None

        hLayout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        jsonStrGroupBox = self.createJsonStrGroupBox(self)
        changeBtnBox = self.createChangeBtnBox(self)
        treeGroupBox = self.createTreeGroupBox(self)

        hLayout.addWidget(jsonStrGroupBox, 2)
        hLayout.addLayout(changeBtnBox)
        hLayout.addWidget(treeGroupBox, 3)

        self.setWindowModality(Qt.WindowModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createJsonStrGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="请输入json数据")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.jsonDataTextEdit = WidgetUtil.createTextEdit(box, text='{"a":false, "b":[["b"],["a"]]}')
        vbox.addWidget(self.jsonDataTextEdit)
        return box

    def createChangeBtnBox(self, parent):
        vbox = WidgetUtil.createVBoxLayout(parent, margins=QMargins(20, 10, 20, 10), spacing=10,
                                           alignment=Qt.AlignCenter)
        vbox.addWidget(WidgetUtil.createPushButton(parent, text=" >> ", onClicked=self.decodeJsonFunc))
        vbox.addWidget(WidgetUtil.createPushButton(parent, text=" << ", onClicked=self.encodeJsonFunc))
        return vbox

    def createTreeGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="格式化后数据")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.jsonTreeWidget = WidgetUtil.createTreeWidget(box)
        self.jsonTreeWidget.customContextMenuRequested.connect(self.customRightMenu)
        vbox.addWidget(self.jsonTreeWidget)
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
                    menu = WidgetUtil.createMenu(func1=self.addItem, action2="修改", func2=self.modifyItem, action3="删除",
                                                 func3=self.delItem)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JsonDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
