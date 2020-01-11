# -*- coding: utf-8 -*-
# python 3.x
# Filename: MainWidget.py
# 定义一个MainWidget类实现MainWindow主窗口的功能
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow


class MainWidget(QMainWindow):
    def __init__(self):
        # 调用父类的构函
        QMainWindow.__init__(self)
        self.setObjectName("Form")
        self.resize(552, 288)
        self.username = QtWidgets.QLabel(self)
        self.username.setGeometry(QtCore.QRect(90, 90, 48, 20))
        self.username.setObjectName("username")
        self.username_2 = QtWidgets.QLabel(self)
        self.username_2.setGeometry(QtCore.QRect(90, 130, 48, 20))
        self.username_2.setObjectName("username_2")
        self.layoutWidget = QtWidgets.QWidget(self)
        self.layoutWidget.setGeometry(QtCore.QRect(140, 130, 189, 22))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.layoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.radioButton = QtWidgets.QRadioButton(self)
        self.radioButton.setGeometry(QtCore.QRect(150, 180, 131, 16))
        self.radioButton.setObjectName("radioButton")
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(180, 220, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.widget = QtWidgets.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(140, 90, 189, 22))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.username.setText(_translate("Form", "用户名："))
        self.username_2.setText(_translate("Form", "密码："))
        self.radioButton.setText(_translate("Form", "记住用户名和密码"))
        self.pushButton_2.setText(_translate("Form", "登录"))