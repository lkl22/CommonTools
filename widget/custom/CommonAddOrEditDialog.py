# -*- coding: utf-8 -*-
# python 3.x
# Filename: CommonAddOrEditDialog.py
# 定义一个CommonAddOrEditDialog类实现添加、编辑相关数据相关的功能
import os.path
import sys
from util.DialogUtil import *
from util.DictUtil import DictUtil
from widget.custom.CommonLineEdit import CommonLineEdit
from widget.custom.CommonSpinBox import CommonSpinBox
from widget.custom.DragInputWidget import DragInputWidget, KEY_CAPTION, KEY_DIRECTORY, KEY_FILTER, KEY_INITIAL_FILTER
from widget.custom.ICommonWidget import ICommonWidget

TAG = "CommonAddOrEditDialog"


class CommonAddOrEditDialog(QtWidgets.QDialog):
    def __init__(self, windowTitle: str, optionInfos: [{}], default=None, items: [] = None, callback=None, width=0.3,
                 height=0.2, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        CommonAddOrEditDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * width)
        CommonAddOrEditDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * height)
        LogUtil.d(TAG, "CommonAddOrEditDialog")
        self.setWindowTitle(WidgetUtil.translate(text=windowTitle))
        self.setObjectName("CommonAddOrEditDialog")
        self.resize(CommonAddOrEditDialog.WINDOW_WIDTH, CommonAddOrEditDialog.WINDOW_HEIGHT)
        # self.setFixedSize(CommonAddOrEditDialog.WINDOW_WIDTH, CommonAddOrEditDialog.WINDOW_HEIGHT)

        self.__default = default if default else {}
        self.__items = items if items else []
        self.__callback = callback
        self.__isAdd = default is None

        self.__optionInfos = []
        self.__widgets: [ICommonWidget] = []

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        labelWidth = 120
        for optionInfo in optionInfos:
            itemType = DictUtil.get(optionInfo, KEY_ITEM_TYPE)
            defaultValue = DictUtil.get(self.__default, optionInfo[KEY_ITEM_KEY], '')
            if itemType == TYPE_LINE_EDIT:
                widget = CommonLineEdit(label=DictUtil.get(optionInfo, KEY_ITEM_LABEL),
                                        text=defaultValue,
                                        labelMinSize=QSize(labelWidth, 0),
                                        toolTip=DictUtil.get(optionInfo, KEY_TOOL_TIP))
            elif itemType == TYPE_SPIN_BOX:
                widget = CommonSpinBox(label=DictUtil.get(optionInfo, KEY_ITEM_LABEL),
                                       value=defaultValue,
                                       minValue=DictUtil.get(optionInfo, KEY_MIN_VALUE),
                                       maxValue=DictUtil.get(optionInfo, KEY_MAX_VALUE),
                                       step=DictUtil.get(optionInfo, KEY_STEP),
                                       prefix=DictUtil.get(optionInfo, KEY_PREFIX),
                                       suffix=DictUtil.get(optionInfo, KEY_SUFFIX),
                                       intBase=DictUtil.get(optionInfo, KEY_INT_BASE),
                                       labelMinSize=QSize(labelWidth, 0),
                                       toolTip=DictUtil.get(optionInfo, KEY_TOOL_TIP))
            elif itemType == TYPE_SELECT_FILE:
                fileParam = DictUtil.get(optionInfo, KEY_FILE_PARAM, {KEY_DIRECTORY: ''})
                if defaultValue:
                    fp, _ = os.path.split(defaultValue)
                    fileParam = DictUtil.join([fileParam, {KEY_DIRECTORY: fp}])
                widget = DragInputWidget(label=DictUtil.get(optionInfo, KEY_ITEM_LABEL),
                                         text=defaultValue,
                                         fileParam=fileParam,
                                         labelMinSize=QSize(labelWidth, 0),
                                         toolTip=DictUtil.get(optionInfo, KEY_TOOL_TIP))
            elif itemType == TYPE_SELECT_DIR:
                dirParam = DictUtil.get(optionInfo, KEY_DIR_PARAM, {KEY_DIRECTORY: ''})
                if defaultValue:
                    fp, _ = os.path.split(defaultValue)
                    dirParam = DictUtil.join([dirParam, {KEY_DIRECTORY: fp}])
                widget = DragInputWidget(label=DictUtil.get(optionInfo, KEY_ITEM_LABEL),
                                         text=defaultValue,
                                         dirParam=dirParam,
                                         labelMinSize=QSize(labelWidth, 0),
                                         toolTip=DictUtil.get(optionInfo, KEY_TOOL_TIP))
            else:
                LogUtil.e(TAG, f'{itemType} not support.')
                continue
            vLayout.addWidget(widget)
            self.__optionInfos.append(optionInfo)
            self.__widgets.append(widget)

        vLayout.addItem(WidgetUtil.createVSpacerItem(1, 1))

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()
        pass

    def acceptFunc(self):
        for index, optionInfo in enumerate(self.__optionInfos):
            data = self.__widgets[index].getData()
            if not DictUtil.get(optionInfo, KEY_IS_OPTIONAL, False):
                if not data:
                    WidgetUtil.showErrorDialog(
                        message=DictUtil.get(optionInfo, KEY_TOOL_TIP, f'{optionInfo[KEY_ITEM_LABEL]}必须设置值'))
                    return
            if DictUtil.get(optionInfo, KEY_IS_UNIQUE, False):
                key = optionInfo[KEY_ITEM_KEY]
                if self.__isAdd or DictUtil.get(self.__default, key) != data:
                    for item in self.__items:
                        if data == item[key]:
                            WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的，{data}已经存在了，不能重复添加")
                            return
            self.__default[optionInfo[KEY_ITEM_KEY]] = data

        if self.__callback:
            self.__callback(self.__default if self.__isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CommonAddOrEditDialog(windowTitle='添加/编辑规则',
                                   optionInfos=[{
                                       KEY_ITEM_KEY: 'name',
                                       KEY_ITEM_TYPE: TYPE_LINE_EDIT,
                                       KEY_ITEM_LABEL: '规则名：',
                                       KEY_IS_OPTIONAL: True,
                                       KEY_TOOL_TIP: '请输入规则名',
                                       KEY_IS_UNIQUE: True
                                   }, {
                                       KEY_ITEM_KEY: 'srcFile',
                                       KEY_ITEM_TYPE: TYPE_SELECT_FILE,
                                       KEY_ITEM_LABEL: '请选则源文件：',
                                       KEY_IS_OPTIONAL: True,
                                       KEY_FILE_PARAM: {KEY_CAPTION: "file", KEY_DIRECTORY: "./", KEY_FILTER: "*.py",
                                                        KEY_INITIAL_FILTER: "*.py"}
                                   }, {
                                       KEY_ITEM_KEY: 'dstDst',
                                       KEY_ITEM_TYPE: TYPE_SELECT_DIR,
                                       KEY_ITEM_LABEL: '请选则目标路径：',
                                       KEY_IS_OPTIONAL: True,
                                       KEY_DIR_PARAM: {KEY_CAPTION: "file", KEY_DIRECTORY: "./"}
                                   }],
                                   callback=lambda it: LogUtil.d(TAG, "callback", it),
                                   # default={"name": 'dd', 'srcFile': '/Users/likunlun/PycharmProjects/CommonTools/widget/custom/progressBar/RoundProgressBar.py'},
                                   items=[{"name": 'dd'}],
                                   isDebug=True)
    window.show()
    sys.exit(app.exec_())
