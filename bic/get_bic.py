import json
import re
import requests
import filetype
import pdfplumber
import io

GET_BIC_URL = 'https://fxg.jinritemai.com/byteshop/bic/getOrderCodePdf?size=100&template=bic_50_30'
UPLOAD_BIC_URL = 'https://web.slpzb.com/rest/v1/apiBiccode/'


class BicCode:
    """
    抓取抖音商城的 BIC 码 暂定每次抓取 1000 条，也就是说每次请求 100 条，循环请求 10 次
    1，下载 pdf 文件
    2，解析 pdf 文件，提取 BIC 码
    3，将 BIC 码上传到数据库
    4，提示用户上传成功
    """

    def __init__(self, cookie_str, user_shop_id: int):
        self.cookie = cookie_str
        self.user_shop_id = user_shop_id
        self.pdf_file_bytes = self.get_pdf_file()
        self.result_bic_list = self.parse_pdf_file()
        self.upload_bic_result = False
        self.upload_bic_code()
        self.get_pdf_signal_str = ''
        self.parse_pdf_signal_str = ''
        self.upload_bic_signal_str = ''


    def get_pdf_file(self):
        """
        下载 pdf 文件
        :return:
        """
        if not self.cookie:
            self.get_pdf_signal_str = '下载 bic_pdf 文件出错， cookie 为空'
            return None
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Cookie': self.cookie
        }
        try:
            response = requests.get(GET_BIC_URL, headers=headers)
            pdf_file_bytes = response.content
            file_type = filetype.guess(pdf_file_bytes)
            if file_type.extension == 'pdf':
                self.get_pdf_signal_str = '下载 bic_pdf 文件成功'
                return pdf_file_bytes
            else:
                self.get_pdf_signal_str = '下载 bic_pdf 文件出错，请求response文件不是 pdf 文件'
                return None
        except Exception as e:
            self.get_pdf_signal_str = '下载 bic_pdf 文件出错，请求未成功'
            return None

    def parse_pdf_file(self):
        """
        解析 pdf 文件，提取 BIC 码
        :return:
        """
        if not self.pdf_file_bytes:
            self.parse_pdf_signal_str = '解析 pdf 文件出错， pdf_file_bytes 为空'
            return None

        result_bic_list = []
        with io.BytesIO(self.pdf_file_bytes) as pdf_obj:
            pdf_file = pdfplumber.open(pdf_obj)
            for page in pdf_file.pages:
                # 理论上每页只有一个 BIC 码
                bic_code = page.extract_text().strip()
                if not bic_code:
                    self.parse_pdf_signal_str = '解析 pdf 文件出错，pdf 中有未解析成功的页面'
                    page.to_image().save('空内容' + str(page.page_number) + '.pdf')
                    continue

                # 校验 BIC 码，全为数字
                pattern = r'^\d+$'
                if not re.match(pattern, bic_code):
                    self.parse_pdf_signal_str = '解析 pdf 文件出错，pdf 中有非法内容页面（不全为数字）'
                    page.to_image().save('非法内容' + str(page.page_number) + '.pdf')
                    continue

                result_bic_list.append(bic_code)
            pdf_file.close()
        if not result_bic_list:
            self.parse_pdf_signal_str = '解析 pdf 文件出错，未提取到任何 BIC 码'
            return None
        if len(result_bic_list) != 100:
            self.parse_pdf_signal_str = '解析 pdf 文件出错，提取到的 BIC 码数量不为 100，可能存在问题'
        self.parse_pdf_signal_str = '解析 pdf 文件成功'
        return result_bic_list

    def upload_bic_code(self):
        """
        将 BIC 码上传到数据库
        :return:
        """
        if not self.result_bic_list:

            self.upload_bic_signal_str = '上传 BIC 码出错，result_bic_list 为空，无法上传'
            return False
        headers = {
            'Content-Type': 'application/json'
        }
        data = json.dumps(
            {
                'prefix_id': self.user_shop_id,
                'biccode': self.result_bic_list
            }
        )

        try:
            response = requests.post(UPLOAD_BIC_URL, headers=headers, data=data).json()
            if response.get('code') == 200 and response.get('msg') == '获取列表成功':
                self.upload_bic_signal_str = 'BIC 码上传成功'
                self.upload_bic_result = True
                return True
            else:
                self.upload_bic_signal_str = 'BIC 码上传失败, 服务器返回内容不匹配：' + str(response)
                return False
        except Exception as e:
            self.upload_bic_signal_str = 'BIC 码上传失败, 网络请求不成功'
            return False


if __name__ == '__main__':
    get_bic_obj = BicCode(user_shop_id=142)
