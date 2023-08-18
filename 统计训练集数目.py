# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/16 9:37
import os

with open(r"classes.txt") as f:
    words = f.read().rstrip()

words = [word.strip() for word in words.split("\n")]

count = {}
folder = "./colab/train/labels"
# folder = "./colab/val/labels"
for f in os.listdir(folder):
    if f == "classes.txt":
        continue
    p = os.path.join(folder, f)
    with open(p, mode="rt") as f_:
        for line in f_.readlines():
            line = line.strip()
            items = line.split(" ")
            label = items[0]
            count[label] = count.get(label, 0) + 1

print(count)
count_show = {}
# count 转 label 文本
for k, v in count.items():
    count_show[words[int(k)]] = v

print(count_show)
