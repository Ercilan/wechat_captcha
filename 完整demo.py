# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/17 16:43
import random
import re
import time

import requests
from bs4 import BeautifulSoup

from main import classification_captcha


def print_html_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('body')
    if body:
        text = body.get_text()
        text = re.sub(r'\n+', '\n', text)
        # 把微信导航栏删除了
        text = re.sub(r"无障碍[\s\S]*?更多>>", "", text)
        print(text)


session_id = None
suid = None
a_uuid = None

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}
url = "https://weixin.sogou.com/weixin?p=01030402&query=%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5&type=2&ie=utf8"
for i in range(99):
    page = requests.get(url, headers=headers)
    # print(page.text)
    print_html_content(page.text)
    if "人民日报" not in page.text:
        print(page.headers)
        set_ck = page.headers.get('Set-Cookie')
        print(set_ck)
        suid = re.search(r"SUID=(.*?); ", set_ck)[1]
        session_id = re.search(r"PHPSESSID=(.*?); ", set_ck)[1]
        a_uuid = re.search(r"var auuid = \"(.*?)\"; ", page.text)[1]
        break

# 携带suid cookie下载验证码
headers['cookie'] = f"SUID={suid}; PHPSESSID={session_id}; IPLOC=CN3502; "
headers[
    'Referer'] = "https://weixin.sogou.com/antispider/?antip=wx_hb&from=%2Fweixin%3Fp%3D01030402%26query%3D%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5%26type%3D2%26ie%3Dutf8"
response = requests.get(
    f'https://weixin.sogou.com/antispider/util/seccode.php?tc={int(time.time() * 1000)}&antip=wx_hb',
    headers=headers)

with open(rf"test.jpeg", mode="wb") as f:
    f.write(response.content)

# 识别验证码
captcha = classification_captcha("test.jpeg")
print(f"识别到：{captcha}")
# time.sleep(3)
# # 请求 https://sogou.com/images/i.png 多设置了一个SUID  只携带 IPLOC=CN3501 cookie
# response = requests.get(f'https://weixin.sogou.com/antispider/util/seccode.php?tc={int(time.time() * 1000)}&antip=wx_hb',
#                         headers={
#                             "Referer": "https://weixin.sogou.com/",
#                             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
#                             "Cookie": "IPLOC=CN3501"
#                         })
# set_ck = response.headers.get('Set-Cookie')
# print(set_ck)
# suid2 = re.search(r"SUID=(.*?); ", set_ck)[1]
# headers['cookie'] = f"{headers['cookie']}SUID={suid2}"
# print(headers)

# 携带auuid 提交验证码  针对cookie解的
data = {
    # 验证码
    'c': captcha,
    # url 查询参数
    'r': '%2Fweixin%3Fp%3D01030402%26query%3D%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5%26type%3D2%26ie%3Dutf8',
    'p': 'wx_hb',
    'v': '5',
    'suuid': '',
    # 页面跳转后，html上面的js赋值的。与ck应该有绑定关系，请求验证码图片也会有更新对应关系
    'auuid': a_uuid,
}

print("提交验证中...")
response = requests.post('https://weixin.sogou.com/antispider/thank.php', headers=headers, data=data)
print(response.text)
if "解封成功" in response.text:
    data = response.json()
    sn_uid = data['id']
    cookie = f"SUV={time.time() * 1000}{random.randint(100, 999)}; SNUID={sn_uid};"
    headers['cookie'] = cookie
    page = requests.get(url, headers=headers)
    # print(page.text)
    print_html_content(page.text)

# todo 测试下ck与ip是否有关联，无关联则可以使用一些被封ip持续生成过验证码ck，提供外部使用
