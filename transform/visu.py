import json

import numpy as np


class JSON_Parser:
    def __init__(self):
        self.bbox_list = list()
        self.type_list = list()

    def set_bbox(self, d: dict):
        if not isinstance(d, dict):
            return
        if "bbox" in d.keys() and d["bbox"] is not None:
            self.bbox_list.append(d["bbox"])
            self.type_list.append(d["type"])
        for value in d.values():
            if isinstance(value, dict):
                self.set_bbox(value)
            if isinstance(value, list):
                for i in value:
                    self.set_bbox(i)


def draw_rect_with_text(
        img,
        x,
        y,
        width,
        height,
        text="test",
        rect_color=(0, 255, 0),
        text_color=(255, 0, 255),
        thickness=2,
):
    # Draw rectangle (top-left to bottom-right corners)
    pt1 = (x, y)
    pt2 = (x + width, y + height)
    cv2.rectangle(img, pt1, pt2, rect_color, thickness)

    # Get text size for centering
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]

    # Center text position
    text_x = x + (width) // 2
    text_y = y + (height) // 2

    # Draw text
    img = cv2.putText(
        img, text, (text_x, text_y), font, font_scale, text_color, font_thickness
    )


def read_item(fp):
    img = cv2.imread(fp.replace("out_label", "out_image").replace(".json", ".jpg"))
    with open(fp) as f:
        labels = json.load(f)

    j_parser = JSON_Parser()
    j_parser.set_bbox(labels)

    return img, j_parser.bbox_list, j_parser.type_list


import os
import cv2

dataset = ""

root = ""
dataset_path = os.path.join(root, "out_label")

from tqdm import tqdm

full_type_list = list()
embeddings = list()
name_list = list()

st = 600
ordfiles = sorted(os.listdir(dataset_path))
t = tqdm(total=len(ordfiles))
t.update(st)

while st < len(ordfiles):
    name = ordfiles[st]
    tmp, bbox_list, type_list = read_item(dataset_path + "/" + name)

    for bbox, type in zip(bbox_list, type_list):
        x, y, width, height = [int(i) for i in bbox]
        sub_img = tmp[y: y + height, x: x + width]

    for bbox, type in zip(bbox_list, type_list):
        x, y, width, height = [int(i) for i in bbox]
        draw_rect_with_text(tmp, x, y, width, height, type)

    cv2.imshow("res", tmp)
    k = cv2.waitKey(150)
    if k == ord("q"):
        break
    elif k == ord("a"):
        st += 1
        t.update()
    elif k == ord("r"):
        st -= 1
        continue
    elif k == ord("d"):
        st += 1
        t.update()
        with open("del.list", "a") as fa:
            fa.write(name + "\n")
    else:
        st += 1
        t.update()

full_type_list = np.array(full_type_list)
embeddings = np.array(embeddings)
name_list = np.array(name_list)

cv2.destroyAllWindows()
