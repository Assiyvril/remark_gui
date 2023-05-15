# -*- coding: utf-8 -*-
# UI 界面文件，继承自Qt Designer生成的文件
# 实现显示与逻辑分离
import re
import time

from PyQt5 import QtCore

from bic.bic_gui import BicWebView
from bic.bic_thread import GetBicThread
from bic.get_bic import BicCode
from main_ui_0515 import Ui_mainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QShortcut, \
    QInputDialog
from PyQt5.QtGui import QKeySequence
from order_scripts import ProcessOrder


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

        self.input_count_dialog = QInputDialog(self)

        # 保存登录的当前用户信息
        self.user_name = None
        self.user_shop = None
        self.user_shop_id = None

        # 修改前的订单信息，用于对比展示
        self.origin_remark = None
        self.origin_flag_text = None

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
        # 获取订单信息
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
        self.origin_remark = remark
        self.origin_flag_text = flag_text
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
            # self.flag = order_flag
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
        self.statusbar.showMessage('订单信息获取成功')

    def clipboard_changed(self):

        # 先校验内容是否为文本，不能为图片等
        if self.clipboard.mimeData().hasText():
            text = self.clipboard.text().strip()
            if re.match(r'^\d{15,20}$|^\d{5,10}-\d{15,20}$', text):
                # 实例化订单信息处理对象
                self.order_process_obj = ProcessOrder(text)
                # 设置当前订单信息
                self.display_order_info(text)
                self.order_process_obj.shop_id = self.user_shop_id
                self.order_process_obj.user_name = self.user_name
                # 设置置顶
                self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
                self.window().show()
                # 取消置顶
                self.window().setWindowFlag(QtCore.Qt.WindowStaysOnTopHint,
                                            False)
                self.window().show()

            else:
                pass

    def get_bic(self):
        """
        获取 BIC 码
        方法在 ProcessOrder 类中，目前返回的测试数据
        :return:
        """
        # 获取 BIC 码
        if not self.user_shop_id:
            self.show_message('当前用户没有所属店铺，不能使用 BIC 码功能')
            return
        msg = '请在弹出的浏览器窗口中登录,' \
              '登录完成后进入 "订单管理 -> QIC 管理 -> QIC 质检" 页面, ' \
              '浏览器抓取到 Cookie 后会自动关闭, ' \
              '在抓取完成之前请不要进行其它操作'
        QMessageBox.information(self, '用法', msg)

        count = self.BicCountInput.value()
        if not count:
            QMessageBox.warning(self, '警告', '请先输入要获取的 BIC 数量')
            return None
        # 计算循环次数， count / 100 向下取整
        loop_count = count // 100

        self.statusbar.showMessage('正在获取 BIC 码...')
        # 禁用按钮
        self.GetBicButton.setChecked(True)
        self.GetBicButton.setDisabled(True)
        self.QuitButton.setDisabled(True)
        self.SubmitRemarkButton.setDisabled(True)
        self.ClearRemarkButton.setDisabled(True)

        def get_bic_by_cookie(cookie):
            print('main_gui get_bic_by_cookie 执行')
            bic_web_view.close()
            self.get_bic_thread = GetBicThread(
                cookie_str=cookie,
                user_shop_id=self.user_shop_id,
                loop_count=loop_count,
            )
            self.get_bic_thread.bic_process_signal.connect(self.show_process)
            self.get_bic_thread.bic_finish_signal.connect(self.bic_finish)
            self.get_bic_thread.start()

        bic_web_view = BicWebView()
        bic_web_view.get_full_cookie_signal.connect(get_bic_by_cookie)
        bic_web_view.show()
        return None

    def show_process(self, process):
        """
        显示进度
        :param process:
        :return:
        """
        self.BicLabel.setText(process)
        return None

    def bic_finish(self, result_bool, amount):
        """
        获取 BIC 码完成
        :param bic_list:
        :return:
        """
        if result_bool:
            info = f'获取 BIC 完成, 共获取到 {amount} 个 BIC 码'
            self.BicLabel.setText(info)
            self.statusbar.showMessage('BIC 码获取圆满完成')
        else:
            info = f'获取 BIC 完成，但中间出现错误，获取到的数量为 {amount}'
            self.BicLabel.setText(info)
            self.statusbar.showMessage('BIC 码获取完成，但是程中出现错误')

        # 启用按钮
        self.GetBicButton.setChecked(False)
        self.GetBicButton.setDisabled(False)
        self.QuitButton.setDisabled(False)
        self.SubmitRemarkButton.setDisabled(False)
        self.ClearRemarkButton.setDisabled(False)
        QMessageBox.information(self, '提示', info)
        return None

    def clear_remark(self):
        """
        清除 RemarkTextInput 中的内容
        :return:
        """
        self.RemarkTextInput.clear()
        return None

    def submit_remark(self):

        if self.order_process_obj is None:
            self.show_message('请先复制一个订单编号, 才能提交备注')
            return None

        # 获取输入的备注信息
        remark = str(self.RemarkTextInput.toPlainText())
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
        # if self.flag != self.order_process_obj.flag:
        #     # 更改了
        #     self.show_message(
        #         f'您更改了flag，将原本的{self.order_process_obj.flag}改为当前的：{self.flag}')

        # 提交备注信息 以数字形式提交 flag 标记， 0 grey， 1 red， 2 yellow， 3 green， 4 blue，
        # 5 purple, 6 purple
        flag_dict = {
            'red': '1',
            'grey': '0',
            'yellow': '2',
            'green': '3',
            'blue': '4',
            'purple': '5'
        }
        flag_num_str = flag_dict.get(self.flag, '0')
        result = self.order_process_obj.submit_remark(
            remark=remark, flag_num_str=flag_num_str
        )
        if result['error']:
            msg = f"提交备注失败，错误信息：{result['msg']}"
            self.show_message(msg)
            return False

        self.show_message('提交备注成功')
        # 清空备注输入框
        self.RemarkTextInput.clear()
        # 在 CurrentOrderInfo 显示修改后的信息
        remark_changed = result['remark_changed']
        order_be_changed = result['order_be_changed']
        flag_changed_text = result['flag_changed_text']
        display_text = f'修改完成！\n被修改的订单：\n{order_be_changed}\n' + \
                       f'原本的备注：\n{self.origin_remark}\n' + \
                       f'被修改为了：\n{remark_changed}\n' + \
                       f'原本的flag：\n{self.origin_flag_text}\n' + \
                       f'被修改为了：\n{flag_changed_text}'
        self.CurrentOrderInfo.setText(display_text)
        return True

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
