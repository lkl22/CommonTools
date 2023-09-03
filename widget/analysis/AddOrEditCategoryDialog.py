# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditCategoryDialog.py
# 定义一个AddOrEditCategoryDialog类实现添加、编辑分类配置功能
import copy
from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.MD5Util import MD5Util
from util.OperaIni import *
from widget.analysis.LogAnalysisManager import *

TAG = "AddOrEditCategoryDialog"


class AddOrEditCategoryDialog(QtWidgets.QDialog):
    def __init__(self, callback, categoryInfo=None, categoryList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.isDebug = isDebug
        self.callback = callback
        if categoryList is None:
            categoryList = []
        self.categoryList = categoryList
        self.isAdd = categoryInfo is None
        self.categoryInfo = categoryInfo

        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AddOrEditCategoryDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.3)
        AddOrEditCategoryDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.1)
        LogUtil.d(TAG, "Add Or Edit Category Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/修改分类配置"))
        self.setObjectName("AddOrEditCategoryDialog")
        self.resize(AddOrEditCategoryDialog.WINDOW_WIDTH, AddOrEditCategoryDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.categoryConfigGroupBox = self.createCategoryConfigGroupBox(self)
        vLayout.addWidget(self.categoryConfigGroupBox)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createCategoryConfigGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        labelWidth = 120
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="分类名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.categoryNameLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.categoryInfo, KEY_NAME))
        hbox.addWidget(self.categoryNameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="分类描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.categoryDescLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.categoryInfo, KEY_DESC))
        hbox.addWidget(self.categoryDescLineEdit)
        vbox.addLayout(hbox)

        vbox.addItem(WidgetUtil.createVSpacerItem(1, 1))
        return box

    def acceptFunc(self):
        LogUtil.d(TAG, "acceptFunc")
        name = self.categoryNameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入分类名")
            return
        desc = self.categoryDescLineEdit.text().strip()
        if not desc:
            WidgetUtil.showErrorDialog(message="请输入分类描述")
            return

        for item in DictUtil.get(self.categoryList, KEY_LIST, []):
            if name == item[KEY_NAME] and name != DictUtil.get(item, KEY_NAME):
                WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的分类名，{name}已经存在了，可以下拉选择")
                return

        id = MD5Util.md5(name)
        if self.categoryInfo is None:
            self.categoryInfo = {}
        self.categoryInfo[KEY_ID] = id
        self.categoryInfo[KEY_NAME] = name
        self.categoryInfo[KEY_DESC] = desc

        self.callback(self.categoryInfo if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditCategoryDialog(callback=lambda it: LogUtil.d(TAG, "callback", it), isDebug=True)
    window = AddOrEditCategoryDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                     categoryInfo={'id': '3691308f2a4c2f6983f2880d32e29c84', 'name': 'ss',
                                                   'desc': 'dddd'},
                                     categoryList=[{'id': '3691308f2a4c2f6983f2880d32e29c84', 'name': 'ss',
                                                    'desc': 'dddd'},
                                                   {'id': '3691308f2a4c2f6983f2880d32e2d9c84', 'name': 'ssss',
                                                    'desc': 'dddd'}],
                                     isDebug=True)
    window.show()
    sys.exit(app.exec_())
