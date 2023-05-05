# -*- coding: utf-8 -*-
# UI 界面文件，继承自Qt Designer生成的文件
# 实现显示与逻辑分离
from PyQt5 import QtCore
from new_ui import Ui_mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence
from scripts import ProcessOrder


class MainGui(QMainWindow, Ui_mainWindow):

    def __init__(self):
        super().__init__()
        # 定义剪贴板对象
        self.clipboard = QApplication.clipboard()
        # 订单信息处理对象
        self.order_process_obj = None
        self.flag = None  # flag标记
        # 快捷键绑定
        self.shortcut = QShortcut(QKeySequence("Alt+S"), self)
        self.shortcut.activated.connect(self.submit_remark)
        # 暂不展示订单信息，只展示已有的备注和 flag

    def listen_clipboard(self):
        self.clipboard.dataChanged.connect(self.clipboard_changed)

    def set_button(self):
        """
        设置按钮功能
        :return:
        """
        # 退出程序按钮 QuitButton，退出所有窗口
        self.QuitButton.clicked.connect(QApplication.quit)

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
        if order_info['error']:
            # 展示错误信息
            self.CurrentOrderInfo.setText(
                f"查询的订单：{order_info['order']}, \n错误信息：{order_info['info']}"
            )
        # 在 CurrentOrderInfo 展示 flag 和备注信息
        # 在备注输入框展示备注信息
        # 将对应的 flag 按钮选中
        order_flag = order_info.get('flag')
        flag_text = order_info.get('flag_text', '无')
        remark = order_info.get('remark', '无')
        display_text = f'当前订单：\n{order}\n' + \
                       f'订单标记：\n{flag_text}\n' + \
                       f'备注信息：\n{remark}'
        self.CurrentOrderInfo.setText(display_text)

        # 备注输入框
        if remark:
            self.RemarkTextInput.setText(remark)
        else:
            self.RemarkTextInput.setText('当前订单无备注，请在此输入')

        # 设置 flag 标记
        if not order_flag:
            pass
        else:
            # self.flag = order_flag # TODO 到底使用哪个逻辑 再议
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
            pass

        # 实例化订单信息处理对象
        self.order_process_obj = ProcessOrder(text)
        # 校验是否为订单编号
        order = self.order_process_obj.check_order()
        if order:

            # 设置当前订单信息
            self.display_order_info(order)
            # 设置置顶
            self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
            self.window().show()
            # 取消置顶
            self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
            self.window().show()

        else:
            pass

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

        # flag 标记按钮, 当点击时，将 flag 值设置为对应的值
        if self.FlagRed.isChecked():
            self.flag = 'red'
        elif self.FlagGrey.isChecked():
            self.flag = 'grey'
        elif self.FlagYellow.isChecked():
            self.flag = 'yellow'
        elif self.FlagGreen.isChecked():
            self.flag = 'green'
        elif self.FlagBlue.isChecked():
            self.flag = 'blue'
        elif self.FlagPurple.isChecked():
            self.flag = 'purple'
        else:
            self.flag = None

        # 是否更改了 flag 标记
        if self.flag != self.order_process_obj.flag:
            # 更改了
            self.show_message(
                f'您更改了flag，将原本的{self.order_process_obj.flag}改为当前的：{self.flag}')
        # 提交备注信息
        result = self.order_process_obj.submit_remark(remark, self.flag)
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
