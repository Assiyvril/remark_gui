# -*- coding: utf-8 -*-
"""
监控剪切板内容
有新的文本内容复制到剪切板时，校验是否为订单编号
如果是订单编号，则弹出程序主窗口，并请求服务器获取订单信息
识别订单编号的规则：r'^\d{15,20}$|^\d{5,10}-\d{15,20}$'
"""
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QClipboard
import re

from gui import Ui_mainWindow


class ListenClipboard(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clipboard = self.clipboard()
        self.clipboard.dataChanged.connect(self.clipboard_changed)

    def check_order(self, text):
        """
        正则校验是否为订单编号
        r'^\d{15,20}$|^\d{5,10}-\d{15,20}$
        :return:
        """
        text = text.strip()
        if re.match(r'^\d{15,20}$|^\d{5,10}-\d{15,20}$', text):
            return text
        else:
            return None


    def clipboard_changed(self):
        text = self.clipboard.text()
        # 先校验内容是否为文本，不能为图片等
        if not self.clipboard.mimeData().hasText():
            print('非文本内容')
        print('文本内容：', text, '长度：', len(text), '类型：', type(text))

        # 校验是否为订单编号
        order_id = self.check_order(text)
        if order_id:
            print('检测到订单编号：', order_id)
        else:
            print('非订单编号', text)


if __name__ == '__main__':
    app = ListenClipboard([])
    app.exec_()
