# -*- coding: utf-8 -*-
# python 3.x
# Filename: FindFileContentDialog.py
# 定义一个FindFileContentDialog类实现批量查找文件内容功能
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView

from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.OperaIni import *
from util.ReUtil import ReUtil
from widget.custom.DragInputWidget import DragInputWidget
from widget.findFileContent.AddOrEditConfigDialog import AddOrEditConfigDialog
from widget.findFileContent.FindFileContentManager import *

TAG = "FindFileContentDialog"


class FindFileContentDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        FindFileContentDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        FindFileContentDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "FindFileContentDialog")
        self.setWindowTitle(WidgetUtil.translate(text="批量查找文件中包含的指定内容"))

        self.setObjectName("FindFileContentDialog")
        self.resize(FindFileContentDialog.WINDOW_WIDTH, FindFileContentDialog.WINDOW_HEIGHT)
        # self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)

        self.isDebug = isDebug
        self.manager = FindFileContentManager(isDebug=isDebug)
        self.configs = self.manager.configs
        if not self.configs:
            self.configs = {KEY_DEFAULT: None, KEY_LIST: []}
        self.defaultName = DictUtil.get(self.configs, KEY_DEFAULT, "")
        self.configList = DictUtil.get(self.configs, KEY_LIST, [])
        self.curConfigInfo = ListUtil.find(self.configList, KEY_NAME, self.defaultName)
        if not self.curConfigInfo:
            self.curConfigInfo = {}

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.managerGroupBox = self.createManagerGroupBox(self)
        vLayout.addWidget(self.managerGroupBox)

        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createManagerGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        labelWidth = 120
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="请选择配置：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.configsComboBox = WidgetUtil.createComboBox(box, activated=self.configIndexChanged)
        self.updateConfigComboBox()
        hbox.addWidget(self.configsComboBox, 1)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Add", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.addConfig))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="Edit", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.editConfig))
        hbox.addWidget(WidgetUtil.createPushButton(box, text="del", minSize=QSize(labelWidth, const.HEIGHT),
                                                   onClicked=self.delConfig))
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="工程路径：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.pathInputWidget = DragInputWidget(
            text=DictUtil.get(self.curConfigInfo, KEY_PATH),
            dirParam=["请选择您工程工作目录", "./"], isReadOnly=True,
            holderText="请拖动您工程的工作目录到此框或者点击右侧的按钮选择您的工程路径")
        hbox.addWidget(self.pathInputWidget)
        vbox.addLayout(hbox)
        return box

    def updateConfigComboBox(self):
        if self.configList:
            self.configsComboBox.clear()
            for index, item in enumerate(self.configList):
                self.configsComboBox.addItem(item[KEY_NAME], item)
            if not self.curConfigInfo:
                self.curConfigInfo = self.configList[0]
            self.configsComboBox.setCurrentText(self.curConfigInfo[KEY_NAME])
            LogUtil.d(TAG, 'updateConfigComboBox setCurrentText', self.curConfigInfo)
        pass

    def configIndexChanged(self, index):
        configInfo = self.configsComboBox.currentData()
        if configInfo:
            self.curConfigInfo = configInfo
        LogUtil.d(TAG, 'configIndexChanged', index, self.curConfigInfo, configInfo)
        self.updateConfigInfo()
        pass

    def addConfig(self):
        LogUtil.d(TAG, "addConfig")
        AddOrEditConfigDialog(configList=self.configs[KEY_LIST], callback=self.addOrEditConfigCallback, isDebug=self.isDebug).show()
        pass

    def editConfig(self):
        LogUtil.d(TAG, "editConfig")
        AddOrEditConfigDialog(configList=self.configs[KEY_LIST], callback=self.addOrEditConfigCallback, isDebug=self.isDebug).show()
        pass

    def delConfig(self):
        LogUtil.d(TAG, "delConfig")
        # name = self.matchList[self.curDelRow][KEY_NAME]
        # LogUtil.i(TAG, f"delMatch {name}")
        # WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{name}</span> 吗？",
        #                               acceptFunc=self.delTableItem)
        pass

    def addOrEditConfigCallback(self, info):
        LogUtil.d(TAG, "addOrEditConfigCallback", info)
        if info:
            self.configList.append(info)
        self.configList = sorted(self.configList, key=lambda x: x[KEY_NAME])
        self.updateConfigComboBox()
        self.updateConfigInfo()
        pass

    def updateConfigInfo(self):
        self.configs[KEY_DEFAULT] = DictUtil.get(self.curConfigInfo, KEY_NAME)
        self.configs[KEY_LIST] = self.configList
        self.manager.saveConfigInfos(self.configs)
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FindFileContentDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
