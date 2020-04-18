# -*- coding: utf-8 -*-
# python 3.x
# Filename: AndroidColorResDialog.py
# 定义一个AndroidColorResDialog类实现android color资源管理
from constant.WidgetConst import *
from util.ExcelUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *
from util.OperaIni import *


class AndroidColorResDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600

    KEY_FIND_EXCEL_FN = "findExcelFn"
    SECTION_ANDROID = "android"

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Android color Res Dialog")
        self.setObjectName("AndroidColorResDialog")
        self.resize(AndroidColorResDialog.WINDOW_WIDTH, AndroidColorResDialog.WINDOW_HEIGHT)
        self.setFixedSize(AndroidColorResDialog.WINDOW_WIDTH, AndroidColorResDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Android color资源管理"))

        self.normalColorRes = {}
        self.darkColorRes = {}

        self.findColorRes = [{}]

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, AndroidColorResDialog.WINDOW_WIDTH - const.PADDING * 2,
                                       AndroidColorResDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        generateExcelGroupBox = self.createGenerateExcelGroupBox(layoutWidget)
        findGroupBox = self.createFindGroupBox(layoutWidget)

        vLayout.addWidget(generateExcelGroupBox)
        vLayout.addWidget(findGroupBox)

        self.operaIni = OperaIni(FileUtil.getProjectPath() + "/CommonTools/config/BaseConfig.ini")

        LogUtil.d(FileUtil.getProjectPath())

        findExcelFn = self.operaIni.getValue(AndroidColorResDialog.KEY_FIND_EXCEL_FN,
                                             AndroidColorResDialog.SECTION_ANDROID)
        if findExcelFn:
            if self.initFindColorRes(findExcelFn):
                self.findExcelFnLineEdit.setText(findExcelFn)
                self.colorNameLineEdit.setEnabled(True)
                self.normalColorLineEdit.setEnabled(True)
                self.darkColorLineEdit.setEnabled(True)
                self.addColorResBtn.setEnabled(True)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createGenerateExcelGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidColorResDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="生成Excel", minSize=QSize(width, const.GROUP_BOX_MARGIN_TOP + const.HEIGHT_OFFSET * 5))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))

        WidgetUtil.createPushButton(splitter, text="normal color res XML文件路径", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getSrcFilePath)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="dark color res XML文件路径", onClicked=self.getDstFilePath)
        self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="生成Excel文件路径", onClicked=self.getGenerateExcelFilePath)
        self.generateExcelLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 100, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="生成Excel", onClicked=self.generateExcel)
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
        ExcelUtil.writeSheet(st, 0, 0, 'key')
        ExcelUtil.writeSheet(st, 0, 1, 'normal')
        ExcelUtil.writeSheet(st, 0, 2, 'dark')
        row = 1
        for key, value in self.normalColorRes.items():
            ExcelUtil.writeSheet(st, row, 0, key)
            ExcelUtil.writeSheet(st, row, 1, value)
            darkColor = self.darkColorRes.get(key)
            if darkColor:
                ExcelUtil.writeSheet(st, row, 2, darkColor)
            row = row + 1
        ExcelUtil.saveBook(bk, fn)
        pass

    def createFindGroupBox(self, parent):
        sizePolicy = WidgetUtil.createSizePolicy()
        box = WidgetUtil.createGroupBox(parent, title="查找资源", sizePolicy=sizePolicy)
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidColorResDialog.WINDOW_WIDTH - const.PADDING * 4
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="color资源汇总Excel文件", minSize=QSize(120, const.HEIGHT),
                                    onClicked=self.getExcelFile)
        sizePolicy = WidgetUtil.createSizePolicy()
        self.findExcelFnLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        WidgetUtil.createLabel(splitter, text="资源名称", alignment=Qt.AlignVCenter | Qt.AlignLeft, minSize=QSize(80, const.HEIGHT))
        sizePolicy = WidgetUtil.createSizePolicy()
        self.colorNameLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy, textChanged=self.colorNameTextChange)

        WidgetUtil.createLabel(splitter, text="normal color", alignment=Qt.AlignVCenter | Qt.AlignRight, minSize=QSize(120, const.HEIGHT))
        self.normalColorLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy, textChanged=self.normalColorTextChange)

        WidgetUtil.createLabel(splitter, text="dark color", alignment=Qt.AlignVCenter | Qt.AlignRight, minSize=QSize(120, const.HEIGHT))
        self.darkColorLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy, textChanged=self.darkColorTextChange)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 200, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="查找", onClicked=self.findRes)
        self.addColorResBtn = WidgetUtil.createPushButton(splitter, text="添加color资源", isEnable=False, onClicked=self.addColorRes)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, 230))
        self.findResTableView = WidgetUtil.createTableView(splitter, minSize=QSize(width, 200), sizePolicy=sizePolicy)

        return box

    def getExcelFile(self):
        fp = WidgetUtil.getOpenFileName(caption='选择color资源汇总Excel文件', filter='*.xls', initialFilter='*.xls')
        if fp:
            res = self.initFindColorRes(fp)
            if res:
                self.findExcelFnLineEdit.setText(fp)
                self.operaIni.addItem(AndroidColorResDialog.SECTION_ANDROID, AndroidColorResDialog.KEY_FIND_EXCEL_FN, fp)
                self.operaIni.saveIni()
                self.colorNameLineEdit.setEnabled(True)
                self.normalColorLineEdit.setEnabled(True)
                self.darkColorLineEdit.setEnabled(True)
                self.addColorResBtn.setEnabled(True)
        pass

    def initFindColorRes(self, fn):
        st = ExcelUtil.getSheet(fn, 0)
        if st:
            self.findColorRes = []
            lines = ExcelUtil.getLines(st)
            for i in range(1, lines):
                key = ExcelUtil.getCell(st, i, 0)
                if key:
                    colorRes = {'colorName': key}
                    normalColor = ExcelUtil.getCell(st, i, 1)
                    colorRes['normalColor'] = normalColor

                    darkColor = ExcelUtil.getCell(st, i, 2)
                    colorRes['darkColor'] = darkColor

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
            LogUtil.e("需要查找的color name：", colorName)
            for colorRes in self.findColorRes:
                if colorName in colorRes['colorName']:
                    res.append(colorRes)
        else:
            normalColor = self.normalColorLineEdit.text().strip().upper()
            darkColor = self.darkColorLineEdit.text().strip().upper()
            if normalColor:
                LogUtil.e("需要查找的normal color：", normalColor)
            if darkColor:
                LogUtil.e("需要查找的dark color：", darkColor)
            for colorRes in self.findColorRes:
                if normalColor in colorRes['normalColor'] and darkColor in colorRes['darkColor']:
                    res.append(colorRes)
            if not (normalColor or darkColor):
                LogUtil.e("没有查询条件，查询所有数据")
                res = self.findColorRes
        LogUtil.e("查找到的资源：", res)
        WidgetUtil.addTableViewData(self.findResTableView, res)
        pass

    def addColorRes(self):
        LogUtil.i("jumpAddColorResDialog")
        from widget.colorManager.AddColorResDialog import AddColorResDialog
        dialog = AddColorResDialog(self.addColorHandle, self.findColorRes)
        # dialog.show()
        pass

    def addColorHandle(self, colorName, normalColor, darkColor):
        LogUtil.e("新添加color资源：", colorName, "  ", normalColor, " dark: ", darkColor)
        fp = self.findExcelFnLineEdit.text().strip()
        oldBk = ExcelUtil.getBook(fp)
        nrows = oldBk.sheets()[0].nrows
        newBk: Workbook = ExcelUtil.copyBook(oldBk)
        st: Worksheet = newBk.get_sheet(0)
        st.write(nrows, 0, colorName)
        st.write(nrows, 1, normalColor)
        st.write(nrows, 2, darkColor)
        self.findColorRes.append({'colorName': colorName, 'normalColor': normalColor, 'darkColor': darkColor})
        newBk.save(fp)
        pass
