# -*- coding: utf-8 -*-
# python 3.x
# Filename: MockExamDialog.py
# 定义一个MockExamDialog类实现考试刷题
from PyQt5.QtCore import QModelIndex

from constant.WidgetConst import *
from util.ExcelUtil import *
from util.DialogUtil import *
from util.DomXmlUtil import *
from util.LogUtil import *
from util.OperaIni import *


class MockExamDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 670

    KEY_FIND_EXCEL_FN = "findExcelFn"
    SECTION_ANDROID = "android"

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Mock Exam Dialog")
        self.setObjectName("MockExamDialog")
        self.resize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)
        self.setFixedSize(MockExamDialog.WINDOW_WIDTH, MockExamDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="模拟考试"))

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(
            QRect(const.PADDING, const.PADDING, MockExamDialog.WINDOW_WIDTH - const.PADDING * 2,
                  MockExamDialog.WINDOW_HEIGHT - const.PADDING * 2))
        layoutWidget.setObjectName("layoutWidget")

        vLayout = WidgetUtil.createVBoxLayout(margins=QMargins(0, 0, 0, 0))
        layoutWidget.setLayout(vLayout)

        generateExcelGroupBox = self.createGenerateExcelGroupBox(layoutWidget)
        vLayout.addWidget(generateExcelGroupBox)

        # self.operaIni = OperaIni()、、、、、
        #
        # LogUtil.d(FileUtil.getProjectPath())
        #
        # findExcelFn = self.operaIni.getValue(MockExamDialog.KEY_FIND_EXCEL_FN,
        #                                      MockExamDialog.SECTION_ANDROID)
        # if findExcelFn:
        #     if self.initFindColorRes(findExcelFn):
        #         self.findExcelFnLineEdit.setText(findExcelFn)
        #         self.colorNameLineEdit.setEnabled(True)
        #         self.normalColorLineEdit.setEnabled(True)
        #         self.darkColorLineEdit.setEnabled(True)
        #         self.findColorResBtn.setEnabled(True)
        #         self.addColorResBtn.setEnabled(True)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createGenerateExcelGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = MockExamDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="生成考试信息",
                                        minSize=QSize(width, const.GROUP_BOX_MARGIN_TOP + const.HEIGHT_OFFSET * 9 / 2))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))

        # WidgetUtil.createPushButton(splitter, text="normal color res XML文件路径", minSize=QSize(120, const.HEIGHT),
        #                             onClicked=self.getSrcFilePath)
        # sizePolicy = WidgetUtil.createSizePolicy()
        # self.srcFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        #
        # yPos += const.HEIGHT_OFFSET
        # splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        # WidgetUtil.createPushButton(splitter, text="dark color res XML文件路径", onClicked=self.getDstFilePath)
        # self.dstFilePathLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        #
        # yPos += const.HEIGHT_OFFSET
        # splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width, const.HEIGHT))
        # WidgetUtil.createPushButton(splitter, text="生成Excel文件路径", onClicked=self.getGenerateExcelFilePath)
        # self.generateExcelLineEdit = WidgetUtil.createLineEdit(splitter, isEnable=False, sizePolicy=sizePolicy)
        #
        # yPos += const.HEIGHT_OFFSET
        # splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, 100, const.HEIGHT))
        # WidgetUtil.createPushButton(splitter, text="生成Excel", onClicked=self.generateExcel)
        return box


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MockExamDialog()
    window.show()
    sys.exit(app.exec_())
