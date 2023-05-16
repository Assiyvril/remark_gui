import time
from PyQt5.QtCore import QThread, pyqtSignal
from selenium.common import TimeoutException
from seleniumwire import webdriver

from .get_bic import BicCode

"""
获取 BIC 码的线程
"""


class GetBicThread(QThread):
    # 定义信号
    bic_finish_signal = pyqtSignal(bool, int)
    bic_process_signal = pyqtSignal(str)

    def __init__(self, user_shop_id, loop_count, *args, **kwargs):
        super(GetBicThread, self).__init__(*args, **kwargs)
        self.web_driver = webdriver.Chrome()
        self.user_shop_id = user_shop_id
        self.loop_count = loop_count
        self.amount = 0
        print('GetBicThread 初始化完成')
        print(f'user_shop_id: {user_shop_id}')
        print(f'loop_count: {loop_count}')

    def get_cookie(self):
        URL = 'https://fxg.jinritemai.com/'
        self.web_driver.get(URL)
        if self.web_driver.service.process:
            self.bic_process_signal.emit('浏览器启动成功, 请在100秒内登录')
        else:
            self.bic_process_signal.emit('浏览器启动失败')
            return None
        # 如果浏览器被关闭，那么就退出程序
        try:
            request = self.web_driver.wait_for_request('printer', timeout=100)
            cookie = request.headers.get('cookie')
            self.get_cookie_signal_str = '获取 cookie 成功'
            print('cookie：', cookie)
            self.web_driver.quit()
            return cookie
        except TimeoutException as e:
            self.web_driver.quit()
            self.bic_process_signal.emit('获取 cookie 失败，请求超时')
            return None

    def run(self):
        cookie = self.get_cookie()
        if not cookie:
            self.bic_process_signal.emit('获取 cookie 失败，程序退出')
            self.bic_finish_signal.emit(False, 0)
            return None
        print('循环外部，run 执行')
        for times in range(1, self.loop_count + 1):
            print('循环即将开始', times)
            bic_code_obj = BicCode(
                cookie_str=cookie,
                user_shop_id=self.user_shop_id
            )
            if bic_code_obj.upload_bic_result:
                bic_count = len(bic_code_obj.result_bic_list)
                self.amount += bic_count
                info_msg = f'第 {times} 次循环：已获取了{bic_count}条 BIC 码，并上传成功, 休眠 10 秒'
                print(info_msg)
                self.bic_process_signal.emit(info_msg)
                time.sleep(10)
            else:
                bic_count = len(bic_code_obj.result_bic_list)
                self.amount += bic_count
                info_msg = f'第 {times} 次循环出错，获取到 {bic_count} 条。下载过程：{bic_code_obj.get_pdf_signal_str}。解析过程：{bic_code_obj.parse_pdf_signal_str}。上传过程：{bic_code_obj.upload_bic_signal_str}, 休眠 10 秒'
                print(info_msg)
                self.bic_process_signal.emit(info_msg)
                time.sleep(10)

        self.bic_finish_signal.emit(True, self.amount)
