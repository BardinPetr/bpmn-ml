import os.path
import pathlib
import time

import cv2
import numpy as np
from ray import serve
from ultralytics import YOLO

from src.diagram.struct.model import DetectorOutput, DetectorLine, DetectorLineType, DetectorObject, DetectorObjectType


def convert(dets) -> DetectorOutput:
    result = DetectorOutput()
    dets = dets[0]
    h, w = dets.orig_shape
    bbox_list, lines_list = dets.boxes.data.cpu().numpy().tolist(), dets.keypoints.data.cpu().numpy().tolist()
    for (bbox_x, bbox_y, bbox_x2, bbox_y2, koef, cls), line in zip(bbox_list, lines_list):
        classifier = int(cls) % len(DetectorObjectType)
        line_out = []
        line = [line[0]] + line[1:][::-1]
        for x, y, v in line:
            x, y = int(x), int(y)
            if v < 0.2: continue
            line_out.append((int(x), int(y)))
            # line_out.append((x / w, y / h))
        if line_out:
            result.lines.append(DetectorLine(type=DetectorLineType(classifier), line=line_out))
        else:
            bbox = (bbox_x, bbox_y, bbox_x2, bbox_y2)
            result.objects.append(DetectorObject(type=DetectorObjectType(classifier), bbox=tuple(int(k) for k in bbox)))
            # result.objects.append(DetectorObject(DetectorObjectType(classifier), (bbox_x / w, bbox_y/h, bbox_x2 / w, bbox_y2/h)))
    return result


@serve.deployment(ray_actor_options={"num_cpus": 0.5})
class ObjectLineDetector:
    def __init__(self):
        model_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "v2.onnx")
        self.__model = YOLO(model_path, task='pose')
        print("[DET] loading")
        try:
            self.__model(np.array([]))
        except:
            pass
        print("[DET] loading done")

    def __call__(self, img) -> DetectorOutput:
        img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
        ts = time.time()
        result = self.__model(img, conf=0.2, iou=0.6, imgsz=1280, device='cpu')
        dt = time.time() - ts
        print(f"[DET] time: {dt * 1000:.0f}ms")
        return convert(result)

