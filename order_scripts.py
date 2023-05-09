# -*- coding: utf-8 -*-
# 额外脚本文件
"""
包括：
    一，订单编号处理
        1，正则校验是否为订单编号
        2，获取订单信息
"""
import json
import re

import requests

FLAG_DICT = {
    '0': 'grey',
    '1': 'red',
    '2': 'yellow',
    '3': 'green',
    '4': 'blue',
    '5': 'purple',
    '6': 'purple',
    'grey': '灰色',
    'red': '红色',
    'yellow': '黄色',
    'green': '绿色',
    'blue': '蓝色',
    'purple': '紫色',
}


class ProcessOrder:
    """
    封装订单处理的类
    1，正则校验订单编号是否合法
    2，获取订单信息
    3，获取 BIC 码
    """

    def __init__(self, order_text):
        self.order_text = order_text    # 用户通过复制输入的订单编号文本，可能不合法
        self.true_order = None      # 真正的订单编号，合法的
        self.flag = None        # 订单 Flag
        self.flag_text = None       # 订单 Flag 文本
        self.user_name = None       # 用户名
        self.shop_id = None     # 店铺 ID

    def check_order(self):
        text = self.order_text.strip()
        if re.match(r'^\d{15,20}$|^\d{5,10}-\d{15,20}$', text):
            return text
        else:
            return None

    def get_order_info(self):
        """
        获取订单信息
        :return:
        """
        order = self.check_order()
        if not order:
            data = {
                'order': self.order_text,
                'info': '查询不到信息, 可能是订单编号有误',
                'error': True
            }
            return data

        # 请求API获取订单信息，只能获取到 备注：seller_words 和 flag：star
        url = 'https://web.slpzb.com/rest/v1/douyin_up_memo/'
        headers = {
            'Content-Type': 'application/json'
        }
        post_data = json.dumps(
            {
                "order_id": order,
                "flat": "getmemo"
            }
        )
        response = requests.post(
            url=url,
            data=post_data,
            headers=headers
        ).json()

        response_data = response.get('data')
        if not response_data:
            data = {
                'order': order,
                'info': '查询不到信息, 可能是订单编号有误',
                'error': True
            }
            return data
        remark = response_data.get('seller_words')
        flag = response_data.get('star')
        data = {
            'order': order,
            'flag': FLAG_DICT.get(flag),
            'flag_text': FLAG_DICT.get(FLAG_DICT.get(flag)),
            'remark': remark,
            'error': False
        }
        self.true_order = order
        self.flag = FLAG_DICT.get(flag)
        self.flag_text = FLAG_DICT.get(FLAG_DICT.get(flag))
        return data

    def get_bic(self):
        # TODO 请求API获取BIC码 暂时不做此功能
        # 暂且返回测试数据
        order = self.check_order()
        if not order:
            bic_code = '订单编号错误，查询不到BIC码'
        else:
            bic_code = '暂不开放此功能'
        return bic_code

    def submit_remark(self, remark, flag_num_str):
        url = 'https://web.slpzb.com/rest/v1/douyin_up_memo/'
        headers = {
            'Content-Type': 'application/json'
        }
        post_data = json.dumps(
            {
                "flat": "upbanner",
                "order_id": self.true_order,
                "remark": remark,
                "star": flag_num_str,
                "prefix_id": self.shop_id,
                "username": self.user_name
            }
        )
        response = requests.post(
            url=url,
            data=post_data,
            headers=headers
        ).json()
        re_msg = response.get('msg')
        if re_msg != '操作成功':
            data = {
                'error': True,
                'msg': '提交失败, 请检查网络或联系管理员'
            }
            return data
        response_data = response.get('query')
        if not response_data:
            data = {
                'error': True,
                'msg': '提交成功, 但返回数据有误，请将此 bug 报告给管理员'
            }
            return data
        remark_changed = response_data.get('memo')
        order_be_changed = response_data.get('tbno')
        flag_changed = response_data.get('banner')
        data = {
            'error': False,
            'msg': '提交成功',
            'remark_changed': remark_changed,
            'order_be_changed': order_be_changed,
            'flag_changed_text': FLAG_DICT.get(FLAG_DICT.get(flag_changed))
        }
        print('response_data\n', response_data)
        return data
