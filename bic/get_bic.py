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

    def __init__(self, cookie: str, user_shop_id: int):
        self.cookie = cookie
        self.user_shop_id = user_shop_id
        self.pdf_file_bytes = self.get_pdf_file()
        print('下载 pdf 文件完成')
        self.result_bic_list = self.parse_pdf_file()
        print('解析 pdf 文件完成', self.result_bic_list)
        self.upload_bic_result = self.upload_bic_code()
        print('上传 BIC 码完成')
        print('BIC 对象初始化完成')

    def get_pdf_file(self):
        """
        下载 pdf 文件
        :return:
        """
        if not self.cookie:
            print('下载 bic pdf 文件 cookie 为空')
            return None
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Cookie': self.cookie
        }
        try:
            response = requests.get(GET_BIC_URL, headers=headers)
            # print('----下载 pdf 的返回内容：----')
            # print('状态码：', response.status_code)
            # print('响应头：', response.headers)
            # print('响应内容：', response.content)
            # print('响应文本：', response.text)
            # print('----下载 pdf 的返回内容 结束：----')
            pdf_file_bytes = response.content
            file_type = filetype.guess(pdf_file_bytes)
            if file_type.extension == 'pdf':
                # self.pdf_file_bytes = pdf_file_bytes
                return pdf_file_bytes
            else:
                return None
        except Exception as e:
            print('下载 pdf 文件失败')
            print(e)
            return None

    def parse_pdf_file(self):
        """
        解析 pdf 文件，提取 BIC 码
        :return:
        """
        if not self.pdf_file_bytes:
            return None

        result_bic_list = []
        with io.BytesIO(self.pdf_file_bytes) as pdf_obj:
            pdf_file = pdfplumber.open(pdf_obj)
            for page in pdf_file.pages:
                # 理论上每页只有一个 BIC 码
                bic_code = page.extract_text().strip()
                if not bic_code:
                    print('当前页码：', page.page_number, '未提取到内容，已将文件保存到当前目录，文件名为：', page.page_number, '.pdf')
                    page.to_image().save('空内容' + str(page.page_number) + '.pdf')
                    continue

                # 校验 BIC 码，全为数字
                pattern = r'^\d+$'
                if not re.match(pattern, bic_code):
                    print('当前页码：', page.page_number, '提取到的内容不合法，已将文件保存到当前目录，文件名为：', page.page_number, '.pdf')
                    page.to_image().save('非法内容' + str(page.page_number) + '.pdf')
                    continue

                result_bic_list.append(bic_code)
            pdf_file.close()
        if not result_bic_list:
            print('未提取到 BIC 码, result_bic_list 为空')
            return None
        if len(result_bic_list) != 100:
            print('提取到的 BIC 码数量不为 100，可能存在问题')
        return result_bic_list

    def upload_bic_code(self):
        """
        将 BIC 码上传到数据库
        :return:
        """
        if not self.result_bic_list:
            print('BIC 码列表为空，无法上传')
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
                print('BIC 码上传成功')
                return True
            else:
                print('BIC 码上传失败')
                return False
        except Exception as e:
            print('BIC 码上传失败')
            print(e)
            return False


