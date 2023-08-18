# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/16 11:04
from typing import Union

from ultralytics import YOLO

# pt版的模型预测使用
model = YOLO('wc.pt')


def cls(img: Union[list, str], conf=0):
    # 置信度设为0，使用max_det选出最大6个
    # results = model(img)
    results = model.predict(img, save=True, imgsz=320, conf=conf, max_det=6)

    for result in results:
        boxes = result.boxes  # Boxes object for bbox outputs
        masks = result.masks  # Masks object for segmentation masks outputs
        keypoints = result.keypoints  # Keypoints object for pose outputs
        probs = result.probs  # Probs object for classification outputs
        # print(result.names)
        # print(f"{boxes}-{masks}-{keypoints}-{probs}")
        locs = [word_loc[0] for word_loc in boxes.xywh]
        sorted_indexes = [index for index, value in sorted(enumerate(locs), key=lambda x: x[1])]
        classes = boxes.cls.tolist()
        labels = [result.names[int(classes[index])] for index in sorted_indexes]
        print("验证码识别结果是：" + " ".join(labels))
        return labels

