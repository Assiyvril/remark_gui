# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLineEdit, QPushButton, \
    QDialog, QMessageBox


class LoginDialog(QDialog):
    def __init__(self, *args, **kwargs):
        '''
        构造函数，初始化登录对话框的内容
        :param args:
        :param kwargs:
        '''
        super().__init__(*args, **kwargs)
        self.setWindowTitle('欢迎登录')  # 设置标题
        self.resize(200, 200)  # 设置宽、高
        self.setFixedSize(self.width(), self.height())

        '''
        定义界面控件设置
        '''
        self.frame = QFrame(self)  # 初始化 Frame对象
        self.verticalLayout = QVBoxLayout(self.frame)  # 设置横向布局
        self.verticalLayout

        self.login_id = QLineEdit()  # 定义用户名输入框
        self.login_id.setPlaceholderText("请输入登录账号")  # 设置默认显示的提示语
        self.verticalLayout.addWidget(self.login_id)  # 将该登录账户设置添加到页面控件

        self.passwd = QLineEdit()  # 定义密码输入框
        self.passwd.setPlaceholderText("请输入登录密码")  # 设置默认显示的提示语
        self.verticalLayout.addWidget(self.passwd)  # 将该登录密码设置添加到页面控件

        self.button_enter = QPushButton()  # 定义登录按钮
        self.button_enter.setText("登录")  # 按钮显示值为登录
        self.verticalLayout.addWidget(self.button_enter)  # 将按钮添加到页面控件

        self.button_quit = QPushButton()  # 定义返回按钮
        self.button_quit.setText("返回")  # 按钮显示值为返回
        self.verticalLayout.addWidget(self.button_quit)  # 将按钮添加到页面控件

        # 绑定按钮事件
        self.button_enter.clicked.connect(self.button_enter_verify)
        self.button_quit.clicked.connect(
            QCoreApplication.instance().quit
        )  # 返回按钮绑定到退出

    def button_enter_verify(self):
        # 校验账号是否正确
        username = self.login_id.text()
        password = self.passwd.text()

        if username == 'admin' and password == 'hello':
            self.accept()
        else:
            """
            登陆失败，弹出提示框
            """
            QMessageBox.warning(
                self, "警告", "用户名或密码错误！", QMessageBox.Yes
            )
            self.login_id.setFocus()  # 将光标移动到用户名输入框
            self.login_id.selectAll()  # 将用户名输入框中的内容全选
            return False


