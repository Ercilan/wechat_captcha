# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/18 13:57
import os
from PIL import Image
import matplotlib.pyplot as plt

from main import classification_captcha

folder_path = "test/"

image_files = [f for f in os.listdir(folder_path) if f.endswith(".jpeg")]

fig = plt.figure(figsize=(8, 7))

max_images_per_row = 3

for i, image_file in enumerate(image_files):
    image_path = os.path.join(folder_path, image_file)
    image = Image.open(image_path)

    ax = fig.add_subplot((len(image_files) - 1) // max_images_per_row + 1, max_images_per_row, i + 1)

    ax.autoscale(enable=True, tight=True)
    ax.imshow(image)

    captcha = classification_captcha(image_path)
    ax.set_title(captcha)

    ax.axis("off")
plt.tight_layout()
plt.savefig("demo.png")
plt.show()
