# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\first_demo.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1130, 889)
        icon = QtGui.QIcon.fromTheme("主题")
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.PageViewLabel = QtWidgets.QLabel(self.centralwidget)
        self.PageViewLabel.setGeometry(QtCore.QRect(400, 10, 111, 21))
        self.PageViewLabel.setTextFormat(QtCore.Qt.AutoText)
        self.PageViewLabel.setObjectName("PageViewLabel")
        self.lineEditCanBeDeleted = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditCanBeDeleted.setGeometry(QtCore.QRect(20, 60, 251, 31))
        self.lineEditCanBeDeleted.setObjectName("lineEditCanBeDeleted")
        self.DeleteButtun = QtWidgets.QPushButton(self.centralwidget)
        self.DeleteButtun.setGeometry(QtCore.QRect(40, 110, 151, 71))
        self.DeleteButtun.setObjectName("DeleteButtun")
        self.RateConversionExchangerLabel = QtWidgets.QLabel(
            self.centralwidget)
        self.RateConversionExchangerLabel.setGeometry(
            QtCore.QRect(570, 60, 151, 16))
        self.RateConversionExchangerLabel.setObjectName(
            "RateConversionExchangerLabel")
        self.EURLabel = QtWidgets.QLabel(self.centralwidget)
        self.EURLabel.setGeometry(QtCore.QRect(530, 110, 31, 31))
        self.EURLabel.setObjectName("EURLabel")
        self.RMBLabel = QtWidgets.QLabel(self.centralwidget)
        self.RMBLabel.setGeometry(QtCore.QRect(750, 120, 41, 16))
        self.RMBLabel.setObjectName("RMBLabel")
        self.ExchangerButton = QtWidgets.QPushButton(self.centralwidget)
        self.ExchangerButton.setGeometry(QtCore.QRect(630, 140, 41, 41))
        self.ExchangerButton.setObjectName("ExchangerButton")
        self.EURInput = QtWidgets.QLineEdit(self.centralwidget)
        self.EURInput.setGeometry(QtCore.QRect(490, 150, 113, 20))
        self.EURInput.setObjectName("EURInput")
        self.RMBInput = QtWidgets.QLineEdit(self.centralwidget)
        self.RMBInput.setGeometry(QtCore.QRect(720, 150, 113, 20))
        self.RMBInput.setObjectName("RMBInput")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1130, 23))
        self.menubar.setObjectName("menubar")
        self.menu_A = QtWidgets.QMenu(self.menubar)
        self.menu_A.setObjectName("menu_A")
        self.menu_B = QtWidgets.QMenu(self.menubar)
        self.menu_B.setObjectName("menu_B")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menu_A.addSeparator()
        self.menubar.addAction(self.menu_A.menuAction())
        self.menubar.addAction(self.menu_B.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "汇率转换器"))
        self.PageViewLabel.setText(
            _translate("MainWindow", "这是一个练习 Demo"))
        self.lineEditCanBeDeleted.setText(
            _translate("MainWindow", "测试输入框 A，可被删除"))
        self.DeleteButtun.setText(_translate("MainWindow", "测试按钮 A，\n"
                                                           "按此删除输入框A的内容"))

        # 建立信号连接，按钮被按下时，清空输入框内容
        # widget.signal.connect(slot_function)
        self.DeleteButtun.clicked.connect(
            self.lineEditCanBeDeleted.clear
        )
        self.RateConversionExchangerLabel.setText(
            _translate("MainWindow", "汇率转换器 欧元 -> RMB"))
        self.EURLabel.setText(_translate("MainWindow", "欧元"))
        self.RMBLabel.setText(_translate("MainWindow", "人民币"))
        self.ExchangerButton.setText(_translate("MainWindow", "转换\n"
                                                              "汇率"))
        self.EURInput.setText(_translate("MainWindow", "输入欧元金额"))
        self.RMBInput.setText(_translate("MainWindow", "输入人民币金额"))

        # 建立信号连接，按钮被按下时，执行汇率转换函数
        self.ExchangerButton.clicked.connect(
            self.exchange_rate
        )

        self.menu_A.setTitle(_translate("MainWindow", "一级菜单 A"))
        self.menu_B.setTitle(_translate("MainWindow", "一级菜单B"))

    def exchange_rate(self):
        """
        汇率转换函数
        """
        # 从输入框中获取欧元金额
        eur_str = self.EURInput.text()
        if eur_str == '输入欧元金额':
            eur_str = None

        rmb_str = self.RMBInput.text()
        if rmb_str == '输入人民币金额':
            rmb_str = None

        # 如果欧元金额和人民币金额都为空，则不执行转换
        if eur_str is None and rmb_str is None:
            return None

        # 如果欧元金额不为空，则执行欧元转人民币
        if eur_str is not None:
            try:
                eur = float(eur_str)
            except ValueError:
                print('输入的欧元金额不是数字')
                return None
            rmb = eur * 7.8
            self.RMBInput.setText(str(rmb))

        # 如果人民币金额不为空，则执行人民币转欧元
        if rmb_str is not None:
            try:
                rmb = float(rmb_str)
            except ValueError:
                print('输入的人民币金额不是数字')
                return None
            eur = rmb / 7.8
            self.EURInput.setText(str(eur))

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
