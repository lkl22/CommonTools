# -*- coding: utf-8 -*-
# python 3.x
# Filename: RunMain.py
# 程序的主入口
import sys, os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from widget.MainWidget import *
from PyQt5.QtGui import QIcon

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainWidget = MainWidget()

    # 增加icon图标，如果没有图片可以没有这句
    mainWidget.setWindowIcon(QIcon('web.png'))
    mainWidget.show()
    sys.exit(app.exec_())
