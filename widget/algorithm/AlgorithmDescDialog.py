# -*- coding: utf-8 -*-
# python 3.x
# Filename: AlgorithmDescDialog.py
# 定义一个AlgorithmDescDialog类实现算法描述和代码实现功能
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexer, QsciLexerJavaScript, QsciLexerJava, QsciLexerCPP
from util.Uiautomator import *


class AlgorithmDescDialog(QtWidgets.QDialog):
    def __init__(self, title, descText, javaCode=None, javaScriptCode=None, pythonCode=None, cCode=None, cppCode=None,
                 swiftCode=None):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        AlgorithmDescDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.8)
        AlgorithmDescDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.8)
        LogUtil.d("Init Algorithm Visualizer Dialog")
        self.setObjectName("AlgorithmVisualizerDialog")
        self.resize(AlgorithmDescDialog.WINDOW_WIDTH, AlgorithmDescDialog.WINDOW_HEIGHT)
        # self.setFixedSize(AlgorithmDescDialog.WINDOW_WIDTH, AlgorithmDescDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text=title))

        vbox = WidgetUtil.createVBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        self.descText = descText
        self.javaCode = javaCode
        self.javaScriptCode = javaScriptCode
        self.pythonCode = pythonCode
        self.cCode = cCode
        self.cppCode = cppCode
        self.swiftCode = swiftCode

        descGroupBox = self.createDescGroupBox(self)
        vbox.addWidget(descGroupBox)

        codeGroupBox = self.createCodeGroupBox(self)
        vbox.addWidget(codeGroupBox)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        self.exec_()

    def createDescGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="算法描述")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        desc = WidgetUtil.createTextEdit(box, isReadOnly=True)
        desc.insertHtml(self.descText)
        vbox.addWidget(desc)
        return box

    def createCodeGroupBox(self, parent):
        box = WidgetUtil.createGroupBox(parent, title="代码实现")
        vbox = WidgetUtil.createVBoxLayout(box, margins=QMargins(10, 10, 10, 10), spacing=10)
        tabWidget = WidgetUtil.createTabWidget(box)
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
        vbox.addWidget(tabWidget)
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
