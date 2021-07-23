# -*- coding: utf-8 -*-
# python 3.x
# Filename: AlgorithmDescDialog.py
# 定义一个AlgorithmDescDialog类实现算法描述和代码实现功能
from PyQt5 import QtPrintSupport
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexer, QsciLexerJavaScript, QsciLexerJava, QsciLexerCPP
from constant.WidgetConst import *
from util.Uiautomator import *


class AlgorithmDescDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    DESC_GROUP_BOX_HEIGHT = 200

    def __init__(self, title, descText, javaCode=None, javaScriptCode=None, pythonCode=None, cCode=None, cppCode=None, swiftCode=None):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Algorithm Visualizer Dialog")
        self.setObjectName("AlgorithmVisualizerDialog")
        self.resize(AlgorithmDescDialog.WINDOW_WIDTH, AlgorithmDescDialog.WINDOW_HEIGHT)
        self.setFixedSize(AlgorithmDescDialog.WINDOW_WIDTH, AlgorithmDescDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text=title))

        width = AlgorithmDescDialog.WINDOW_WIDTH - const.PADDING * 2

        vbox = WidgetUtil.createVBoxLayout()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       int(AlgorithmDescDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2)))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)

        self.descText = descText
        self.javaCode = javaCode
        self.javaScriptCode = javaScriptCode
        self.pythonCode = pythonCode
        self.cCode = cCode
        self.cppCode = cppCode
        self.swiftCode = swiftCode

        descGroupBox = self.createDescGroupBox(layoutWidget)
        vbox.addWidget(descGroupBox)

        sizePolicy = WidgetUtil.createSizePolicy()
        codeGroupBox = self.createCodeGroupBox(layoutWidget)
        codeGroupBox.setSizePolicy(sizePolicy)
        vbox.addWidget(codeGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createDescGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AlgorithmDescDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="算法描述",
                                        minSize=QSize(width, AlgorithmDescDialog.DESC_GROUP_BOX_HEIGHT))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.PADDING * 2,
                                                                 AlgorithmDescDialog.DESC_GROUP_BOX_HEIGHT - const.PADDING * 4))

        desc = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        desc.insertHtml(self.descText)
        return box

    def createCodeGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = AlgorithmDescDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="代码实现",
                                        minSize=QSize(width, AlgorithmDescDialog.DESC_GROUP_BOX_HEIGHT))

        # sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.PADDING * 2, 330))

        tabWidget = WidgetUtil.createTabWidget(splitter)
        if self.javaCode:
            tabWidget.addTab(self.createTabWidget(self.javaCode, QsciLexerJava()), "Java")
        if self.javaScriptCode:
            tabWidget.addTab(self.createTabWidget(self.javaScriptCode, QsciLexerJavaScript()), "JavaScript")
        if self.pythonCode:
            tabWidget.addTab(self.createTabWidget(self.pythonCode, QsciLexerPython()), "Python")
        if self.cCode:
            tabWidget.addTab(self.createTabWidget(self.cCode, QsciLexerCPP()), "C")
        if self.cppCode:
            tabWidget.addTab(self.createTabWidget(self.cppCode, QsciLexerCPP()), "C++")
        if self.swiftCode:
            tabWidget.addTab(self.createTabWidget(self.swiftCode, QsciLexerCPP()), "Swift")

        return box

    def createTabWidget(self, code, textLexer: QsciLexer):
        tabWidget = QWidget()
        # 垂直布局
        layout = WidgetUtil.createVBoxLayout()
        # 设置布局方式
        tabWidget.setLayout(layout)

        editor = QsciScintilla(tabWidget)
        editor.setLexer(textLexer)

        # 行号提示
        editor.setMarginType(0, QsciScintilla.NumberMargin)  # 设置编号为1的页边显示行号。
        editor.setMarginLineNumbers(0, True)  # 对该页边启用行号
        editor.setMarginWidth(0, 30)  # 设置页边宽度
        editor.setText(code)
        editor.SendScintilla(QsciScintilla.SCI_SETCODEPAGE, QsciScintilla.SC_CP_UTF8)  # 设置编码为UTF-8

        editor.setReadOnly(True)

        # 添加控件到布局中
        layout.addWidget(editor)
        return tabWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AlgorithmDescDialog()
    window.show()
    sys.exit(app.exec_())
