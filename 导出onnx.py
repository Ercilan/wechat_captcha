# coding=utf-8
# @Author: 二次蓝
# @Created at 2023/8/17 13:49

from ultralytics import YOLO

# Load a model
model = YOLO('wc.pt')

# Export the model
model.export(format='onnx', simplify=True, opset=12)
