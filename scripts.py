# -*- coding: utf-8 -*-
# 额外脚本文件
"""
包括：
    一，订单编号处理
        1，正则校验是否为订单编号
        2，获取订单信息
"""
import re


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

    def check_order(self):
        text = self.order_text.strip()
        if re.match(r'^\d{15,20}$|^\d{5,10}-\d{15,20}$', text):
            return text
        else:
            return None

    def get_order_info(self):
        """
        获取订单信息 TODO 需要请求API
        :param order:
        :return:
        """
        order = self.check_order()
        if not order:
            data = {
                '订单': self.order_text,
                '信息': '订单编号错误，查询不到信息'
            }
            return data
        # TODO 请求API获取订单信息
        # 暂且返回测试数据
        data = {
            '订单': order,
            '店铺': '测试-包子铺',
            '用户': '测试用户-王麻子',
            '备注': '测试备注-客户不要醋',
            'flag': 'green',

        }
        self.true_order = order
        self.flag = data['flag']
        return data

    def get_bic(self):
        # TODO 请求API获取BIC码
        # 暂且返回测试数据
        order = self.check_order()
        if not order:
            bic_code = '订单编号错误，查询不到BIC码'
        else:
            bic_code = '测试BIC码 ywq123'
        return bic_code

    def submit_remark(self, remark, flag):
        # TODO 请求API提交备注
        # 暂且返回测试数据
        print('要提交的备注', remark)
        print('要提交的flag', flag)
        order = self.check_order()
        if not order:
            return False
        return True
