# -*- coding: utf-8 -*-
# python 3.x
# Filename: DecisionTreeCodeGenDialog.py
# 定义一个DecisionTreeCodeGenDialog类实现通过uml图生成模版代码的功能
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QApplication

from constant.ColorEnum import ColorEnum
from util.LogUtil import LogUtil
from util.OperaIni import OperaIni
from util.StrUtil import StrUtil
from util.WidgetUtil import WidgetUtil
from widget.custom.CommonTextEdit import CommonTextEdit

TAG = 'DecisionTreeCodeGenDialog'

uml = """
@startuml
hide empty description
state A #green
state B #green
state C #green
state D #green
state FAILED #green
[*] --> init
init --> check
check --> C
C --> D
D --> E
D --> Failed
C --> Failed
check --> Failed
init --> Failed
@enduml
"""

class DecisionTreeCodeGenDialog(QtWidgets.QDialog):
    def __init__(self, isDebug=False):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(Qt.Dialog | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        DecisionTreeCodeGenDialog.WINDOW_WIDTH = int(WidgetUtil.getScreenWidth() * 0.7)
        DecisionTreeCodeGenDialog.WINDOW_HEIGHT = int(WidgetUtil.getScreenHeight() * 0.6)
        LogUtil.d(TAG, "Init Harmony Merge Res Dialog")
        self.setObjectName("DecisionTreeCodeGenDialog")
        self.resize(DecisionTreeCodeGenDialog.WINDOW_WIDTH, DecisionTreeCodeGenDialog.WINDOW_HEIGHT)
        # self.setFixedSize(DecisionTreeCodeGenDialog.WINDOW_WIDTH, DecisionTreeCodeGenDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="Harmony 合并资源文件处理"))

        self.__isDebug = isDebug
        self.__operaIni = OperaIni()
        self.__tasks = []
        self.__tree = {}

        dialogLayout = WidgetUtil.createHBoxLayout(self, margins=QMargins(10, 10, 10, 10), spacing=10)

        self.__umlCodeTextEdit = CommonTextEdit(title='请输入UML代码：', text=uml, isReadOnly=False, isShowCopyFunc=False)
        dialogLayout.addWidget(self.__umlCodeTextEdit, 2)

        self.__genTsCodeBtn = WidgetUtil.createPushButton(self, text='生成TypeScript Code', onClicked=self.__genTsCodeEvent)
        dialogLayout.addWidget(self.__genTsCodeBtn)

        self.__genCodeTextEdit = CommonTextEdit(title='生成代码：')
        dialogLayout.addWidget(self.__genCodeTextEdit, 3)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        if not isDebug:
            self.exec_()

    def __genTsCodeEvent(self):
        umlCode = self.__umlCodeTextEdit.getData()
        if not umlCode:
            WidgetUtil.showErrorDialog(message='请输入UML代码')
            return
        self.__genCodeTextEdit.clear()
        self.__parseUmlCode(umlCode)
        self.__genTsCode()
        pass

    def __parseUmlCode(self, umlCode):
        lines = umlCode.split('\n')
        nodeLines = [item for item in lines if '-->' in item]
        LogUtil.d(TAG, nodeLines)
        tree = {}
        tasks = []
        for item in nodeLines:
            nodes = item.split('-->')
            if '[*]' in nodes[0]:
                tree['root'] = StrUtil.under2camel(nodes[1].strip())
                tasks.append(tree['root'])
            else:
                parentNode = StrUtil.under2camel(nodes[0].strip())
                childNode = StrUtil.under2camel(nodes[1].strip())
                if parentNode not in tasks:
                    tasks.append(parentNode)
                if childNode not in tasks:
                    tasks.append(childNode)
                if parentNode in tree:
                    tree[parentNode].append(childNode)
                else:
                    tree[parentNode] = []
                    tree[parentNode].append(childNode)
        LogUtil.d(TAG, tasks, tree)
        self.__tasks = tasks
        self.__tree = tree

    def __genTsCode(self):
        taskEnum = ''
        for index, task in enumerate(self.__tasks):
            sp = "" if index == 0 else ",\n"
            taskEnum += f'{sp}  {StrUtil.camel2under(task)} = "{task}"'
        self.__genCodeTextEdit.standardOutputOne('Tasks:', ColorEnum.Red.value)
        self.__genCodeTextEdit.standardOutputOne("export const enum Tasks {\n" + taskEnum + "\n}", ColorEnum.Blue.value)

        self.__genCodeTextEdit.standardOutputOne('Build tree:', ColorEnum.Red.value)
        self.__genCodeTextEdit.standardOutputOne('  private buildTree() {\n    let builder = new DecisionTreeBuilder<Tasks, TreeContext>();', ColorEnum.Blue.value)

        root = self.__tree['root']
        for key, childNodes in self.__tree.items():
            if key == 'root':
                continue
            self.__genCodeTextEdit.standardOutputOne(
                f'    builder.{"root" if key == root else "node"}(Tasks.{StrUtil.camel2under(key)}, async (ctx?: TreeContext) => {{\n      return this.{key}Action();\n    }}', ColorEnum.Blue.value)
            for childNode in childNodes:
                isLeaf = False if childNode in self.__tree else True
                funcContent = f"this.{childNode}Action();" if isLeaf else f"return this.{childNode}Action();"
                self.__genCodeTextEdit.standardOutputOne(
                    f'    {".leaf" if isLeaf else ".nonLeaf"}(Tasks.{StrUtil.camel2under(childNode)}, async (ctx?: TreeContext) => {{\n      {funcContent}\n    }}', ColorEnum.Blue.value)
            self.__genCodeTextEdit.standardOutputOne('', ColorEnum.Blue.value)
        self.__genCodeTextEdit.standardOutputOne('    this.tree = builder.build();\n  }', ColorEnum.Blue.value)

        for task in self.__tasks:
            self.__genCodeTextEdit.standardOutputOne(f'\n  async {task}Action(){{\n  }}', ColorEnum.Blue.value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DecisionTreeCodeGenDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())