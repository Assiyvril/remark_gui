import sys
import time

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QMessageBox
from dd_login_scripts import DingLoginRequestInterceptor, QR_URL
from main_gui import MainGui


class DDloginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_name = None
        self.user_shop = None
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
            print('登录事件触发')
            login_obj = self.request_interceptor.ding_login_obj
            if not login_obj:
                # 弹出提示框，提示用户登录失败
                print('登录对象为空')
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '软件发生内部错误，登录失败，请重试，或联系开发者',
                    QMessageBox.Ok
                )
                self.reject()
                time.sleep(8)
                exit(1)
            elif not login_obj.have_response:
                print('未收到服务器响应')
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未收到服务器响应，请检查网络连接',
                    QMessageBox.Ok
                )
                self.reject()
                time.sleep(8)
                exit(1)
            elif not login_obj.legal:
                print('登录对象不合法')
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '未查找到当前用户，请检查是否使用了正确的钉钉账号登录',
                    QMessageBox.Ok
                )
                self.reject()
                time.sleep(8)
                exit(1)
            elif not login_obj.is_login:
                print('登录失败')
                QMessageBox.warning(
                    self,
                    '登录出错',
                    '登录失败，请重试',
                    QMessageBox.Ok
                )
                self.reject()
                time.sleep(8)
                exit(1)
            else:
                self.user_name = login_obj.user_name
                self.user_shop = login_obj.user_shop
                print('信号处理--登录成功')
                self.accept()


if __name__ == '__main__':
    window_application = QApplication(sys.argv)
    login_dialog = DDloginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print('登录成功')
        main_gui = MainGui()
        main_gui.setupUi(main_gui)
        main_gui.CurrentUserLabel.setText('当前用户: ' + login_dialog.user_name)
        main_gui.CurrentStoreLabel.setText('当前店铺: ' + login_dialog.user_shop)
        main_gui.show()
        main_gui.listen_clipboard()
        main_gui.set_button()
        sys.exit(window_application.exec_())
    else:
        print('登录失败')
        # 结束进程
        exit(1)

