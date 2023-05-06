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
TEM_ACCESS_TOKEN = '6a94830698473ea7bc919ae825801c87'
QR_URL = 'https://oapi.dingtalk.com/connect/qrconnect?appid=dingqqjuy2zdbf7qd9v0&response_type=code&scope=snsapi_login&state=123&redirect_uri=http://127.0.0.1:80'


class DDLogin:

    def __init__(self, sns_code):
        self.access_token = TEM_ACCESS_TOKEN
        self.user_token_dict = None
        self.sns_code = sns_code
        # self.get_access_token()

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

    def get_user_info(self):
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
            {'tmp_auth_code': self.sns_code}
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

    def get_user_id(self, unionid):
        """
        通过 unionid 获取用户 userid
        :return:
        """
        url = 'https://oapi.dingtalk.com/user/getUseridByUnionid'
        query_params = {
            'access_token': self.access_token,
            'unionid': unionid
        }
        response = requests.get(
            url=url,
            params=query_params
        )
        response_data = response.json()
        print('user_id_info \n', response_data)
        return response_data


if __name__ == '__main__':

    class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
        def __init__(self, parent=None):
            super().__init__(parent)

        def interceptRequest(self, info):
            url = info.requestUrl().toString()
            print('url:', url)
            sns_code = re.findall(r'code=(.*?)&', url)
            print('sns_code:', sns_code)
            if sns_code:
                print('发现code:', sns_code)
                dd_login_obj = DDLogin(sns_code[0])
                print('实例化dd_login_obj成功')
                print('access_token:', dd_login_obj.access_token)
                print('sns_code:', dd_login_obj.sns_code)
                dd_response = dd_login_obj.get_user_info()
                if dd_response.get('errcode') != 0:
                    return False
                elif dd_response.get('errmsg') != 'ok':
                    return False
                user_info = dd_response.get('user_info')
                if not user_info:
                    return False
                union_id = user_info.get('unionid')
                dd_login_obj.get_user_id(union_id)

            else:
                pass

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
