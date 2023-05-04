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
from hashlib import sha256

import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QApplication

APP_KEY = 'dingqqjuy2zdbf7qd9v0'
APP_SECRET = '2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
AGENT_ID = '2568548056'
TEM_ACCESS_TOKEN = 'e074889a23493072bc6bd768485d8c92'


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
        if response_data.get('accessToken') and response_data.get('refreshToken'):
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


if __name__ == '__main__':

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
            qr_url = 'https://login.dingtalk.com/oauth2/auth?redirect_uri=http://127.0.0.1:80&response_type=code&client_id=dingqqjuy2zdbf7qd9v0&scope=openid&state=dddd&prompt=consent'
            # 指定打开界面的 URL
            self.browser.setUrl(QUrl(qr_url))
             # 添加浏览器到窗口中
            self.setCentralWidget(self.browser)

        def url_changed(self, url):

            print(type(url.toString()))
            # http://127.0.0.1/?authCode=29682bbaf07f30ac91cce307e88493b5&state=dddd  提取出 authCode 29682bbaf07f30ac91cce307e88493b5
            auth_code = re.findall(r'authCode=(.*?)&', url.toString())
            if auth_code:
                print('发现code:', auth_code)

                time_stamp = time.time()
                print('time_stamp:\n', time_stamp)
                signature = base64.b64encode(
                    hmac.new(
                        APP_SECRET.encode('utf-8'),
                        time_stamp.encode('utf-8'),
                        digestmod=sha256
                    ).digest()
                )
                print('signature:\n', signature)

                url = f'https://oapi.dingtalk.com/sns/getuserinfo_bycode?accessKey=dingqqjuy2zdbf7qd9v0&timestamp={time_stamp}&signature={signature}'
                post_data = json.dumps(
                    {'tmp_auth_code': auth_code}
                )
                header = {
                    'Content-Type': 'application/json'
                }
                print('请求中')
                response = requests.post(
                    url=url,
                    data=post_data,
                    headers=header
                )
                print('Reponse: \n', response)
                print('Reponse.text: \n', response.text)
                print('Reponse.json: \n', response.json())

            else:
                print('没有获取到code')
                return None

        def get_user_info(self, sns_code):
            """
            根据 SNS code 获取用户信息
            :param sns_code:
            :return:
            """
            time_stamp = time.time()
            signature = base64.b64encode(
                hmac.new(
                    APP_SECRET.encode('utf-8'),
                    time_stamp.encode('utf-8'),
                    digestmod=sha256
                ).digest()
            )
            url = f'https://oapi.dingtalk.com/sns/getuserinfo_bycode?accessKey=dingqqjuy2zdbf7qd9v0&timestamp={time_stamp}&signature={signature}'
            post_data = json.dumps(
                {'tmp_auth_code': sns_code}
            )
            header = {
                'Content-Type': 'application/json'
            }
            response_data = requests.post(
                url=url,
                data=post_data,
                headers=header
            ).json()

            return response_data
    # 创建应用
    app = QApplication(sys.argv)
    # 创建主窗口
    window = MainWindow()
    # 显示窗口
    window.show()
    # 运行应用，并监听事件
    app.exec_()
