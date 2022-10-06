# PyQt5使用指导

## 窗口置顶

> .setWindowFlags(Qt.WindowStaysOnTopHint)

## QWidget

### 设置hover时背景色

> .setStyleSheet("QWidget:hover{background-color:rgb(0,255,255)}")

### 鼠标点击事件

```python
def mousePressEvent(self, ev: QMouseEvent):
    super.mousePressEvent(ev)
    LogUtil.d('mousePressEvent')
    if ev.button() == Qt.RightButton:
```

## QFrame

相关API|	含义|	参数
---|---|---
setLineWidth(int width)|	设置外线宽度|	整型
midLineWidth()|	设置中线宽度|	整型
setFrameShape(QFrame.Shape)|	设置边框形状|	QFrame.Shape 枚举值
setFrameShadow(QFrame.Shadow)|	设置边框阴影|	QFrame.Shadow 枚举值
setFrameStyle(int style)|	设置边框样式|	枚举值
setFrameRect(QRect)|	设置边框矩形|	整型

[pyQt5 学习笔记（19）QFrame 边框设置](https://blog.csdn.net/qq_17351161/article/details/102987451)

### 设置边框

> .setStyleSheet("ObjectName{border:1px solid rgb(0,255,255)}")

* ObjectName是对象名

## QLineEdit

### 设置背景色

> .setStyleSheet("QLineEdit{ background:rgb(0,255,0);}")

### 输入密码

则你可以使用下面三种方式定义输入的显示模式。
其中

* Normal表示正常输入
* PassWord表示显示为圆点
* PassWordEchoEdit表示输入时显示字符，光标挪开时，显示圆点密码形式

```python
.setEchoMode(QtWidgets.QLineEdit.Normal)
.setEchoMode(QtWidgets.QLineEdit.Password)
.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
```

## QTextEdit

### 去除外框

> .setStyleSheet("border: none;")
