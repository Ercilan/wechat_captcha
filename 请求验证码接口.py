# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/16 13:56

import requests

cookies = {
    'IPLOC': 'CN3502',
    'SUID': '5C621C757450A00A0000000064C8A5C3',
    'cuid': 'AAEZc2VmRgAAAAqgIyWGnQEASQU=',
    'SUV': '1690871242166726',
    'ABTEST': '3|1690871248|v1',
    'SNUID': 'EDFD5914A4A5A648F929B8F4A4DF4B1C',
    'PHPSESSID': 'cr7p6ocg1ua3f75c9o0o7i4sq0',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'Cookie': 'IPLOC=CN3502; SUID=5C621C757450A00A0000000064C8A5C3; cuid=AAEZc2VmRgAAAAqgIyWGnQEASQU=; SUV=1690871242166726; ABTEST=3|1690871248|v1; SNUID=EDFD5914A4A5A648F929B8F4A4DF4B1C; PHPSESSID=cr7p6ocg1ua3f75c9o0o7i4sq0',
    'Origin': 'https://weixin.sogou.com',
    'Referer': 'https://weixin.sogou.com/antispider/?from=%2fweixin%3Fp%3d01030402%26query%3d%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5%26type%3d2%26ie%3dutf8&antip=wx_hb',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

data = {
    # 验证码
    'c': 'hr58eb',
    # url 查询参数
    'r': '%2Fweixin%3Fp%3D01030402%26query%3D%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5%26type%3D2%26ie%3Dutf8',
    'p': 'wx_hb',
    'v': '5',
    'suuid': '',
    # 页面跳转后，html上面的js赋值的。与ck应该有绑定关系，请求验证码图片也会有更新对应关系
    'auuid': 'ea2bf3e5-b624-407e-9c70-d1221bc870de',
}

response = requests.post('https://weixin.sogou.com/antispider/thank.php', cookies=cookies, headers=headers, data=data)
print(response.text)
