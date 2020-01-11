from PyQt5 import QtCore, QtGui, QtWidgets
from widget.MainWidget import *
import sys
from PyQt5.QtGui import QIcon
from constant.WidgetConst import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    mainWidget = MainWidget()
    print(const.PADDING)
    # 增加icon图标，如果没有图片可以没有这句
    mainWidget.setWindowIcon(QIcon('web.png'))
    mainWidget.show()
    sys.exit(app.exec_())
