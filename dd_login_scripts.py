"""
封装钉钉扫码登陆
1 通过AppKey和AppSecret，获取企业内部应用的accessToken
2 通过 clientId（AppKey）和 clientSecret（AppSecret）获取用户 Token

"""
import re
import sys
import requests
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication

APP_KEY = 'dingj2boitttylsscgyd'   # web 前端 web.slpzb.com
APP_SECRET = '2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
REDIRECT_URI = 'https://web.slpzb.com/#/login'
QR_URL = f'https://oapi.dingtalk.com/connect/qrconnect?appid={APP_KEY}&response_type=code&scope=snsapi_login&state=STATE&redirect_uri={REDIRECT_URI}'


class DingLogin:
    """
    使用钉钉 sns 码登录
    抓取到 sns 码后，将 sns 码发给服务器
    """
    def __init__(self, sns_code):
        self.sns_code = sns_code
        self.is_login = False   # 是否登录成功
        self.have_response = False      # 是否有响应, 若没有响应则应检查网络
        self.legal = True     # 是否合法用户
        self.user_name = None       # 登陆后赋值的 用户名
        self.user_shop = None       # 登陆后赋值的 用户所属店铺
        self.user_shop_id = None    # 登陆后赋值的 用户所属店铺id

        self.login()

    def login(self):
        login_url = f'https://web.slpzb.com/rest/v1/account/dinglogin/?code={self.sns_code}&state=STATE&flatdata=2&myshop=shilipai'
        try:
            response = requests.get(login_url).json()
        except Exception:
            response = None
        if not response:
            return None
        if response.get('code') == 200 and response.get('msg') != 'success':
            self.legal = False
            self.have_response = True
            return None
        if response.get('code') == 200 and response.get('msg') == 'success':
            self.is_login = True
            self.have_response = True
            self.legal = True
        try:
            self.user_name = response.get('data').get('username')
        except Exception:
            self.user_name = '未获取到用户名'
        try:
            self.user_shop = response.get('data').get('prefix').get('name')
        except Exception:
            self.user_shop = '未获取到店铺名'
        try:
            self.user_shop_id = response.get('data').get('prefix').get('id')
        except Exception:
            self.user_shop_id = '未获取到店铺id'
        return True


class DingLoginRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """
    拦截请求
    """
    login_event = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ding_login_obj = None

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        sns_code = re.findall(r'code=(.*?)&', url)

        if sns_code:
            sns_code = sns_code[0]
            if len(sns_code) > 20:
                self.ding_login_obj = DingLogin(sns_code)
                self.login_event.emit(True)
                # login 事件触发后，将 ding_login_obj 传递给主窗口
        # 不让真正跳转，若是以 https://web.slpzb.com/ 开头的请求，都拦截
        if url.startswith('https://web.slpzb.com/'):
            info.block(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QWebEngineView()
    page = QWebEnginePage()
    page.setUrl(QUrl(QR_URL))
    t = DingLoginRequestInterceptor()
    page.profile().setRequestInterceptor(t)
    view.setPage(page)
    view.resize(600, 400)
    view.show()
    sys.exit(app.exec_())
