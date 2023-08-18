# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/15 10:02
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from tqdm import tqdm

headers = {
    # 'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    # 'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Connection': 'keep-alive',
    # 'Cookie': 'IPLOC=CN3502; SUID=5C621C757450A00A0000000064C8A5C3; cuid=AAEZc2VmRgAAAAqgIyWGnQEASQU=; SUV=1690871242166726; ABTEST=3|1690871248|v1; SNUID=EDFD5914A4A5A648F929B8F4A4DF4B1C; PHPSESSID=kd6bqalg0380bag3mn8l2ovip7',
    'Referer': 'https://weixin.sogou.com/antispider/?antip=wx_hb&from=%2Fweixin%3Fp%3D01030402%26query%3D%E4%BA%BA%E6%B0%91%E6%97%A5%E6%8A%A5%26type%3D2%26ie%3Dutf8',
    # 'Sec-Fetch-Dest': 'image',
    # 'Sec-Fetch-Mode': 'no-cors',
    # 'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    # 'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    # 'sec-ch-ua-mobile': '?0',
    # 'sec-ch-ua-platform': '"Windows"',
}

params = {
    'tc': '1692064230073',
}


def down_pic(save_dir):
    response = requests.get('https://weixin.sogou.com/antispider/util/seccode.php', params=params, headers=headers)

    with open(rf"{save_dir}/{round(time.time() * 1000)}.jpeg", mode="wb") as f:
    # with open(rf"{save_dir}/1.jpeg", mode="wb") as f:
        f.write(response.content)


def download_images(num, save_dir, num_threads=5):
    os.makedirs(save_dir, exist_ok=True)
    with ThreadPoolExecutor(max_workers=num_threads) as executor, \
            tqdm(total=num) as progress_bar:
        futures = []
        for i in range(num):
            futures.append(executor.submit(down_pic, save_dir))
        for f in as_completed(futures):
            progress_bar.update(1)


if __name__ == '__main__':
    print(round(time.time() * 1000))
    download_images(num=20, save_dir="./test", num_threads=5)
