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

RES_TYPE_LIST = ['无', 'string', 'color', 'style', 'dimen', 'plurals', 'declare-styleable', 'array', 'string-array',
                 'integer-array', 'attr']


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
        self.findNormalColorRes = {}
        self.findDarkColorRes = {}

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

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createGenerateExcelGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="生成Excel")
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AndroidColorResDialog.WINDOW_WIDTH - const.PADDING * 4
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
        box = WidgetUtil.createGroupBox(parent, title="查找资源")
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
        self.colorNameLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy, textChanged=self.colorNameTextChange)

        WidgetUtil.createLabel(splitter, text="normal color", alignment=Qt.AlignVCenter | Qt.AlignRight, minSize=QSize(120, const.HEIGHT))
        self.normalColorLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy, textChanged=self.normalColorTextChange)

        WidgetUtil.createLabel(splitter, text="dark color", alignment=Qt.AlignVCenter | Qt.AlignRight, minSize=QSize(120, const.HEIGHT))
        self.darkColorLineEdit = WidgetUtil.createLineEdit(splitter, sizePolicy=sizePolicy, textChanged=self.darkColorTextChange)

        yPos += const.HEIGHT_OFFSET
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 50, const.HEIGHT))
        WidgetUtil.createPushButton(splitter, text="查找", onClicked=self.findRes)

        yPos += const.HEIGHT_OFFSET

        return box

    def getExcelFile(self):
        fp = WidgetUtil.getOpenFileName(caption='选择color资源汇总Excel文件', filter='*.xls', initialFilter='*.xls')
        if fp:
            res = self.initFindColorRes(fp)
            if res:
                self.findExcelFnLineEdit.setText(fp)
                self.operaIni.addItem(AndroidColorResDialog.SECTION_ANDROID, AndroidColorResDialog.KEY_FIND_EXCEL_FN, fp)
                self.operaIni.saveIni()
        pass

    def initFindColorRes(self, fn):
        st = ExcelUtil.getSheet(fn, 0)
        if st:
            self.findNormalColorRes = {}
            self.findDarkColorRes = {}
            lines = ExcelUtil.getLines(st)
            for i in range(1, lines):
                key = ExcelUtil.getCell(st, i, 0)
                if key:
                    normalColor = ExcelUtil.getCell(st, i, 1)
                    if normalColor:
                        self.findNormalColorRes[key] = normalColor

                    darkColor = ExcelUtil.getCell(st, i, 2)
                    if darkColor:
                        self.findDarkColorRes[key] = darkColor
            if self.findNormalColorRes or self.findDarkColorRes:
                print(self.findNormalColorRes)
                print(self.findDarkColorRes)
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
        if colorName:
            LogUtil.e("需要查找的color name：", colorName)
        else:
            normalColor = self.normalColorLineEdit.text().strip()
            darkColor = self.darkColorLineEdit.text().strip()
            if normalColor:
                LogUtil.e("需要查找的normal color：", normalColor)
            if darkColor:
                LogUtil.e("需要查找的dark color：", darkColor)
            if not (normalColor or darkColor):
                LogUtil.e("没有查询条件，查询所有数据")
        pass
