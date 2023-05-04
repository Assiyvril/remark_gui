# -*- coding: utf-8 -*-
import urllib.parse

APP_SECRET = r'2DeitGN2KKvEMixQL_CO4tc-t0VTJRrGsuwP9R5AdM0XSPpNUDqJ7g2NuIFxlEu5'
import base64
import hmac
import json
import re
import sys
import time
from hashlib import sha256

def sign(appSecret):
    # 根据timestamp, appSecret计算签名值

    # 根据timestamp, appSecret计算签名值
    time_stamp = int(round(time.time() * 1000))
    # 签名算法为HmacSHA256，签名数据是当前时间戳timestamp，密钥是 APP_SECRET，使用密钥对 timestamp 计算签名值。

    signature_bytes = hmac.new(APP_SECRET.encode('utf-8'),
                               str(time_stamp).encode('utf-8'),
                               sha256).digest()


    signature = base64.b64encode(signature_bytes).decode('utf-8')
    signature = urllib.parse.quote_plus(signature)
    print(signature)

    if signature == "":
        return None

    return signature

print(sign(APP_SECRET))