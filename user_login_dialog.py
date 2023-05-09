# -*- coding: utf-8 -*-
import json

import requests
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
        self.user_name = None
        self.user_shop = None
        self.user_shop_id = None

    def login(self):
        """
        API 请求登录
        :return:
        """
        username = self.UserNameInput.text()
        password = self.PasswdInput.text()
        login_url = 'https://web.slpzb.com/rest/v1/account/jwtlogin/'
        headers = {
            'Content-Type': 'application/json'
        }
        post_data = json.dumps(
            {
                'username': username,
                'password': password
            }
        )
        response = requests.post(
            url=login_url,
            data=post_data,
            headers=headers
        ).json()
        if response.get('code') == 200 and response.get('data').get('id'):
            self.user_name = response.get('data').get('username')
            self.user_shop = response.get('data').get('prefix').get('name')
            self.user_shop_id = response.get('data').get('prefix').get('id')
            return True
        elif response['msg'] == '用户名或者密码错误':
            QMessageBox.warning(
                self, '错误', '用户名或密码错误！',
                QMessageBox.Yes, QMessageBox.Yes
            )
            self.UserNameInput.setFocus()
            self.PasswdInput.selectAll()
            return False
        else:
            QMessageBox.warning(
                self, '错误', '登录出错，请检查网络链接或联系管理员！',
                QMessageBox.Yes, QMessageBox.Yes
            )
            self.UserNameInput.setFocus()
            self.PasswdInput.selectAll()
            return False

    def login_event(self):
        login_result = self.login()

        if login_result:
            self.accept()
            return True
        else:
            # QMessageBox.warning(
            #     self, '错误', '用户名或密码错误！',
            #     QMessageBox.Yes, QMessageBox.Yes
            # )
            #
            # self.UserNameInput.setFocus()  # 将光标移动到用户名输入框
            # self.PasswdInput.selectAll()  # 将用户名输入框中的内容全选
            return False
