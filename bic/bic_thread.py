import time
from PyQt5.QtCore import QThread, pyqtSignal
from .get_bic import BicCode

"""
获取 BIC 码的线程
"""


class GetBicThread(QThread):
    # 定义信号
    bic_finish_signal = pyqtSignal(bool, int)
    bic_process_signal = pyqtSignal(str)

    def __init__(self, cookie_str, user_shop_id, loop_count, *args, **kwargs):
        super(GetBicThread, self).__init__(*args, **kwargs)
        self.cookie_str = cookie_str
        self.user_shop_id = user_shop_id
        self.loop_count = loop_count
        self.amount = 0
        print('GetBicThread 初始化完成')
        print(f'cookie_str: {cookie_str}')
        print(f'user_shop_id: {user_shop_id}')
        print(f'loop_count: {loop_count}')

    def run(self):
        print('循环外部，run 执行')
        for times in range(1, self.loop_count + 1):
            print('循环即将开始', times)
            bic_code_obj = BicCode(
                cookie=self.cookie_str, user_shop_id=self.user_shop_id
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
