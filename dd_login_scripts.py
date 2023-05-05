"""
封装钉钉扫码登陆
1 通过AppKey和AppSecret，获取企业内部应用的accessToken
2 通过 clientId（AppKey）和 clientSecret（AppSecret）获取用户 Token

"""
import base64
import hmac
import json
import re
import sys
import time
import urllib
from hashlib import sha256

import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QMainWindow, QApplication

APP_KEY = 'dingqqjuy2zdbf7qd9v0'
APP_SECRET = '2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
AGENT_ID = '2568548056'
TEM_ACCESS_TOKEN = 'e074889a23493072bc6bd768485d8c92'
QR_URL = 'https://oapi.dingtalk.com/connect/qrconnect?appid=dingqqjuy2zdbf7qd9v0&response_type=code&scope=snsapi_login&state=123&redirect_uri=http://127.0.0.1:80'

class DDLogin:

    def __init__(self):
        self.access_token = 'e074889a23493072bc6bd768485d8c92'
        self.user_token_dict = None

    def get_access_token(self):
        """
        获取企业内部应用的accessToken
        :return:
        """
        url = 'https://api.dingtalk.com/v1.0/oauth2/accessToken/'
        post_data = json.dumps(
            {
                'appKey': APP_KEY,
                'appSecret': APP_SECRET
            }
        )
        header = {
            'Content-Type': 'application/json'
        }

        response = requests.post(
            url=url,
            data=post_data,
            headers=header
        )
        access_token = response.json().get('accessToken')
        if access_token:
            self.access_token = access_token
            return access_token
        else:
            return None

    def get_user_token(self):
        """
        获取用户 token
        :return:
        """
        url = 'https://api.dingtalk.com/v1.0/oauth2/userAccessToken/'
        post_data = json.dumps(
            {
                'clientId': APP_KEY,
                'clientSecret': APP_SECRET,
                'code': self.access_token,
                'grantType': 'authorization_code'
            }
        )
        header = {
            'Content-Type': 'application/json'
        }
        response_data = requests.post(
            url=url,
            data=post_data,
            headers=header
        ).json()
        print(response_data)
        if response_data.get('accessToken') and response_data.get(
                'refreshToken'):
            self.user_token_dict = response_data
            return response_data
        else:
            return None

    def get_sns(self):
        """
        获取用户授权的SNS_Code
        :return:
        """
        url = f'https://oapi.dingtalk.com/connect/qrconnect?appid={APP_KEY}&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=http://ddt.zjyu.de'
        response = requests.get(url=url)
        print(response.text)
        return None


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置窗口标题
        self.setWindowTitle('My Browser')
        self.setFixedSize(1600, 1000)
        # 设置窗口图标
        self.setWindowIcon(QIcon('flags/6.png'))
        self.show()

        # 设置浏览器
        self.browser = QWebEngineView()
        # 绑定url改变信号
        self.browser.urlChanged.connect(self.url_changed)
        qr_url = 'http://data.slpzb.com/login.html'
        # 指定打开界面的 URL
        self.browser.setUrl(QUrl(qr_url))
        # 添加浏览器到窗口中
        self.setCentralWidget(self.browser)

    def url_changed(self, url):

        # http://127.0.0.1/?authCode=29682bbaf07f30ac91cce307e88493b5&state=dddd  提取出 authCode 29682bbaf07f30ac91cce307e88493b5
        auth_code = re.findall(r'authCode=(.*?)&', url.toString())
        if auth_code:
            # 中断链接
            # self.browser.setUrl(QUrl('about:blank'))
            print('发现code:', auth_code)
            a = self.get_user_info(auth_code[0])
            print('GET \n', a)
        else:
            print('没有获取到code')
            return None

    def get_user_info(self, sns_code):
        """
        根据 SNS code 获取用户信息
        :param sns_code:
        :return:
        """
        time_stamp = int(time.time() * 1000)
        # 签名算法为HmacSHA256，签名数据是当前时间戳timestamp，密钥是 APP_SECRET，使用密钥对 timestamp 计算签名值。

        signature_bytes = hmac.new(APP_SECRET.encode('utf-8'),
                                   str(time_stamp).encode('utf-8'),
                                   sha256).digest()

        signature = base64.b64encode(signature_bytes).decode('utf-8')
        import urllib.parse
        signature = urllib.parse.quote_plus(signature)
        print('signature:\n', signature)
        url = f'https://oapi.dingtalk.com/sns/getuserinfo_bycode?accessKey=dingqqjuy2zdbf7qd9v0&timestamp={time_stamp}&signature={signature}'
        post_data = json.dumps(
            {'tmp_auth_code': sns_code}
        )
        header = {
            'Content-Type': 'application/json'
        }
        response = requests.post(
            url=url,
            data=post_data,
            headers=header
        )
        print('response_text:\n', response.text)
        response_data = response.json()
        print('response_data:\n', response_data)

        return response_data


if __name__ == '__main__':

    class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
        def __init__(self, parent=None):
            super().__init__(parent)

        def interceptRequest(self, info):
            # 打印请求的url
            url = info.requestUrl().toString()
            auth_code = re.findall(r'code=(.*?)&', url)
            if auth_code:
                print('发现code:', auth_code)
                dd_response = self.get_user_info(auth_code[0])
                if dd_response.get('errcode') != 0:
                    return False
                elif dd_response.get('errmsg') != 'ok':
                    return False
                user_info = dd_response.get('user_info')
                if not user_info:
                    return False
                union_id = user_info.get('unionid')
                dd_id = user_info.get('dingId')
                openid = user_info.get('openid')

            else:
                return False

        def get_user_info(self, sns_code):
            """
            根据 SNS code 获取用户信息
            :param sns_code:
            :return:
            """
            time_stamp = int(time.time() * 1000)
            # 签名算法为HmacSHA256，签名数据是当前时间戳timestamp，密钥是 APP_SECRET，使用密钥对 timestamp 计算签名值。

            signature_bytes = hmac.new(APP_SECRET.encode('utf-8'),
                                       str(time_stamp).encode('utf-8'),
                                       sha256).digest()

            signature = base64.b64encode(signature_bytes).decode('utf-8')
            import urllib.parse
            signature = urllib.parse.quote_plus(signature)
            url = f'https://oapi.dingtalk.com/sns/getuserinfo_bycode?accessKey=dingqqjuy2zdbf7qd9v0&timestamp={time_stamp}&signature={signature}'
            post_data = json.dumps(
                {'tmp_auth_code': sns_code}
            )
            header = {
                'Content-Type': 'application/json'
            }
            response = requests.post(
                url=url,
                data=post_data,
                headers=header
            )
            response_data = response.json()
            return response_data

        def get_user_id(self, union_id):
            """
            根据 union_id 获取用户 id
            :param union_id:
            :return:
            """
            url = 'https://oapi.dingtalk.com/user/getUseridByUnionid'



    app = QApplication(sys.argv)
    view = QWebEngineView()
    page = QWebEnginePage()
    page.setUrl(QUrl(QR_URL))
    t = WebEngineUrlRequestInterceptor()
    page.profile().setRequestInterceptor(t)
    view.setPage(page)
    view.resize(600, 400)
    view.show()
    sys.exit(app.exec_())
