# -*- coding: utf-8 -*-
# UI 界面文件，继承自Qt Designer生成的文件
# 实现显示与逻辑分离
import re

from PyQt5 import QtCore

from new_ui import Ui_mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox

from scripts import ProcessOrder


class MainGui(QMainWindow, Ui_mainWindow):
    def __init__(self):
        super().__init__()
        # 定义剪贴板对象
        self.clipboard = QApplication.clipboard()
        # 订单信息处理对象
        self.order_process_obj = None
        self.flag = None    # flag标记

    def listen_clipboard(self):
        self.clipboard.dataChanged.connect(self.clipboard_changed)

    def set_button(self):
        """
        设置按钮功能
        :return:
        """
        # 退出程序按钮 QuitButton
        self.QuitButton.clicked.connect(self.close)

        # 获取 BIC 码按钮 GetBicButton
        self.GetBicButton.clicked.connect(self.get_bic)

        # 清空按钮 清除输入的备注信息 RemarkTextInput ClearRemarkButton
        self.ClearRemarkButton.clicked.connect(self.clear_remark)

        # 提交按钮 SubmitRemarkButton
        self.SubmitRemarkButton.clicked.connect(self.submit_remark)

    def display_order_info(self, order):
        """
        获取订单信息并显示
        :param order:
        :return:
        """
        # 显示订单编号
        self.CurrentOrderLabel.setText('当前订单：' + order)
        # 获取订单信息 TODO 需要请求API
        order_info = self.order_process_obj.get_order_info()
        # 显示订单信息
        self.CurrentOrderInfo.setText(str(order_info))
        # 设置 flag 标记
        order_flag = order_info['flag']
        print('flag:', order_flag)
        if not order_flag:
            pass
        else:
            self.flag = order_flag
            # 显示flag
            flag_dict = {
                'red': self.FlagRed,
                'grey': self.FlagGrey,
                'yellow': self.FlagYellow,
                'green': self.FlagGreen,
                'blue': self.FlagBlue,
                'purple': self.FlagPurple
            }
            flag_dict[order_flag].setChecked(True)


    def clipboard_changed(self):
        text = self.clipboard.text()
        # 先校验内容是否为文本，不能为图片等
        if not self.clipboard.mimeData().hasText():
            print('非文本内容')
        print('文本内容：', text, '长度：', len(text), '类型：', type(text))

        # 实例化订单信息处理对象
        self.order_process_obj = ProcessOrder(text)
        # 校验是否为订单编号
        order = self.order_process_obj.check_order()
        if order:
            print('检测到订单编号：', order)
            # 设置当前订单信息
            self.display_order_info(order)
            # 设置置顶
            self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            self.window().show()
            # 取消置顶
            self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
            self.window().show()

        else:
            print('非订单编号', text)

    def get_bic(self):
        """
        获取 BIC 码
        方法在 ProcessOrder 类中，目前返回的测试数据
        TODO 需要请求API
        :return:
        """
        # 获取 BIC 码
        if self.order_process_obj is None:
            self.show_message('请先复制一个订单编号, 才能获取 BIC')
            return None
        bic = self.order_process_obj.get_bic()
        # 显示 BIC 码
        self.BicLabel.setText('BIC 码：' + bic)

        return None

    def clear_remark(self):
        """
        清除 RemarkTextInput 中的内容
        :return:
        """
        self.RemarkTextInput.clear()
        return None

    def submit_remark(self):
        # TODO 需要请求API之后再来测试
        if self.order_process_obj is None:
            self.show_message('请先复制一个订单编号, 才能提交备注')
            return None
        # 获取输入的备注信息
        remark = self.RemarkTextInput.toPlainText()
        # 校验备注信息
        if not remark:
            self.show_message('不能提交空备注')
            return None
        result = self.order_process_obj.submit_remark(remark)
        if result:
            self.show_message('提交备注成功')
            # 清空备注输入框
            self.RemarkTextInput.clear()
            # 刷新订单信息
            order_info = self.order_process_obj.get_order_info()
            self.CurrentOrderInfo.setText(str(order_info))
        else:
            self.show_message('提交备注失败')

        return None

    def show_message(self, message: str):
        """
        弹出一个消息提示框
        :param message:
        :return:
        """
        QMessageBox.warning(self, '提示', message, QMessageBox.Ok)


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    mainWindow = MainGui()
    mainWindow.setupUi(mainWindow)
    mainWindow.show()
    mainWindow.listen_clipboard()
    mainWindow.set_button()
    sys.exit(app.exec_())
