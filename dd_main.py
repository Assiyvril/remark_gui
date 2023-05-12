import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QMessageBox
from dd_login_scripts import DingLoginRequestInterceptor, QR_URL
from main_gui import MainGui


class DDloginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('备注修改器-钉钉扫码登录')
        self.user_name = None
        self.user_shop = None
        self.user_shop_id = None
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
            elif not login_obj.have_response:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未收到服务器响应，请检查网络连接',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            elif not login_obj.legal:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未查找到当前用户，请检查是否使用了正确的钉钉账号登录',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            elif not login_obj.is_login:
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '登录失败，请重试',
                    QMessageBox.Ok
                )
                self.reject()
                sys.exit(1)
            else:
                self.user_name = login_obj.user_name
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
        main_gui.show()
        main_gui.listen_clipboard()
        main_gui.set_button()
        sys.exit(window_application.exec_())
    else:
        # 结束进程
        # sys.exit(window_application.exec_())
        sys.exit(0)

