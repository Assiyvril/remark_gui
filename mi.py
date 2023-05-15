import os
import re
import time
import base64
import random
import hashlib
import requests
from Crypto.Cipher import AES

# proxies = {"http":"http://127.0.0.1:8080"}
proxies = {}


def get_mac():
    ## get mac
    r0 = requests.get("http://192.168.31.1/cgi-bin/luci/web", proxies=proxies)
    mac = re.findall(r'deviceId = \'(.*?)\'', r0.text)[0]
    # print(mac)
    return mac


def get_account_str():
    ## read /etc/config/account
    r1 = requests.get(
        "http://192.168.31.1/api-third-party/download/extdisks../etc/config/account",
        proxies=proxies)
    print(r1.text)
    account_str = re.findall(r'admin\'? \'(.*)\'', r1.text)[0]
    return account_str


def create_nonce(mac):
    type_ = 0
    deviceId = mac
    time_ = int(time.time())
    rand = random.randint(0, 10000)
    return "%d_%s_%d_%d" % (type_, deviceId, time_, rand)


def calc_password(nonce, account_str):
    m = hashlib.sha1()
    m.update((nonce + account_str).encode('utf-8'))
    return m.hexdigest()


mac = get_mac()
account_str = get_account_str()
## login, get stok
nonce = create_nonce(mac)
password = calc_password(nonce, account_str)
data = "username=admin&password={password}&logtype=2&nonce={nonce}".format(
    password=password, nonce=nonce)
r2 = requests.post("http://192.168.31.1/cgi-bin/luci/api/xqsystem/login",
                   data=data,
                   headers={
                       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
                       "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                   proxies=proxies)
# print(r2.text)
stok = re.findall(r'"token":"(.*?)"', r2.text)[0]
print("stok=" + stok)
