# -*- coding: utf-8 -*-
# python 3.x
# Filename: AddOrEditOptionGroupDialog.py
# 定义一个AddOrEditOptionGroupDialog类实现添加、编辑选项群组配置功能
import copy
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QToolTip
from constant.WidgetConst import *
from util.DialogUtil import *
from util.DictUtil import DictUtil
from util.ListUtil import ListUtil
from util.MD5Util import MD5Util
from util.OperaIni import *
from widget.projectManage.AddOrEditOptionDialog import AddOrEditOptionDialog
from widget.projectManage.ProjectManager import *

TAG = "AddOrEditOptionGroupDialog"


class AddOrEditOptionGroupDialog(QtWidgets.QDialog):
    def __init__(self, callback, default=None, groupList=None, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.currentRow = -1
        self.isDebug = isDebug
        self.callback = callback
        if groupList is None:
            groupList = []
        self.groupList = groupList
        self.isAdd = default is None
        if default is None:
            default = {KEY_OPTIONS: []}
        elif KEY_OPTIONS not in default:
            default[KEY_OPTIONS] = []
        self.default = default
        self.options = copy.deepcopy(default[KEY_OPTIONS])

        windowFlags = Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        if PlatformUtil.isMac():
            windowFlags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(windowFlags)
        AddOrEditOptionGroupDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.6)
        AddOrEditOptionGroupDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.5)
        LogUtil.d(TAG, "Add Or Edit Option Group Dialog")
        self.setWindowTitle(WidgetUtil.translate(text="添加/修改选项群组配置"))
        self.setObjectName("AddOrEditOptionGroupDialog")
        self.resize(AddOrEditOptionGroupDialog.WINDOW_WIDTH, AddOrEditOptionGroupDialog.WINDOW_HEIGHT)

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)
        self.setLayout(vLayout)

        self.moduleConfigGroupBox = self.createModuleConfigGroupBox(self)
        vLayout.addWidget(self.moduleConfigGroupBox)

        btnBox = WidgetUtil.createDialogButtonBox(parent=self, acceptedFunc=self.acceptFunc,
                                                  rejectedFunc=lambda: self.close())
        vLayout.addWidget(btnBox)
        self.setWindowModality(Qt.WindowModal)
        if not isDebug:
            # 很关键，不加出不来
            self.exec_()

    def createModuleConfigGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(5, 5, 5, 5), spacing=5)
        labelWidth = 100
        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="选项群组名：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.nameLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.default, KEY_NAME),
                                                      toolTip="选项群组可以由多个配置项拼接而成，强调一定的顺序，可以在table里调整")
        hbox.addWidget(self.nameLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createLabel(box, text="选项群组描述：", minSize=QSize(labelWidth, const.HEIGHT)))
        self.descLineEdit = WidgetUtil.createLineEdit(box, text=DictUtil.get(self.default, KEY_DESC))
        hbox.addWidget(self.descLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout(spacing=10)
        hbox.addWidget(WidgetUtil.createPushButton(box, text="添加选项", onClicked=self.addOption))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        hbox.addWidget(WidgetUtil.createLabel(box, text="顺序调整:"))
        self.topPostionBtn = WidgetUtil.createPushButton(box, text="⬆️️", toolTip="移动到首行", isEnable=False,
                                                         onClicked=lambda: self.moveOptionPosition(0))
        hbox.addWidget(self.topPostionBtn)
        self.upOnePostionBtn = WidgetUtil.createPushButton(box, text="↑️️", toolTip="向上移动一行", isEnable=False,
                                                           onClicked=lambda: self.moveOptionPosition(
                                                               self.currentRow - 1))
        hbox.addWidget(self.upOnePostionBtn)
        self.downOnePostionBtn = WidgetUtil.createPushButton(box, text="↓️", toolTip="向下移动一行", isEnable=False,
                                                             onClicked=lambda: self.moveOptionPosition(
                                                                 self.currentRow + 1))
        hbox.addWidget(self.downOnePostionBtn)
        self.bottomPostionBtn = WidgetUtil.createPushButton(box, text="⬇️️", toolTip="移动到末行", isEnable=False,
                                                            onClicked=lambda: self.moveOptionPosition(-1))
        hbox.addWidget(self.bottomPostionBtn)
        vbox.addLayout(hbox)

        self.tableView = WidgetUtil.createTableView(box, clicked=self.tableClicked,
                                                    doubleClicked=self.tableDoubleClicked)
        # 设为不可编辑
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置选中模式为选中行
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置选中单个
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        # 设置自定义右键菜单
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.customRightMenu)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # 列宽手动调整
        self.updateCmdTableView()
        vbox.addWidget(self.tableView, 1)
        return box

    def moveOptionPosition(self, newPos):
        LogUtil.d(TAG, "moveOptionPosition", newPos)
        # 交换数据
        ListUtil.insert(self.options, self.currentRow, newPos)
        # 更新table表格数据
        self.updateCmdTableView()
        # 更新当前选择的行
        self.currentRow = newPos if newPos >= 0 else len(self.options) - 1
        self.tableView.selectRow(self.currentRow)
        # 更新调整位置按钮的状态
        self.updatePositionBtnStatus()
        pass

    def addOption(self):
        LogUtil.d(TAG, "addOption")
        AddOrEditOptionDialog(callback=self.addOrEditOptionCallback, optionList=self.options)
        pass

    def addOrEditOptionCallback(self, info):
        LogUtil.d(TAG, "addOrEditOptionCallback", info)
        if info:
            self.options.append(info)
        self.updateCmdTableView()
        pass

    def updatePositionBtnStatus(self):
        LogUtil.d(TAG, "updatePositionBtnStatus")
        size = len(self.options)
        self.topPostionBtn.setEnabled(self.currentRow > 0)
        self.upOnePostionBtn.setEnabled(self.currentRow > 0)
        self.downOnePostionBtn.setEnabled(0 <= self.currentRow < size - 1)
        self.bottomPostionBtn.setEnabled(0 <= self.currentRow < size - 1)
        pass

    def tableClicked(self):
        currentRow = self.tableView.currentIndex().row()
        LogUtil.d(TAG, "tableClicked", currentRow)
        if currentRow != self.currentRow:
            self.currentRow = currentRow
            self.updatePositionBtnStatus()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        AddOrEditOptionDialog(callback=self.addOrEditOptionCallback, default=self.options[row],
                              optionList=self.options)
        pass

    def customRightMenu(self, pos):
        self.curDelRow = self.tableView.currentIndex().row()
        LogUtil.i(TAG, "customRightMenu", pos, ' row: ', self.curDelRow)
        menu = WidgetUtil.createMenu("删除", func1=self.delOption)
        menu.exec(self.tableView.mapToGlobal(pos))
        pass

    def delOption(self):
        option = self.options[self.curDelRow][KEY_NAME]
        LogUtil.i(TAG, f"delOption {option}")
        WidgetUtil.showQuestionDialog(message=f"你确定需要删除 <span style='color:red;'>{option}</span> 吗？",
                                      acceptFunc=self.delTableItem)
        pass

    def delTableItem(self):
        LogUtil.i(TAG, "delTableItem")
        self.options.remove(self.options[self.curDelRow])
        self.updateCmdTableView()
        pass

    def updateCmdTableView(self):
        tableData = []
        for item in self.options:
            tableData.append({
                KEY_NAME: DictUtil.get(item, KEY_NAME),
                KEY_DESC: DictUtil.get(item, KEY_DESC),
                KEY_ECHO: DictUtil.get(item, KEY_ECHO),
                KEY_DEFAULT: DictUtil.get(item, KEY_OPTION_VALUES)[item[KEY_DEFAULT]][KEY_DESC],
                KEY_OPTION_VALUES: DictUtil.get(item, KEY_OPTION_VALUES),
            })
        WidgetUtil.addTableViewData(self.tableView, tableData,
                                    headerLabels=["name", "描述", "情景文本", "默认选项", "选项列表"])
        # WidgetUtil.tableViewSetColumnWidth(self.cmdTableView, 0, 100)
        pass

    def acceptFunc(self):
        LogUtil.d(TAG, "acceptFunc")
        name = self.nameLineEdit.text().strip()
        if not name:
            WidgetUtil.showErrorDialog(message="请输入选项群组名")
            return
        desc = self.descLineEdit.text().strip()
        if not desc:
            WidgetUtil.showErrorDialog(message="请输入选项群组描述")
            return

        if self.isAdd or self.default[KEY_NAME] != name:
            for item in self.groupList:
                if name == item[KEY_NAME]:
                    WidgetUtil.showErrorDialog(message=f"请重新添加一个其他的选项群组，{name}已经存在了。")
                    return

        if self.default is None:
            self.default = {}
        self.default[KEY_ID] = MD5Util.md5(name)
        self.default[KEY_NAME] = name
        self.default[KEY_DESC] = desc
        self.default[KEY_OPTIONS] = self.options

        self.callback(self.default if self.isAdd else None)
        self.close()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # window = AddOrEditOptionGroupDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
    #                                     isDebug=True)
    window = AddOrEditOptionGroupDialog(callback=lambda it: LogUtil.d(TAG, "callback", it),
                                        default={'options': [
                                            {'default': 0,
                                             'optionValues': [{'value': 'product', 'desc': '现网环境', 'input': 'A'}],
                                             'name': 'productFlavors', 'desc': '打包渠道', 'echo': '请输入环境'}],
                                            'id': 'f7b9d4a9655e78ca1f665ed463919fe3', 'name': 'buildGroup',
                                            'desc': '打包指令'},
                                        isDebug=True)
    window.show()
    sys.exit(app.exec_())
