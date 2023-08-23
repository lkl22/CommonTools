# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidColorResDialog.py
# 定义一个AndroidColorResDialog类实现android color资源管理
from PyQt5.QtCore import QModelIndex

from constant.WidgetConst import *
from util.ExcelUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.OperaIni import *

TAG = "AndroidColorResDialog"


class AndroidColorResDialog(QtWidgets.QDialog):
    KEY_FIND_EXCEL_FN = "findExcelFn"
    SECTION_ANDROID = "android"

    KEY_COLOR_NAME = "colorName"
    KEY_COLOR_NAME_COL_NUM = 0
    KEY_NORMAL_COLOR = "normalColor"
    KEY_NORMAL_COLOR_COL_NUM = 1
    KEY_DARK_COLOR = "darkColor"
    KEY_DARK_COLOR_COL_NUM = 2
    KEY_ROW = "row"

    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AndroidColorResDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        AndroidColorResDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.7)
        LogUtil.d(TAG, "Init Android color Res Dialog")
        self.setObjectName("AndroidColorResDialog")
        self.resize(AndroidColorResDialog.WINDOW_WIDTH, AndroidColorResDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AndroidColorResDialog.WINDOW_WIDTH, AndroidColorResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android color资源管理"))

        self.normalColorRes = {}
        self.darkColorRes = {}

        # 查找的数据源
        self.findColorRes = [{}]
        # 查找到的结果
        self.findColorResResult = [{}]
        # 当前正在编辑的color资源
        self.curEditColorRes = {}

        vLayout = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        generateExcelGroupBox = self.createGenerateExcelGroupBox(self)
        opacityGroupBox = self.createOpacityGroupBox(self)
        findGroupBox = self.createFindGroupBox(self)

        vLayout.addWidget(generateExcelGroupBox)
        vLayout.addWidget(opacityGroupBox)
        vLayout.addWidget(findGroupBox, 1)

        if isDebug:
            self.operaIni = OperaIni('../../resources/config/BaseConfig.ini')
        else:
            self.operaIni = OperaIni()

        LogUtil.d(TAG, FileUtil.getProjectPath())

        findExcelFn = self.operaIni.getValue(AndroidColorResDialog.KEY_FIND_EXCEL_FN,
                                             AndroidColorResDialog.SECTION_ANDROID)
        if findExcelFn:
            if self.initFindColorRes(findExcelFn):
                self.findExcelFnLineEdit.setText(findExcelFn)
                self.colorNameLineEdit.setEnabled(True)
                self.normalColorLineEdit.setEnabled(True)
                self.darkColorLineEdit.setEnabled(True)
                self.findColorResBtn.setEnabled(True)
                self.addColorResBtn.setEnabled(True)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def createGenerateExcelGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="生成Excel")

        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(
            WidgetUtil.createPushButton(box, text="normal color res XML文件路径", minSize=QSize(120, const.HEIGHT),
                                        onClicked=self.getSrcFilePath))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.srcFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="dark color res XML文件路径", onClicked=self.getDstFilePath))
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.dstFilePathLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="生成Excel文件路径", onClicked=self.getGenerateExcelFilePath))
        self.generateExcelLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.generateExcelLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="生成Excel", onClicked=self.generateExcel))
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)
        return box

    def getSrcFilePath(self):
        fp = WidgetUtil.getOpenFileName()
        if fp:
            self.srcFilePathLineEdit.setText(fp)
            self.normalColorRes = DomXmlUtil.readAndroidRes(fp)
            # print(self.normalColorRes)
        pass

    def getDstFilePath(self):
        fp = WidgetUtil.getOpenFileName()
        if fp:
            self.dstFilePathLineEdit.setText(fp)
            self.darkColorRes = DomXmlUtil.readAndroidRes(fp)
            # print(self.darkColorRes)
        pass

    def getGenerateExcelFilePath(self):
        fp = WidgetUtil.getExistingDirectory()
        if fp:
            self.generateExcelLineEdit.setText(fp)
        pass

    def generateExcel(self):
        fp = self.generateExcelLineEdit.text().strip()
        if not fp:
            WidgetUtil.showErrorDialog(message="请选择生成Excel文件存储路径")
            return
        fn = os.path.join(fp, 'AndroidRes.xls')
        bk = ExcelUtil.createBook()
        st = ExcelUtil.addSheet(bk, 'color')
        ExcelUtil.writeSheet(st, 0, AndroidColorResDialog.KEY_COLOR_NAME_COL_NUM, 'key')
        ExcelUtil.writeSheet(st, 0, AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM, 'normal')
        ExcelUtil.writeSheet(st, 0, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM, 'dark')
        row = 1
        for key, value in self.normalColorRes.items():
            ExcelUtil.writeSheet(st, row, AndroidColorResDialog.KEY_COLOR_NAME_COL_NUM, key)
            ExcelUtil.writeSheet(st, row, AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM, value)
            darkColor = self.darkColorRes.get(key)
            if darkColor:
                ExcelUtil.writeSheet(st, row, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM, darkColor)
            else:
                ExcelUtil.writeSheet(st, row, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM, '')
            row = row + 1
        ExcelUtil.saveBook(bk, fn)
        pass

    def createOpacityGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="计算不透明度")

        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()

        hbox.addWidget(WidgetUtil.createLabel(box, text="不透明度：", minSize=QSize(50, const.HEIGHT)))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.percentOpacitySpinBox = WidgetUtil.createSpinBox(box, value=0, minValue=0, maxValue=100, step=5,
                                                              suffix='%',
                                                              sizePolicy=sizePolicy,
                                                              valueChanged=self.percentOpacityChanged)
        hbox.addWidget(self.percentOpacitySpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="透明度：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.percentOpennessSpinBox = WidgetUtil.createSpinBox(box, value=100, minValue=0, maxValue=100, step=5,
                                                               suffix='%',
                                                               sizePolicy=sizePolicy,
                                                               valueChanged=self.percentOpennessChanged)
        hbox.addWidget(self.percentOpennessSpinBox)
        hbox.addWidget(WidgetUtil.createLabel(box, text="16进制数值：", alignment=Qt.AlignVCenter | Qt.AlignRight,
                                              minSize=QSize(120, const.HEIGHT)))
        self.hexOpacitySpinBox = WidgetUtil.createSpinBox(box, value=0, minValue=0, maxValue=255, step=1,
                                                          prefix='0x',
                                                          intBase=16, sizePolicy=sizePolicy,
                                                          valueChanged=self.hexOpacityChanged)
        hbox.addWidget(self.hexOpacitySpinBox)
        vbox.addLayout(hbox)
        return box

    def percentOpacityChanged(self):
        percentOpacity = self.percentOpacitySpinBox.value()
        percentOpenness = 100 - percentOpacity
        self.percentOpennessSpinBox.setValue(percentOpenness)
        hexOpacity = int(255 * percentOpacity / 100 + 0.5)
        self.hexOpacitySpinBox.setValue(hexOpacity)
        pass

    def percentOpennessChanged(self):
        percentOpenness = self.percentOpennessSpinBox.value()
        percentOpacity = 100 - percentOpenness
        self.percentOpacitySpinBox.setValue(percentOpacity)
        hexOpacity = int(255 * percentOpacity / 100 + 0.5)
        self.hexOpacitySpinBox.setValue(hexOpacity)
        pass

    def hexOpacityChanged(self):
        hexOpacity = self.hexOpacitySpinBox.value()
        percentOpacity = int(hexOpacity * 100 / 255 + 0.5)
        percentOpenness = 100 - percentOpacity
        self.percentOpennessSpinBox.setValue(percentOpenness)
        self.percentOpacitySpinBox.setValue(percentOpacity)
        pass

    def createFindGroupBox(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy()
        box = WidgetUtil.createGroupBox(parent, title="查找资源", sizePolicy=sizePolicy)
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createPushButton(box, text="color资源汇总Excel文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getExcelFile))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.findExcelFnLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy)
        hbox.addWidget(self.findExcelFnLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        hbox.addWidget(WidgetUtil.createLabel(box, text="资源名称", alignment=Qt.AlignVCenter | Qt.AlignLeft,
                               minSize=QSize(80, const.HEIGHT)))
        self.colorNameLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy,
                                                           textChanged=self.colorNameTextChange)
        hbox.addWidget(self.colorNameLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="normal color", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT)))
        self.normalColorLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy,
                                                             textChanged=self.normalColorTextChange)
        hbox.addWidget(self.normalColorLineEdit)
        hbox.addWidget(WidgetUtil.createLabel(box, text="dark color", alignment=Qt.AlignVCenter | Qt.AlignRight,
                               minSize=QSize(120, const.HEIGHT)))
        self.darkColorLineEdit = WidgetUtil.createLineEdit(box, isEnable=False, sizePolicy=sizePolicy,
                                                           textChanged=self.darkColorTextChange)
        hbox.addWidget(self.darkColorLineEdit)
        vbox.addLayout(hbox)

        hbox = WidgetUtil.createHBoxLayout()
        self.findColorResBtn = WidgetUtil.createPushButton(box, text="查找", isEnable=False, onClicked=self.findRes)
        hbox.addWidget(self.findColorResBtn)
        self.addColorResBtn = WidgetUtil.createPushButton(box, text="添加color资源", isEnable=False,
                                                          onClicked=self.addColorRes)
        hbox.addWidget(self.addColorResBtn)
        hbox.addItem(WidgetUtil.createHSpacerItem(1, 1))
        vbox.addLayout(hbox)

        self.findResTableView = WidgetUtil.createTableView(box, doubleClicked=self.tableDoubleClicked)
        vbox.addWidget(self.findResTableView, 1)
        return box

    def getExcelFile(self):
        fp = WidgetUtil.getOpenFileName(caption='选择color资源汇总Excel文件', filter='*.xls', initialFilter='*.xls')
        if fp:
            res = self.initFindColorRes(fp)
            if res:
                self.findExcelFnLineEdit.setText(fp)
                self.operaIni.addItem(AndroidColorResDialog.SECTION_ANDROID, AndroidColorResDialog.KEY_FIND_EXCEL_FN,
                                      fp)
                self.operaIni.saveIni()
                self.colorNameLineEdit.setEnabled(True)
                self.normalColorLineEdit.setEnabled(True)
                self.darkColorLineEdit.setEnabled(True)
                self.findColorResBtn.setEnabled(True)
                self.addColorResBtn.setEnabled(True)
        pass

    def initFindColorRes(self, fn):
        st = ExcelUtil.getSheet(fn, 0)
        if st:
            self.findColorRes = []
            lines = ExcelUtil.getRows(st)
            for i in range(1, lines):
                key = ExcelUtil.getCell(st, i, 0)
                if key:
                    colorRes = {AndroidColorResDialog.KEY_COLOR_NAME: key}
                    normalColor = ExcelUtil.getCell(st, i, AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM)
                    colorRes[AndroidColorResDialog.KEY_NORMAL_COLOR] = normalColor

                    darkColor = ExcelUtil.getCell(st, i, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM)
                    colorRes[AndroidColorResDialog.KEY_DARK_COLOR] = darkColor
                    colorRes[AndroidColorResDialog.KEY_ROW] = i

                    self.findColorRes.append(colorRes)
            if self.findColorRes:
                print(self.findColorRes)
                return True
        else:
            return False

    def colorNameTextChange(self, data):
        if data:
            self.normalColorLineEdit.setEnabled(False)
            self.darkColorLineEdit.setEnabled(False)
        else:
            self.normalColorLineEdit.setEnabled(True)
            self.darkColorLineEdit.setEnabled(True)
        pass

    def normalColorTextChange(self, data):
        if data:
            self.colorNameLineEdit.setEnabled(False)
        else:
            if not self.darkColorLineEdit.text().strip():
                self.colorNameLineEdit.setEnabled(True)
        pass

    def darkColorTextChange(self, data):
        if data:
            self.colorNameLineEdit.setEnabled(False)
        else:
            if not self.normalColorLineEdit.text().strip():
                self.colorNameLineEdit.setEnabled(True)
        pass

    def findRes(self):
        colorName = self.colorNameLineEdit.text().strip()
        res = []
        if colorName:
            LogUtil.e(TAG, "需要查找的color name：", colorName)
            for colorRes in self.findColorRes:
                if colorName in colorRes[AndroidColorResDialog.KEY_COLOR_NAME]:
                    res.append(colorRes)
        else:
            normalColor = self.normalColorLineEdit.text().strip().upper()
            darkColor = self.darkColorLineEdit.text().strip().upper()
            if normalColor:
                LogUtil.e(TAG, "需要查找的normal color：", normalColor)
            if darkColor:
                LogUtil.e(TAG, "需要查找的dark color：", darkColor)
            for colorRes in self.findColorRes:
                if normalColor in colorRes[AndroidColorResDialog.KEY_NORMAL_COLOR] and darkColor in colorRes[
                    AndroidColorResDialog.KEY_DARK_COLOR]:
                    res.append(colorRes)
            if not (normalColor or darkColor):
                LogUtil.e(TAG, "没有查询条件，查询所有数据")
                res = self.findColorRes
        LogUtil.e(TAG, "查找到的资源：", res)
        self.findColorResResult = res
        WidgetUtil.addTableViewData(self.findResTableView, data=res, ignoreCol=[AndroidColorResDialog.KEY_ROW],
                                    itemChanged=self.tableItemChanged)
        pass

    def addColorRes(self):
        LogUtil.i(TAG, "jumpAddColorResDialog")
        from widget.colorManager.AddColorResDialog import AddColorResDialog
        dialog = AddColorResDialog(self.addColorHandle, self.findColorRes)
        # dialog.show()
        pass

    def addColorHandle(self, colorName, normalColor, darkColor):
        LogUtil.e(TAG, "新添加color资源：", colorName, "  ", normalColor, " dark: ", darkColor)
        fp = self.findExcelFnLineEdit.text().strip()
        oldBk = ExcelUtil.getBook(fp)
        nrows = oldBk.sheets()[0].nrows
        newBk: Workbook = ExcelUtil.copyBook(oldBk)
        st: Worksheet = newBk.get_sheet(0)
        st.write(nrows, AndroidColorResDialog.KEY_COLOR_NAME_COL_NUM, colorName)
        st.write(nrows, AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM, normalColor)
        st.write(nrows, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM, darkColor)
        self.findColorRes.append(
            {AndroidColorResDialog.KEY_COLOR_NAME: colorName, AndroidColorResDialog.KEY_NORMAL_COLOR: normalColor,
             AndroidColorResDialog.KEY_DARK_COLOR: darkColor, AndroidColorResDialog.KEY_ROW: nrows})
        newBk.save(fp)
        # 添加了数据，重新查询一遍结果
        self.findRes()
        pass

    def tableItemChanged(self, item: QStandardItem):
        newData = item.text().strip()
        col = item.column()
        LogUtil.d(TAG, "编辑的单元格：row ", item.row(), ' col', col, ' data ', newData)
        if AndroidColorResDialog.KEY_COLOR_NAME_COL_NUM == col:
            for colorRes in self.findColorRes:
                if colorRes[AndroidColorResDialog.KEY_COLOR_NAME] == newData \
                        and self.curEditColorRes[AndroidColorResDialog.KEY_COLOR_NAME] != newData:
                    WidgetUtil.showErrorDialog(
                        message=newData + "已经存在了，请输入不一样的color name")
                    item.setText(self.curEditColorRes[AndroidColorResDialog.KEY_COLOR_NAME])
                    return
            if self.curEditColorRes[AndroidColorResDialog.KEY_COLOR_NAME] != newData:
                # 修改了并且满足条件
                self.curEditColorRes[AndroidColorResDialog.KEY_COLOR_NAME] = newData
                self.editExcel()
        elif AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM == col:
            if not ReUtil.matchColor(newData):
                WidgetUtil.showErrorDialog(message="normal color请输入正确的颜色值（#FFF、#FFFFFF、#FFFFFFFF、666、666666、66666666）")
                item.setText(self.curEditColorRes[AndroidColorResDialog.KEY_NORMAL_COLOR])
                return
            if self.curEditColorRes[AndroidColorResDialog.KEY_NORMAL_COLOR] != newData:
                # 修改了并且满足条件
                self.curEditColorRes[AndroidColorResDialog.KEY_NORMAL_COLOR] = newData
                self.editExcel()
        elif AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM == col:
            if newData and not ReUtil.matchColor(newData):
                WidgetUtil.showErrorDialog(message="dark color请输入正确的颜色值（#FFF、#FFFFFF、#FFFFFFFF、666、666666、66666666）")
                item.setText(self.curEditColorRes[AndroidColorResDialog.KEY_DARK_COLOR])
                return
            if self.curEditColorRes[AndroidColorResDialog.KEY_DARK_COLOR] != newData:
                # 修改了并且满足条件
                self.curEditColorRes[AndroidColorResDialog.KEY_DARK_COLOR] = newData
                self.editExcel()
        pass

    def editExcel(self):
        colorName = self.curEditColorRes[AndroidColorResDialog.KEY_COLOR_NAME]
        normalColor = self.curEditColorRes[AndroidColorResDialog.KEY_NORMAL_COLOR]
        darkColor = self.curEditColorRes[AndroidColorResDialog.KEY_DARK_COLOR]
        row = self.curEditColorRes[AndroidColorResDialog.KEY_ROW]
        LogUtil.e(TAG, "编辑color资源：", colorName, "  ", normalColor, " dark: ", darkColor, ' row ', row)
        fp = self.findExcelFnLineEdit.text().strip()
        oldBk = ExcelUtil.getBook(fp)
        newBk: Workbook = ExcelUtil.copyBook(oldBk)
        st: Worksheet = newBk.get_sheet(0)
        st.write(row, AndroidColorResDialog.KEY_COLOR_NAME_COL_NUM, colorName)
        st.write(row, AndroidColorResDialog.KEY_NORMAL_COLOR_COL_NUM, normalColor)
        st.write(row, AndroidColorResDialog.KEY_DARK_COLOR_COL_NUM, darkColor)
        newBk.save(fp)
        # 修改了数据，重新查询一遍结果
        self.findRes()
        pass

    def tableDoubleClicked(self, index: QModelIndex):
        oldValue = index.data()
        row = index.row()
        LogUtil.d(TAG, "双击的单元格：row ", row, ' col', index.column(), ' data ', oldValue)
        colorRes = self.findColorResResult[row]
        LogUtil.d(TAG, "Excel中源数据：row ", colorRes[AndroidColorResDialog.KEY_ROW], ' colorName ',
                  colorRes[AndroidColorResDialog.KEY_COLOR_NAME],
                  ' normalColor ', colorRes[AndroidColorResDialog.KEY_NORMAL_COLOR], ' darkColor ',
                  colorRes[AndroidColorResDialog.KEY_DARK_COLOR])
        self.curEditColorRes = colorRes
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AndroidColorResDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())
