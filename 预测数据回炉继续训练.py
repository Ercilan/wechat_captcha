# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/16 13:46
import os
import traceback

from v8_predict_pt import cls

# 使用训练出来的模型，去预测，人工筛选出预测错误的图片，再附加一些正确的图片。丢回去重新训练，提高准确度
folder = "./to_find"
for f in os.listdir(folder):
    # classes.txt
    if len(f) == 11:
        continue

    p = os.path.join(folder, f)
    result = cls(p)
    try:
        os.rename(p, os.path.join(folder, "".join(result) + ".jpeg"))
        print("".join(result))
    except Exception as e:
        traceback.format_exc()