if __name__ == '__main__':
    a = 'umdata_=G21F4E11C9405016F86B12A6C9DD50C0DEFE558;uid=28a370a27367a289;Hm_lvt_b6520b076191ab4b36812da4c90f7a5e=1683885309,1683887832,1683887857,1683887873;MONITOR_WEB_ID=6b7f363c-5599-457b-b42d-5d84cb95b4c5;_tea_utm_cache_2018=undefined;login_info=%7B%22for_im_reply%22%3A%22dbaecb8ca864959930925e373da03767%22%7D;PHPSESSID=dbaecb8ca864959930925e373da03767;PHPSESSID_SS=dbaecb8ca864959930925e373da03767;d_ticket=e009511889e96b397177d72b1ebc135a6b6ca;msToken=FP0_xA7ssSu846_hSgH3XEfTTBMgE1NjNPDJTC7NhZzndcNBmtpZHMWEMK13HL4WjSqzAzeCgl1WN9gdk9rSL5WhvORPi1hU8DrI828qknVbxti6vLxABIPTngzv8w==;n_mh=m4oOMx7I0Ude2gfOJhmYCU4L6VNyq3ZZ85ECQjQTxDM;odin_tt=1f2ba535bd8e5421c69db0aa3cfd8d29a68af63b088a7b8da9bddf604452459698132d3d06a1494393b5527ceeafa6470c7733a07a1fe3c5d4fb3fc1bdc4c23a;passport_auth_status=2c57abeda55bc0c90958f90f1ccd6410%2Ca465b412eea4dfeef648877a477cbbf7;passport_auth_status_ss=2c57abeda55bc0c90958f90f1ccd6410%2Ca465b412eea4dfeef648877a477cbbf7;passport_csrf_token=d5dfaed139f762d89e52752768fad342;passport_csrf_token_default=d5dfaed139f762d89e52752768fad342;sessionid=c021699a084c5f871df33ce25f372c16;sessionid_ss=c021699a084c5f871df33ce25f372c16;sid_guard=c021699a084c5f871df33ce25f372c16%7C1683887913%7C5184000%7CTue%2C+11-Jul-2023+10%3A38%3A33+GMT;sid_tt=c021699a084c5f871df33ce25f372c16;sid_ucp_sso_v1=1.0.0-KGU0ZWMxMTZjZWU0MWMwMzkwN2ViYTBiYTYyYWY4NzBiMDQ1OTRkN2IKHwjo6rDo3cz8BBCkrviiBhiwISAMMKui96IGOAJA8QcaAmxmIiA5NDMxMTU5ODJkOTNkMjhjNDM2Yzg3ZDlhMmIyZTZlOQ;sid_ucp_v1=1.0.0-KDQxMDU0ZTFmYzhmYjY5MDlhNTg3YzdiYzRlMDIxMzk2NmQ2OTkyZTkKGQjo6rDo3cz8BBCprviiBhiwISAMOAJA8QcaAmhsIiBjMDIxNjk5YTA4NGM1Zjg3MWRmMzNjZTI1ZjM3MmMxNg;ssid_ucp_sso_v1=1.0.0-KGU0ZWMxMTZjZWU0MWMwMzkwN2ViYTBiYTYyYWY4NzBiMDQ1OTRkN2IKHwjo6rDo3cz8BBCkrviiBhiwISAMMKui96IGOAJA8QcaAmxmIiA5NDMxMTU5ODJkOTNkMjhjNDM2Yzg3ZDlhMmIyZTZlOQ;ssid_ucp_v1=1.0.0-KDQxMDU0ZTFmYzhmYjY5MDlhNTg3YzdiYzRlMDIxMzk2NmQ2OTkyZTkKGQjo6rDo3cz8BBCprviiBhiwISAMOAJA8QcaAmhsIiBjMDIxNjk5YTA4NGM1Zjg3MWRmMzNjZTI1ZjM3MmMxNg;sso_auth_status=bcfd7fa78686eafe4160dce7de869248;sso_auth_status_ss=bcfd7fa78686eafe4160dce7de869248;sso_uid_tt=a4704ab1b771f64b0eb24250d9d62db7;sso_uid_tt_ss=a4704ab1b771f64b0eb24250d9d62db7;store-region=cn-gd;store-region-src=uid;toutiao_sso_user=943115982d93d28c436c87d9a2b2e6e9;toutiao_sso_user_ss=943115982d93d28c436c87d9a2b2e6e9;ttwid=1%7C0eQROiAhszmF-g8a4twGGXVkktio4zZuCyXkYaYOQPo%7C1683887873%7C32a64d8958f53749a294f0123227620d6c9e06fae074b5f573eeb1cdfcc3d595;ucas_c0=CkEKBTEuMC4wEISIiqL84oWvZBjmJiCnieDM3Yz8AiiwITDo6rDo3cz8BECprviiBkip4rSlBlC8vL-m3v_PrmRYbxIUKDHqIEMYMRjaH5UmZ8kavaXjwXk;ucas_c0_ss=CkEKBTEuMC4wEISIiqL84oWvZBjmJiCnieDM3Yz8AiiwITDo6rDo3cz8BECprviiBkip4rSlBlC8vL-m3v_PrmRYbxIUKDHqIEMYMRjaH5UmZ8kavaXjwXk;ucas_sso_c0=CkEKBTEuMC4wEKOIg-Ch44WvZBjmJiCnieDM3Yz8AiiwITDo6rDo3cz8BECprviiBkip4rSlBlC8vL-m3v_PrmRYbxIULPM_IYiu1scU64OiyTt7wDQ-CGI;ucas_sso_c0_ss=CkEKBTEuMC4wEKOIg-Ch44WvZBjmJiCnieDM3Yz8AiiwITDo6rDo3cz8BECprviiBkip4rSlBlC8vL-m3v_PrmRYbxIULPM_IYiu1scU64OiyTt7wDQ-CGI;uid_tt=06ba7da9daf025aa992cf5559e61b19c;uid_tt_ss=06ba7da9daf025aa992cf5559e61b19c;fxg_guest_session=eyJhbGciOiJIUzI1NiIsInR5cCI6InR5cCJ9.eyJndWVzdF9pZCI6IkNnc0lBUkR6SEJnQklBRW9BUkkrQ2p5Z2FSd2JvaXpNQVErbjJ3aC9ETWwraXEzWU1hZnJkUXY4S1krR3VSbWZpZXR1NC81Ynd6ZEUvbzdNRGtwOFh2bWhGQ09PNlo5TVVyNXY5YjBhQUE9PSIsImlhdCI6MTY4Mzg3OTUwMCwibmJmIjoxNjgzODc5NTAwLCJleHAiOjE2ODUxNzU1MDB9.40940433ef271d8f2ec271bbca8e10b3a2929c00673ddd1d5d0e7eac8481de76;gd_random_410971=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODQ0OTAyNDIsImlhdCI6MTY4Mzg4NTQ0MiwibWF0Y2giOmZhbHNlLCJuYmYiOjE2ODM4ODU0NDIsInBhdGgiOiIvZmZhLW1pY3JvLWNvbmZpZy9hZC9wcm9tb3Rpb24tZ2FyIiwicGVyY2VudCI6MC4xMzE0Mjc0MjIwNjg3MzIzN30.Lr1R_AF42MCGJBT9tUgCdJUP6IDglwToiwY0gvf-pLg;gd_random_601503=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODQ0OTI3MTUsImlhdCI6MTY4Mzg4NzkxNSwibWF0Y2giOnRydWUsIm5iZiI6MTY4Mzg4NzkxNSwicGF0aCI6Ii9mZmEtbWljcm8tY29uZmlnL2hvbWVwYWdlIiwicGVyY2VudCI6MC4wMDA1MTU0MjcwNTU4NTM1NjZ9.OLJMsHETCeXXrpijjjR__1KsJqx-VE7iNcEFnk3_byQ;gd_worker_v2_random_391685=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2ODQ0OTAyNDQsImlhdCI6MTY4Mzg4NTQ0NCwibWF0Y2giOnRydWUsIm5iZiI6MTY4Mzg4NTQ0NCwicGF0aCI6Ii9mZmEtbWljcm8tY29uZmlnL2NvbXBhc3MiLCJwZXJjZW50IjowLjQzMjY1Mzk3OTIwMTU0MDd9.yRh7rSjxpAZ_Z5sGtZpuOXd3BdJ-JfMY5fOTJX59Mms;s_v_web_id=verify_lhkduexd_tWMMn9J9_SzwG_4HFj_8u6Q_ulthhOC0Ci3B;tt_scid=XSd3YQH2acVs8BEwa1rYasbF4Dg4kX-XTKNkVU2K4.rsKCBFLFyutQwPVaV2C7rf20ae;ttcid=dfa06710ecd84c44a1fd660f23b4ce6b13;x-jupiter-uuid=16838795009631868;BAIDUID=9709032B1589FAD1DB6D7A0719305DC9:FG=1;BAIDUID_BFESS=9709032B1589FAD1DB6D7A0719305DC9:FG=1;BA_HECTOR=0k00052g0h802h008h8hah671i5rv351n;BIDUPSID=9709032B1589FAD176E188F6F64F0C69;PSTM=1683881060;ZFY=6s53B7nJvGuO48C8NRzQv:AbiEBYhT2ZyC5EmEopUor8:C;HMACCOUNT=5A1C5BE385A67E4E;HMACCOUNT_BFESS=5A1C5BE385A67E4E;BD_UPN=12314753;_ga=GA1.2.945499583.1683530328;cna=+HDfHHlQ6mQCAd0FU0z41YM1;isg=BLy8yYeN9BIgtMBLxNCTeletjVputWDfJ-c9D5Y9yKeKYVzrvsUwbzJQQYEZKZg3;l=fBaGqwJlNhQZcBdJBOfwPurza77OSIRAguPzaNbMi9fP9wCH5ypFW1wBxrLMC3GNFsnyR37talRHBeYBquE-nxvOA8u21CMmnAsSbSf..;tfstk=cKw5BRmqtUYSVWBHE4s4Ckgoa8MFZhKsA_guVN92hSqhEXZ5iDpZ5Y00teh-nm1..;xlly_s=1;_uab_collina=168352230081207953446726;_umdata=G21F4E11C9405016F86B12A6C9DD50C0DEFE558;x5secdata=xd405c8ba72837772ff06657fb21f2f55bd75f04ab3dc44c871683861837a-717315356a1993109894abazc2aaa__bx__fourier.taobao.com%3A443%2Frp;Hm_lpvt_b6520b076191ab4b36812da4c90f7a5e=1683887873;Hm_ck_1683887872720=42;csrf_session_id=0b91962d9752b919524e913cd85742e9;MONITOR_DEVICE_ID=0b2d0686-f789-4ed2-8e03-95934d72ff67;uidpasaddaehruigqreajf=0;need_choose_shop=0;'
    shop_id = 142
    bic_obj = BicCode(cookie=a, user_shop_id=shop_id)
    print('最终结果：')
    print(bic_obj.result_bic_list)
    print(bic_obj.upload_bic_result)
