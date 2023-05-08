import sys
import time

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout

from dd_login_gui import DingLoginGui
from dd_login_scripts import DingLoginRequestInterceptor, QR_URL
from new_gui import MainGui

class DDloginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.webview = QWebEngineView()
        self.request_interceptor = DingLoginRequestInterceptor()

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        self.setLayout(layout)

        self.webview.page().profile().setRequestInterceptor(self.request_interceptor)
        self.webview.page().setUrl(QUrl(QR_URL))
        self.request_interceptor.login_success.connect(
            self.login_success
        )

    def login_success(self, success):
        self.accept()


if __name__ == '__main__':
    window_application = QApplication(sys.argv)
    login_dialog = DDloginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        print('登录成功')
        main_gui = MainGui()
        main_gui.setupUi(main_gui)
        main_gui.show()
        main_gui.listen_clipboard()
        main_gui.set_button()
        sys.exit(window_application.exec_())
    else:
        print('登录失败')
        sys.exit(window_application.exec_())