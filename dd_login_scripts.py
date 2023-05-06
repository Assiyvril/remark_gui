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
import urllib.parse
import requests
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication

APP_KEY = 'dingqqjuy2zdbf7qd9v0'
APP_SECRET = '2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
AGENT_ID = '2568548056'
TEM_ACCESS_TOKEN = '6a94830698473ea7bc919ae825801c87'
QR_URL = 'https://oapi.dingtalk.com/connect/qrconnect?' \
         'appid=dingqqjuy2zdbf7qd9v0&' \
         'response_type=code&scope=snsapi_login&state=123&' \
         'redirect_uri=http://127.0.0.1:80'


class DDLogin:

    def __init__(self, sns_code):
        self.access_token = None    # 应用的 access_token
        self.sns_code = sns_code    # 用户的 sns_code
        self.unionid = None     # 用户的 unionid，通过 sns_code 获取
        self.user_dd_id = None      # 用户的钉钉 ID，通过 unionid 获取
        self.is_login = False       # 是否登录成功
        self.user_name = None       # 登陆后赋值的 用户名
        self.user_shop = None       # 登陆后赋值的 用户所属店铺
        self.get_access_token()
        self.get_unionid()
        self.get_user_dd_id()
        self.login_by_user_dd_id()

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
        try:
            # {
            #   'expireIn': 7200,
            #   'accessToken': 'fe63eba4b7b13113a7668182ae67bda9'
            #  }
            # 没有 errcode 和 errmsg
            response_data = response.json()
        except Exception:
            response_data = None
        if response_data:
            self.access_token = response_data.get('accessToken')
            return True
        else:
            return None

    def get_unionid(self):
        """
        根据 SNS code 获取用户信息 unionid
        :return:
        """
        if not self.sns_code:
            return None
        time_stamp = int(time.time() * 1000)
        # 签名算法为HmacSHA256，签名数据是当前时间戳timestamp，密钥是 APP_SECRET，
        # 使用密钥对 timestamp 计算签名值。
        signature_bytes = hmac.new(APP_SECRET.encode('utf-8'),
                                   str(time_stamp).encode('utf-8'),
                                   sha256).digest()
        signature = base64.b64encode(signature_bytes).decode('utf-8')
        signature = urllib.parse.quote_plus(signature)
        url = f'https://oapi.dingtalk.com/sns/getuserinfo_bycode?' \
              f'accessKey=dingqqjuy2zdbf7qd9v0&' \
              f'timestamp={time_stamp}&' \
              f'signature={signature}'
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
        try:
            response_data = response.json()
        except Exception:
            response_data = None
        if response_data:
            if response_data.get('errmsg') == 'ok':
                self.unionid = response_data.get('user_info').get('unionid')
                return True
            else:
                return None
        else:
            return None

    def get_user_dd_id(self):
        """
        通过 unionid 获取用户 userid
        :return:
        """
        if not self.unionid:
            return None
        url = 'https://oapi.dingtalk.com/user/getUseridByUnionid'
        query_params = {
            'access_token': self.access_token,
            'unionid': self.unionid
        }
        response = requests.get(
            url=url,
            params=query_params
        )
        try:
            response_data = response.json()
        except Exception:
            print('response_data:', response.text)
            response_data = None
        if response_data:
            if response_data.get('errmsg') == 'ok':
                self.user_dd_id = response_data.get('userid')
                return self.user_dd_id
            else:
                return None
        else:
            return None

    def login_by_user_dd_id(self):
        # 通过钉钉 ID 登录系统
        # TODO 需要请求API获取用户信息
        if not self.user_dd_id:
            return None
        # TODO 登录逻辑
        # 暂时测试返回 True
        print(self.user_dd_id, '登录成功')
        self.user_name = '刘六柳'
        self.user_shop = '老张火锅店'
        self.is_login = True
        return True


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, parent=None):
        super().__init__(parent)

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        sns_code = re.findall(r'code=(.*?)&', url)
        if not sns_code:
            pass
        dd_login_obj = DDLogin(sns_code[0])
        # TODO
        if dd_login_obj.is_login:
            # 登录成功，关闭浏览器窗口
            # TODO
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
