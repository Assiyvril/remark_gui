# -*- coding: utf-8 -*-
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QDialog, QMessageBox

from user_login_ui import Ui_UserNameLogin


class UserNameLoginDialog(QDialog, Ui_UserNameLogin):
    """
    用户名密码登录对话框，
    使用 Qt Designer 设计，
    继承自 Ui_UserNameLogin，实现显示与逻辑分离
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)
        self.LoginBotton.clicked.connect(self.login_event)
        self.QuitBotton.clicked.connect(QCoreApplication.instance().quit)

    def login_event(self):
        username = self.UserNameInput.text()
        password = self.PasswdInput.text()

        if username == 'admin' and password == 'hello':
            # 临时测试逻辑 后续需要适配 登录 API TODO
            self.accept()
            return True
        else:
            QMessageBox.warning(
                self, '错误', '用户名或密码错误！',
                QMessageBox.Yes, QMessageBox.Yes
            )

            self.UserNameInput.setFocus()  # 将光标移动到用户名输入框
            self.PasswdInput.selectAll()  # 将用户名输入框中的内容全选
            return False
