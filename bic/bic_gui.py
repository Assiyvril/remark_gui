"""
获取 BIC 码的 UI 窗口
用户点击 ”获取 BIC 码“ 按钮后，弹出此窗口
此窗口是一个浏览器页面，内容是 抖音店铺登录页面
用户在此页面登录抖音店铺后，抓取 cookie，然后关闭此窗口
"""
import sys
import time

from PyQt5.QtCore import pyqtSignal, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication, QDialog

URL = 'https://fxg.jinritemai.com/'


class BicWebView(QWebEngineView):

    get_full_cookie_signal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(BicWebView, self).__init__(*args, **kwargs)
        self.paget = QWebEnginePage()
        self.paget.profile().cookieStore().cookieAdded.connect(self.onCookieAdd)
        self.paget.setUrl(QUrl(URL))
        self.setPage(self.paget)
        self.resize(1300, 800)
        self.urlChanged.connect(self.on_url_changed)
        self.cookie = {}
        self.cookie_str = None

    def onCookieAdd(self, cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        self.cookie[name] = value

    def on_url_changed(self, url):
        if '/bic/order/printer' in url.toString():
            print('已登陆成功并到达 BIC 码页面')

            if self.loadFinished:
                time.sleep(2)
                cookie_str = self.get_cookie_str()
                self.get_full_cookie_signal.emit(cookie_str)
                print('web页面已将cookie发送出去')
                self.close()
                return cookie_str

    def get_cookie_str(self):
        cookie_str = ''
        for key, value in self.cookie.items():
            cookie_str += f'{key}={value};'
        self.cookie_str = cookie_str
        return cookie_str


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     view = BicWebView()
#     view.resize(1300, 800)
#     view.show()
#     sys.exit(app.exec_())
