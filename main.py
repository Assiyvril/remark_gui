# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 15:58:00 2021
UI file: first_demo.ui
code file: first_demo.py
程序入口
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from gui import Ui_mainWindow
import login

if __name__ == "__main__":
    # 创建应用
    window_application = QApplication(sys.argv)
    # 设置登录窗口
    login_ui = login.LoginDialog()


    # 校验是否验证通过
    if login_ui.exec_() == QDialog.Accepted:
        username = login_ui.login_id.text()
        print('username', username)
        # 初始化主功能窗口
        app = QApplication(sys.argv)
        mainWindow = QMainWindow()
        ui = Ui_mainWindow()
        # 登陆成功，修改主窗口的“当前用户” 和 “当前店铺” 的值
        ui.setupUi(mainWindow)
        ui.CurrentUserLabel.setText("当前用户： " + username)
        mainWindow.show()
        sys.exit(app.exec_())
    else:
        sys.exit(window_application.exec_())
