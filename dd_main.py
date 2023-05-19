import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QMessageBox, \
    QPushButton, QLineEdit, QRadioButton
from dd_login_scripts import DingLoginRequestInterceptor, QR_URL
from main_gui import MainGui

class ChoiceShopDialog(QDialog):
    """
    选择店铺的对话框
    若用户绑定了多个店铺，在此选择要进入的店铺
    """
    def __init__(self, shop_list, parent=None, default_shop_id=None):
        super().__init__(parent)
        self.setWindowTitle('选择店铺')
        self.shop_list = shop_list
        self.default_shop_id = int(default_shop_id)  # 默认选择的店铺ID
        self.button_choice_shop_id = None   # 通过按钮选择的店铺ID
        self.input_shop_id = None           # 通过输入框输入的店铺ID
        self.final_shop_id = None           # 最终选择的店铺ID
        self.final_shop_name = None         # 最终选择的店铺名称
        self.shop_id_input = QLineEdit()
        self.init_ui()

    def init_ui(self):
        """
        初始化界面
        :return:
        """
        layout = QVBoxLayout()
        for shop in self.shop_list:
            choice_button = QRadioButton('店铺ID：' + str(shop.get('id')) + '，店铺名称：' + shop.get('name'))
            choice_button.clicked.connect(self.deal_choice_shop)
            layout.addWidget(choice_button)
            if self.default_shop_id == int(shop.get('id')):
                choice_button.setChecked(True)
        # 保险起见，再加一个输入框，用户输入店铺ID
        # self.shop_id_input = QLineEdit()
        self.shop_id_input.setPlaceholderText('输入店铺ID')
        layout.addWidget(self.shop_id_input)
        # 确认按钮
        confirm_button = QPushButton('确认')
        confirm_button.clicked.connect(self.deal_input_shop_id)
        layout.addWidget(confirm_button)
        self.setLayout(layout)

    def deal_choice_shop(self):
        """
        通过按钮选择店铺
        :return:
        """
        sender = self.sender()
        self.button_choice_shop_id = sender.text().split('：')[1].split('，')[0]
        # 将按钮设置为被选择
        print('按钮选择的店铺ID：')
        print(self.button_choice_shop_id, type(self.button_choice_shop_id))
        print('按钮选择的店铺名称：')
        print(sender.text().split('：')[2])
        self.final_shop_name = sender.text().split('：')[2]

    def deal_input_shop_id(self):
        """
        通过输入框输入店铺ID
        :return:
        """

        self.input_shop_id = self.shop_id_input.text()
        print('输入框输入的店铺ID：')
        print(self.input_shop_id, type(self.input_shop_id))
        if not self.input_shop_id:
            QMessageBox.warning(
                self,
                '店铺ID错误',
                '请输入店铺ID',
            )
        if self.input_shop_id == self.button_choice_shop_id:
            self.final_shop_id = self.input_shop_id
            self.accept()
        else:
            QMessageBox.warning(
                self,
                '店铺ID错误, 选择的店铺ID与输入的店铺ID不一致',
                '请重新选择或输入店铺ID',
            )
            self.input_shop_id = None



class DDloginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('备注修改器-钉钉扫码登录')
        self.user_name = None
        self.user_shop = None
        self.user_shop_id = None
        self.choice_shop_dialog_obj = None
        self.webview = QWebEngineView()
        self.request_interceptor = DingLoginRequestInterceptor()

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

        self.webview.page().profile().setRequestInterceptor(
            self.request_interceptor
        )
        self.webview.page().setUrl(QUrl(QR_URL))
        self.request_interceptor.login_event.connect(
            self.deal_login_event
        )

    def deal_login_event(self, is_trigger):
        if is_trigger:
            login_obj = self.request_interceptor.ding_login_obj
            if not login_obj:
                # 弹出提示框，提示用户登录失败
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '软件发生内部错误，登录失败，请重试，或联系开发者',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            if not login_obj.have_response:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未收到服务器响应，请检查网络连接',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            if not login_obj.legal:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未查找到当前用户，请检查是否使用了正确的钉钉账号登录',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            if not login_obj.is_login:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '登录失败，请重试',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)

            self.user_name = login_obj.user_name
            # 判断用户是否绑定了多个店铺
            if login_obj.shop_list:
                # 弹出选择店铺的对话框
                self.choice_shop_dialog_obj = ChoiceShopDialog(login_obj.shop_list, default_shop_id=login_obj.user_shop_id)
                if self.choice_shop_dialog_obj.exec_() == QDialog.Accepted:
                    self.user_shop = self.choice_shop_dialog_obj.final_shop_name
                    self.user_shop_id = self.choice_shop_dialog_obj.final_shop_id
                    self.accept()
                    # sys.exit(0)
            else:

                self.user_shop = login_obj.user_shop
                self.user_shop_id = login_obj.user_shop_id
                self.accept()
                # sys.exit(0)


if __name__ == '__main__':
    window_application = QApplication(sys.argv)
    login_dialog = DDloginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        main_gui = MainGui()
        main_gui.setupUi(main_gui)
        main_gui.CurrentUserLabel.setText('当前用户: ' + login_dialog.user_name)
        main_gui.CurrentStoreLabel.setText('当前店铺: ' + login_dialog.user_shop)
        main_gui.user_name = login_dialog.user_name
        main_gui.user_shop = login_dialog.user_shop
        main_gui.user_shop_id = login_dialog.user_shop_id
        print('74 号')
        print('login_dialog.user_shop_id', login_dialog.user_shop_id)
        print('login_dialog.user_shop', login_dialog.user_shop)
        print('login_dialog.user_name', login_dialog.user_name)
        print('main_gui.user_name', main_gui.user_name)
        print('main_gui.user_shop', main_gui.user_shop)
        print('main_gui.user_shop_id', main_gui.user_shop_id)
        main_gui.statusbar.showMessage('登录成功, 开始监听剪贴板')
        main_gui.show()
        main_gui.listen_clipboard()
        main_gui.set_button()
        sys.exit(window_application.exec_())
    else:
        # 结束进程
        # sys.exit(window_application.exec_())
        sys.exit(0)

# if __name__ == '__main__':
#     shop_list = [
#         {'id': 1, 'name': '店铺1'},
#         {'id': 2, 'name': '店铺2'},
#         {'id': 3, 'name': '店铺3'},
#         {'id': 4, 'name': '店铺4'},
#         {'id': 5, 'name': '店铺5'},
#         {'id': 6, 'name': '店铺6'},
#     ]
#     window_application = QApplication(sys.argv)
#     choice_shop_dialog = ChoiceShopDialog(shop_list)
#     if choice_shop_dialog.exec_() == QDialog.Accepted:
#         print('choice_shop_dialog.shop_id_input', choice_shop_dialog.shop_id_input)
#         sys.exit(0)
#     else:
#         sys.exit(1)
