"""
封装钉钉扫码登陆
1 通过AppKey和AppSecret，获取企业内部应用的accessToken
2 通过 clientId（AppKey）和 clientSecret（AppSecret）获取用户 Token

"""
import json
import sys

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

# if __name__ == '__main__':
#     qr_url = 'https://login.dingtalk.com/login/qrcode.htm?goto=https%3A%2F%2Foapi.dingtalk.com%2Fconnect%2Foauth2%2Fsns_authorize%3Fappid%3Ddingqqjuy2zdbf7qd9v0%26response_type%3Dcode%26scope%3Dsnsapi_login%26state%3DSTATE%26redirect_uri%3Dhttp%3A%2F%2Fddt.zjyu.de'
#     reponse = requests.get(
#         url=qr_url,
#     )
#     print('reponse.text\n', reponse.text)
#     print('reponse.content\n', reponse.content)
#     print('reponse.json\n', reponse.json())
#     print('reponse.headers\n', reponse.headers)
#     print('reponse.cookies\n', reponse.cookies)
#     print('reponse.status_code\n', reponse.status_code)
#     print('reponse.url\n', reponse.url)
#     print('reponse.history\n', reponse.history)
#     print('reponse.encoding\n', reponse.encoding)
#     print('reponse.raw\n', reponse.raw)
#     print('reponse.reason\n', reponse.reason)
#     print('reponse.object\n', reponse)



if __name__ == '__main__':
    class MainWindow(QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # 设置窗口标题
            self.setWindowTitle('My Browser')
            self.setFixedSize(800,600)
            # 设置窗口图标
            self.setWindowIcon(QIcon('flags/6.png'))
            self.show()

            # 设置浏览器
            self.browser = QWebEngineView()
            qr_url = 'https://login.dingtalk.com/login/qrcode.htm?goto=https%3A%2F%2Foapi.dingtalk.com%2Fconnect%2Foauth2%2Fsns_authorize%3Fappid%3Ddingqqjuy2zdbf7qd9v0%26response_type%3Dcode%26scope%3Dsnsapi_login%26state%3DSTATE%26redirect_uri%3Dhttp%3A%2F%2Fddt.zjyu.de'
            # 指定打开界面的 URL
            self.browser.setUrl(QUrl(qr_url))
             # 添加浏览器到窗口中
            self.setCentralWidget(self.browser)

    # 创建应用
    app = QApplication(sys.argv)
    # 创建主窗口
    window = MainWindow()
    # 显示窗口
    window.show()
    # 运行应用，并监听事件
    app.exec_()