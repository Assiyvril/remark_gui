# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 15:58:00 2021
UI file: first_demo.ui
code file: first_demo.py
程序入口
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import first_demo

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = first_demo.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(
        app.exec_()
    )
