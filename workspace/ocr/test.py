import time
from pprint import pprint

import cv2
import numpy as np

from datasetload import load_dataset
from transform.visu import draw_rect_with_text

rus_ds = [
    "0f4c1460f8077f81230114b6f80e47b418c8f726724924d7409d96302b14992a",
    "042b4c494cf76f0766cc5dce950fd40ae543f396c6bfe16628920027aade322e",
    "6c687fa68107d786a7e386a7e11f32a2789457f7d5a82e0fdacdfb32f432bf27",
    "0f4c1460f8077f81230114b6f80e47b418c8f726724924d7409d96302b14992a",
    "922834786e1189e034d8d4c2ac23a18713f6cc4e02982d77740e2603bade4c40",
    "415b4d5434e47c10cab4056ac4335dce2f9cfcb4ae286a84a1f162c50d6c6cdb",
    "81b4cbf1283147611d05839e6a6c8078aec6c40e40efa2c29f217a38edb46a97",
    "4ac06927a538b76cc9a75c3779dc6ea85ac6b23cf8c8e6a7fac73c20fcb79fc4",
]

data = load_dataset("../dataset")
data = [
    (i['image'], i['textdetect'], i['diagram'])
    for i in data
    if i['hash'] in rus_ds
]


def pi(x):
    return [int(i) for i in x]


d = data[1]
# fimg = "/home/petr/Pictures/Screenshots/Screenshot_20260201_172527.png"
# fimg = "/home/petr/projects/mltests/demos/ph1.jpg"
fimg = d[0]
dg = d[2]
print(fimg)

x = cv2.imread(fimg)
# x = cv2.resize(x, (int(x.shape[1]//1.2), int(x.shape[0]//1.2)))
x = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
x = cv2.fastNlMeansDenoising(x, None, h=20, templateWindowSize=1, searchWindowSize=11)
# x = cv2.bilateralFilter(x, 9, 80, 10)
x = cv2.adaptiveThreshold(x, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 7, 3)
# x = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(x)
# kernel_sharpen = np.array([[-1, -1, -1],
#                            [-1, 9, -1],
#                            [-1, -1, -1]])
# x = cv2.filter2D(x, -1, kernel_sharpen)

cv2.imwrite("inn.png", x)
img = cv2.imread("inn.png")


"""
from paddleocr import PaddleOCR
ocr = PaddleOCR(
    lang="ru",
    # ocr_version="PP-OCRv5",
    text_detection_model_name="PP-OCRv5_server_det",
    text_recognition_model_name="cyrillic_PP-OCRv5_server_rec",
    use_doc_unwarping=False,
    use_textline_orientation=True,
    use_doc_orientation_classify = False
)

t = time.time()
result = ocr.ocr("inn.png", det=True, rec=False, cls=True, bin=True)
print(time.time() - t)
pprint(result)

for i in result[0]:
    # pts, (n, _) = i
    pts = i
    n= ""
    draw_rect_with_text(img, int(pts[0][0]), int(pts[0][1]), 10, 10, n)
    cv2.line(img, (int(pts[0][0]), int(pts[0][1])), (int(pts[2][0]), int(pts[2][1])), (0, 0, 255), 1)

import easyocr

reader = easyocr.Reader(['ru'])

t = time.time()
result = reader.readtext(
    'inn.png',
    # decoder='beamsearch',
    # beamWidth=2,
    batch_size=1,
    paragraph=True
)
print(time.time() - t)

pprint(result)


for i in result:
    ((px,py), _, _, _), n = i
    draw_rect_with_text(img, px-10, py-10, 10, 10, n)

"""


for i in dg.processes:
    # for j in i.flows:
    #     for k1, k2 in zip(j.lines[:-1], j.lines[1:]):
    #         cv2.line(img, k1, k2, (0, 0, 255), 2)

    for j in i.lanes:
        x, y, w, h = j.bbox
        cv2.line(img, pi((x, y)), pi((x+w, y+h)), (255, 0, 0), 2)

    x, y, w, h = i.bbox
    cv2.line(img, pi((x, y)), pi((x+w, y+h)), (0, 255, 0), 2)

for j in dg.interprocess_flows:
    for k1, k2 in zip(j.lines[:-1], j.lines[1:]):
        cv2.line(img, k1, k2, (0, 0, 255), 2)
        

cv2.imwrite("test.jpg", img)
