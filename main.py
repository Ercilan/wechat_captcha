import time

import cv2.dnn
import numpy as np

onnx_model = f"wc.onnx"
CLASSES = ["B", "H", "M", "2", "8", "7", "4", "S", "A", "K", "5", "3", "T", "E", "D", "6", "P", "X", "V", "C", "Y", "F",
           "R", "J"]
SHAPE = [320, 320]
# PyTorch: starting from 'wc.pt' with input shape (1, 3, 320, 320) BCHW and output shape(s) (1, 28, 2100) (21.4 MB)

load_start = time.perf_counter()
model: cv2.dnn.Net = cv2.dnn.readNetFromONNX(onnx_model)
print(f"模型加载耗时: {time.perf_counter() - load_start:.2f}s")

colors = np.random.uniform(0, 255, size=(len(CLASSES), 3))


def draw_bounding_box(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = f'{CLASSES[class_id]} ({confidence:.2f})'
    color = colors[class_id]
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
    cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def detect_v8(input_image, score_threshold=0.25):
    original_image: np.ndarray = cv2.imread(input_image)
    [height, width, _] = original_image.shape
    length = max((height, width))
    image = np.zeros((length, length, 3), np.uint8)
    image[0:height, 0:width] = original_image
    scale = length / SHAPE[0]

    blob = cv2.dnn.blobFromImage(image, scalefactor=1 / 255, size=SHAPE, swapRB=True)
    model.setInput(blob)
    outputs = model.forward()

    outputs = np.array([cv2.transpose(outputs[0])])
    rows = outputs.shape[1]

    boxes = []
    scores = []
    class_ids = []

    for i in range(rows):
        classes_scores = outputs[0][i][4:]
        (minScore, maxScore, minClassLoc, (x, maxClassIndex)) = cv2.minMaxLoc(classes_scores)
        if maxScore >= score_threshold:
            box = [
                outputs[0][i][0] - (0.5 * outputs[0][i][2]), outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                outputs[0][i][2], outputs[0][i][3]]
            boxes.append(box)
            scores.append(maxScore)
            class_ids.append(maxClassIndex)

    result_boxes = cv2.dnn.NMSBoxes(boxes, scores, score_threshold, 0.45, 0.5)

    detections = []
    for i in range(len(result_boxes)):
        index = result_boxes[i]
        box = boxes[index]
        detection = {
            'class_id': class_ids[index],
            'class_name': CLASSES[class_ids[index]],
            'confidence': scores[index],
            'box': box,
            'scale': scale}
        detections.append(detection)
        # 绘图
        # draw_bounding_box(original_image, class_ids[index], scores[index], round(box[0] * scale), round(box[1] * scale),
        #                   round((box[0] + box[2]) * scale), round((box[1] + box[3]) * scale))

    # cv2.imshow('image', original_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return detections


def classification_captcha(input_image):
    res = detect_v8(input_image, score_threshold=0.15)
    if len(res) > 6:
        sorted_data = sorted(res, key=lambda x: x['confidence'], reverse=True)
        res = sorted_data[:6]
    sorted_indexes = [index for index, value in sorted(enumerate(res), key=lambda x: x[1]['box'][0])]
    return "".join([word for index in sorted_indexes for word in res[index]['class_name']])


if __name__ == '__main__':
    start = time.perf_counter()
    print(classification_captcha(r"to_add\RP2EM7.jpeg"))
    print(classification_captcha(r"to_add\5ESA48.jpeg"))
    print(classification_captcha(r"to_add\4S475B.jpeg"))
    print(classification_captcha(r"colab\train\images\F326MH.jpeg"))
    print(classification_captcha(r"colab\train\images\J7EBD3.jpeg"))
    print(classification_captcha(r"colab\train\images\4585M7.jpeg"))
    print(classification_captcha(r"colab\val\images\D75B2A.jpeg"))
    print(f"检测耗时：{time.perf_counter() - start:.2f}s")
