# -*- coding: utf-8 -*-
# python 3.x
# Filename: SelectionSortDescDialog.py
# 定义一个SelectionSortDescDialog类实现选择排序算法描述
from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexer, QsciLexerJavaScript, QsciLexerJava
from PyQt5.QtCore import QRectF, QPointF
from PyQt5.QtGui import QSyntaxHighlighter, QTextDocument

from constant.ColorConst import ColorConst
from util.AutoTestUtil import *
from util.GraphicsUtil import GraphicsUtil
from constant.WidgetConst import *
from util.Uiautomator import *
from widget.syntaxHighlighter.PythonHighlighter import PythonHighlighter


class SelectionSortDescDialog(QtWidgets.QDialog):
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    DESC_GROUP_BOX_HEIGHT = 200

    def __init__(self):
        # 调用父类的构函
        QtWidgets.QDialog.__init__(self)
        LogUtil.d("Init Algorithm Visualizer Dialog")
        self.setObjectName("AlgorithmVisualizerDialog")
        self.resize(SelectionSortDescDialog.WINDOW_WIDTH, SelectionSortDescDialog.WINDOW_HEIGHT)
        self.setFixedSize(SelectionSortDescDialog.WINDOW_WIDTH, SelectionSortDescDialog.WINDOW_HEIGHT)
        self.setWindowTitle(WidgetUtil.translate(text="选择排序算法描述"))

        width = SelectionSortDescDialog.WINDOW_WIDTH - const.PADDING * 2

        vbox = WidgetUtil.createVBoxLayout()

        layoutWidget = QtWidgets.QWidget(self)
        layoutWidget.setGeometry(QRect(const.PADDING, const.PADDING, width,
                                       int(SelectionSortDescDialog.WINDOW_HEIGHT - const.PADDING * 3 / 2)))
        layoutWidget.setObjectName("layoutWidget")
        layoutWidget.setLayout(vbox)

        descGroupBox = self.createDescGroupBox(layoutWidget)
        vbox.addWidget(descGroupBox)

        sizePolicy = WidgetUtil.createSizePolicy()
        codeGroupBox = self.createCodeGroupBox(layoutWidget)
        codeGroupBox.setSizePolicy(sizePolicy)
        vbox.addWidget(codeGroupBox)

        # splitter = WidgetUtil.createSplitter(self, geometry=QRect(const.PADDING, const.PADDING, width, const.HEIGHT))
        # splitter.setSizePolicy(sizePolicy)
        # vbox.addWidget(splitter)

        self.setWindowModality(Qt.ApplicationModal)
        # 很关键，不加出不来
        # self.exec_()

    def createDescGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = SelectionSortDescDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="算法描述",
                                        minSize=QSize(width, SelectionSortDescDialog.DESC_GROUP_BOX_HEIGHT))

        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.PADDING * 2,
                                                                 SelectionSortDescDialog.DESC_GROUP_BOX_HEIGHT - const.PADDING * 4))

        desc = WidgetUtil.createTextEdit(splitter, isReadOnly=True)
        desc.insertHtml(r'''选择排序是一种简单直观的排序算法，无论什么数据进去都是 O(n²) 的时间复杂度。所以用到它的时候，数据规模越小越好。唯一的好处可能就是不占用额外的内存空间了吧。
<h3>算法步骤</h3>
首先在未排序序列中找到最小（大）元素，存放到排序序列的起始位置。<br>
再从剩余未排序元素中继续寻找最小（大）元素，然后放到已排序序列的末尾。<br>
重复第二步，直到所有元素均排序完毕。''')
        return box

    def createCodeGroupBox(self, parent):
        yPos = const.GROUP_BOX_MARGIN_TOP
        width = SelectionSortDescDialog.WINDOW_WIDTH - const.PADDING * 4

        box = WidgetUtil.createGroupBox(parent, title="代码实现",
                                        minSize=QSize(width, SelectionSortDescDialog.DESC_GROUP_BOX_HEIGHT))

        sizePolicy = WidgetUtil.createSizePolicy()
        splitter = WidgetUtil.createSplitter(box, geometry=QRect(const.PADDING, yPos, width - const.PADDING * 2, 330))

        tabWidget = WidgetUtil.createTabWidget(splitter)
        tabWidget.addTab(self.createTabWidget(self.getJavaCode(), QsciLexerJava()), "Java")
        tabWidget.addTab(self.createTabWidget(self.getJavaScriptCode(), QsciLexerJavaScript()), "JavaScript")
        tabWidget.addTab(self.createTabWidget(self.getPythonCode(), QsciLexerPython()), "Python")

        return box

    def createTabWidget(self, code, textLexer):
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

        editor.setReadOnly(True)

        # 添加控件到布局中
        layout.addWidget(editor)
        return tabWidget

    def getPythonCode(self):
        return r'''def selectionSort(arr):
    for i in range(len(arr) - 1):
        # 记录最小数的索引
        minIndex = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[minIndex]:
                minIndex = j
        # i 不是最小数时，将 i 和最小数进行交换
        if i != minIndex:
            arr[i], arr[minIndex] = arr[minIndex], arr[i]
    return arr'''

    def getJavaCode(self):
        return r'''```Java
public class SelectionSort implements IArraySort {

    @Override
    public int[] sort(int[] sourceArray) throws Exception {
        int[] arr = Arrays.copyOf(sourceArray, sourceArray.length);

        // 总共要经过 N-1 轮比较
        for (int i = 0; i < arr.length - 1; i++) {
            int min = i;

            // 每轮需要比较的次数 N-i
            for (int j = i + 1; j < arr.length; j++) {
                if (arr[j] < arr[min]) {
                    // 记录目前能找到的最小值元素的下标
                    min = j;
                }
            }

            // 将找到的最小值和i位置所在的值进行交换
            if (i != min) {
                int tmp = arr[i];
                arr[i] = arr[min];
                arr[min] = tmp;
            }

        }
        return arr;
    }
}
```'''

    def getJavaScriptCode(self):
        return r'''function selectionSort(arr) {
    var len = arr.length;
    var minIndex, temp;
    for (var i = 0; i < len - 1; i++) {
        minIndex = i;
        for (var j = i + 1; j < len; j++) {
            if (arr[j] < arr[minIndex]) {     // 寻找最小的数
                minIndex = j;                 // 将最小数的索引保存
            }
        }
        temp = arr[i];
        arr[i] = arr[minIndex];
        arr[minIndex] = temp;
    }
    return arr;
}'''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionSortDescDialog()
    window.show()
    sys.exit(app.exec_())
