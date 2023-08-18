# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/17 10:41
import os
import random
from pathlib import Path

"""附加准备再训练的数据，但没想到新增的数据 R J 标签 classes.txt 里反了，，，也不知为啥，补救一下"""

# 1. 统一命名，把to_add里面一些当初没有识别的图片重命名，通过名称区分两批数据（起始用时间修改就可以了）
base_folder = Path("failed/train/")
for f in os.listdir(base_folder / "images"):
    if len(f) != 18:
        continue
    p = base_folder / "images" / f
    print(p)
    # 重命名为6长度的（不包括后缀）
    new_base_name = f"a_{random.randint(1000, 9999)}"
    new_name = f"{new_base_name}.jpeg"
    os.rename(p, p.with_name(new_name))
    os.rename(base_folder / "labels" / (p.stem + ".txt"), base_folder / "labels" / (new_base_name + ".txt"))


# 2. 验证这一百张长度为11都是新增的标签翻了的
# num = 0
# p = r"F:\PyProject\wechat_captcha\colab\train\images"
# file_paths = [os.path.join(p, filename) for filename in os.listdir(p)]
# sorted_files = sorted(file_paths, key=lambda x: os.path.getmtime(x))
# for f in file_paths:
#     # print(f)
#     if len(os.path.basename(f)) == 11:
#         num += 1
#         if not os.path.exists(base_folder / "images" / os.path.basename(f)):
#             raise ValueError("有命名不是这种规律的图片哦")
# print(num)

# 3. 手动替换classes.txt，然后用这步修改标签，替换补充数据的23、22标记
folder_path = r"F:\PyProject\wechat_captcha\colab\train\labels"
folder_path = r"/failed\train\labels"
folder_path = r"/failed\val\labels"

for filename in os.listdir(folder_path):
    if filename.endswith(".txt") and len(filename) == 10:
        file_path = os.path.join(folder_path, filename)
        lines = []

        with open(file_path, "r") as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) > 0:
                    if int(parts[0]) == 23:
                        parts[0] = "22"
                    elif int(parts[0]) == 22:
                        parts[0] = "23"
                lines.append(" ".join(parts))

        with open(file_path, "w") as file:
            file.write("\n".join(lines))
