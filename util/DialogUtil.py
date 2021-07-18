# -*- coding: utf-8 -*-
# python 3.x
# Filename: DialogUtil.py
# 定义一个DialogUtil工具类实现通用dialog功能
from util.WidgetUtil import *


class DialogUtil:
    @staticmethod
    def createBottomBtn(dialog: QDialog, okBtnText="Ok", okCallback=None, cancelBtnText=None, cancelCallback=None, ignoreBtnText=None, ignoreCallback=None):
        def okFunc():
            if okCallback:
                if okCallback():
                    # 有回调函数并且处理完成
                    dialog.close()
            else:
                dialog.close()

        def cancelFunc():
            if cancelCallback:
                if cancelCallback():
                    # 有回调函数并且处理完成
                    dialog.close()
            else:
                dialog.close()

        def ignoreFunc():
            if ignoreCallback:
                if ignoreCallback():
                    # 有回调函数并且处理完成
                    dialog.close()
            else:
                dialog.close()

        sizePolicy = WidgetUtil.createSizePolicy()
        hbox = WidgetUtil.createHBoxLayout()
        label = WidgetUtil.createLabel(dialog, sizePolicy=sizePolicy)
        hbox.addWidget(label)
        if ignoreBtnText:
            ignoreBtn = WidgetUtil.createPushButton(dialog, text=ignoreBtnText, onClicked=ignoreFunc)
            hbox.addWidget(ignoreBtn)
        if cancelBtnText:
            cancelBtn = WidgetUtil.createPushButton(dialog, text=cancelBtnText, onClicked=cancelFunc)
            hbox.addWidget(cancelBtn)
        okBtn = WidgetUtil.createPushButton(dialog, text=okBtnText, onClicked=okFunc)
        hbox.addWidget(okBtn)
        return hbox
        pass

    @staticmethod
    def showLineEditDialog(label="请在输入框输入内容：", title="", text="", acceptFunc=None):
        dialog = QtWidgets.QDialog()
        dialog.resize(300, 50)
        dialog.setObjectName("LineEditDialog")
        if title:
            dialog.setWindowTitle(title)
        vbox = WidgetUtil.createVBoxLayout()
        hbox = WidgetUtil.createHBoxLayout()
        hbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label = WidgetUtil.createLabel(dialog, text=label)
        lineEdit = WidgetUtil.createLineEdit(dialog, text=text)

        splitter = DialogUtil.createBottomBtn(dialog, okCallback=acceptFunc, cancelBtnText="Cancel")
        vbox.addWidget(label)
        vbox.addWidget(lineEdit)
        vbox.addLayout(splitter)

        dialog.setLayout(vbox)
        # 该模式下，只有该dialog关闭，才可以关闭父界面
        dialog.setWindowModality(Qt.ApplicationModal)
        # dialog.exec_()
        dialog.show()
