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
from jinja2 import Template

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

typeScriptTemplate = """Tasks:
export const enum Tasks {
{%- for index, task in enumerate(tasks) %}
  {{ camel2under(task) }} = "{{task}}"
  {%- if index != len(tasks) - 1 -%}
    ,
  {%- endif -%}
{%- endfor %}
}

Build tree:
export class DecisionTree {
  private buildTree() {
    let builder = new DecisionTreeBuilder<Tasks, TreeContext>();
    {%- for key, childNodes in tree.items() %}
    {%- if key != 'root' -%}
    {{"\n"}}    builder.
        {%- if key == root -%} 
    root(Tasks.{{ camel2under(key) }}, async (ctx?: TreeContext) => {
      return this.{{ key }}Action();
    }
        {%- else -%} 
          node(Tasks.{{ camel2under(key) }}) 
        {%- endif -%} 
        {%- for childNode in childNodes %}
            {%- if nodeInTree(childNode, tree) -%} 
                {{"\n"}}    .leaf 
            {%- else -%} 
                {{"\n"}}    .nonLeaf 
            {%- endif -%}
            (Tasks.{{ camel2under(childNode) }}, async (ctx?: TreeContext) => {
            {%- if nodeInTree(childNode, tree) -%} 
                {{"\n"}}      this.{childNode}Action();
            {%- else -%} 
                {{"\n"}}      return this.{childNode}Action();
            {%- endif -%}
          {{"\n"}}    })
        {%- endfor %}
        {{""}}
    {%- endif -%}
    {%- endfor %}
    this.tree = builder.build();
  }

  {%- for task in tasks %}

  async {{ task }}Action(){
  }
  {%- endfor %}
}
"""


def nodeInTree(node, tree):
    return node in tree


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
        root = self.__tree['root']
        tmpl = Template(typeScriptTemplate)
        tmpl.globals["camel2under"] = StrUtil.camel2under
        tmpl.globals["enumerate"] = enumerate
        tmpl.globals["len"] = len
        tmpl.globals["nodeInTree"] = nodeInTree
        ret = tmpl.render(tasks=self.__tasks, root=root, tree=self.__tree)
        self.__genCodeTextEdit.standardOutputOne(ret, ColorEnum.LIGHT_ORANGE.value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DecisionTreeCodeGenDialog(isDebug=True)
    window.show()
    sys.exit(app.exec_())