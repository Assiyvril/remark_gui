# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 15:58:00 2021
UI file: first_demo.ui
code file: first_demo.py
程序入口
"""

import sys
from PyQt5.QtWidgets import QApplication, QDialog
from new_gui import MainGui
import userlogin as login

if __name__ == "__main__":
    # 创建应用
    window_application = QApplication(sys.argv)
    # 设置登录窗口
    login_ui = login.UserNameLoginDialog()

    # 校验是否验证通过
    if login_ui.exec_() == QDialog.Accepted:

        # 初始化主功能窗口
        app = QApplication(sys.argv)
        mainWindow = MainGui()
        mainWindow.user_name = login_ui.user_name
        mainWindow.user_shop = login_ui.user_shop
        mainWindow.user_shop_id = login_ui.user_shop_id
        mainWindow.setupUi(mainWindow)
        # 登陆成功，修改主窗口的“当前用户” 和 “当前店铺” 的值
        mainWindow.CurrentUserLabel.setText("当前用户： " + mainWindow.user_name)
        mainWindow.CurrentStoreLabel.setText("当前店铺： " + mainWindow.user_shop)
        mainWindow.show()
        mainWindow.listen_clipboard()
        mainWindow.set_button()
        sys.exit(app.exec_())

    else:
        sys.exit(window_application.exec_())
