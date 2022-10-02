# PyQt5使用指导

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