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
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication

# APP_KEY = 'dingqqjuy2zdbf7qd9v0'
APP_KEY = 'dingj2boitttylsscgyd'   # web 前端 web.slpzb.com
APP_SECRET = '2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
# REDIRECT_URI = 'http://127.0.0.1:80'
REDIRECT_URI = 'https://web.slpzb.com/#/login'
QR_URL = f'https://oapi.dingtalk.com/connect/qrconnect?appid={APP_KEY}&response_type=code&scope=snsapi_login&state=STATE&redirect_uri={REDIRECT_URI}'
# QQ_URL = 'https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=dingfxj522ilwmlympws&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=http://data.slpzb.com/rest/v1/account/dinglogin/?groupID=1&flatdata=1'


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
        print('获取 access_token')
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
