from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QUrl
from dd_login_scripts import DingLoginRequestInterceptor, QR_URL


class DingLoginGui(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置窗口标题
        self.setWindowTitle('钉钉扫码登录')
        self.setFixedSize(600, 400)
        # 设置窗口图标
        self.setWindowIcon(QIcon('flags/dd_login.png'))
        self.show()
        # 设置浏览器
        self.browser = QWebEngineView()
        self.page = QWebEnginePage()
        self.page.setUrl(QUrl(QR_URL))
        self.request_interceptor = DingLoginRequestInterceptor()
        self.page.profile().setRequestInterceptor(self.request_interceptor)
        self.browser.setPage(self.page)
        self.browser.show()

a = DingLoginGui()
