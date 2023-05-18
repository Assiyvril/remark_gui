import time
from win32process import CREATE_NO_WINDOW
from PyQt5.QtCore import QThread, pyqtSignal
from selenium import webdriver
from selenium.common import NoSuchWindowException, TimeoutException

from .get_bic import BicCode

"""
获取 BIC 码的线程
"""


class GetBicThread(QThread):
    # 定义信号
    bic_finish_signal = pyqtSignal(bool, int)
    bic_process_signal = pyqtSignal(str)
    browser_killed_signal = pyqtSignal(bool)    # 浏览器被意外关闭的信号
    get_cookie_signal = pyqtSignal(bool)

    def __init__(self, user_shop_id, loop_count, *args, **kwargs):
        super(GetBicThread, self).__init__(*args, **kwargs)
        self.web_driver_options = webdriver.ChromeOptions()

        self.web_driver_options.add_argument('--silent')
        self.web_driver_options.add_argument('--log-level=3')
        self.web_driver_options.add_argument('--disable-gpu')
        self.web_driver_options.add_argument('--disable-extensions')
        self.web_driver_options.add_argument('--disable-dev-shm-usage')
        self.web_driver = webdriver.Chrome(options=self.web_driver_options)
        self.web_driver.service.creation_flags = CREATE_NO_WINDOW
        self.user_shop_id = user_shop_id
        self.loop_count = loop_count
        self.amount = 0

    def get_cookie(self):
        URL = 'https://fxg.jinritemai.com/'
        self.web_driver.implicitly_wait(200)
        self.web_driver.get(URL)
        # if self.web_driver.service.process:
        #     self.bic_process_signal.emit('浏览器启动成功, 请在100秒内登录')
        # else:
        #     self.bic_process_signal.emit('浏览器启动失败')
        #     return None
        # 如果浏览器被关闭，那么就结束线程
        try:
            for i in range(1, 200):
                current_url = self.web_driver.current_url
                if '/bic/order/printer' in current_url:
                    cookie = self.web_driver.execute_script('return document.cookie')
                    self.web_driver.quit()
                    return cookie
                time.sleep(1)
            self.web_driver.quit()
            return None
        except NoSuchWindowException as e:
            self.browser_killed_signal.emit(True)
            self.web_driver.quit()
            return None

        except TimeoutException as e:
            self.web_driver.quit()
            return None

    def run(self):
        cookie = self.get_cookie()
        if not cookie:
            self.bic_process_signal.emit('获取 cookie 失败，程序退出')
            self.bic_finish_signal.emit(False, 0)
            return None
        self.get_cookie_signal.emit(True)
        for times in range(1, self.loop_count + 1):
            bic_code_obj = BicCode(
                cookie_str=cookie,
                user_shop_id=self.user_shop_id
            )
            if bic_code_obj.upload_bic_result:
                bic_count = len(bic_code_obj.result_bic_list)
                self.amount += bic_count
                info_msg = f'第 {times} 次循环：已获取了{bic_count}条 BIC 码，并上传成功, 休眠 10 秒'
                self.bic_process_signal.emit(info_msg)
                time.sleep(10)
            else:
                bic_count = len(bic_code_obj.result_bic_list)
                self.amount += bic_count
                info_msg = f'第 {times} 次循环出错，获取到 {bic_count} 条。下载过程：{bic_code_obj.get_pdf_signal_str}。解析过程：{bic_code_obj.parse_pdf_signal_str}。上传过程：{bic_code_obj.upload_bic_signal_str}, 休眠 10 秒'
                self.bic_process_signal.emit(info_msg)
                time.sleep(10)

        self.bic_finish_signal.emit(True, self.amount)
