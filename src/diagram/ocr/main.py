import asyncio
import string
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict

import cv2
import numpy as np
from easyocr import Reader
from ray import serve
from rich import print

from src.diagram.ocr.model import OCROutput, OCRText

ru_alpha = ''.join(chr(i) for i in range(ord('а'), ord('я')))
alphabet = dict(en=string.ascii_letters, ru=ru_alpha)


def choose_lang(variants: Dict[str, OCROutput]) -> str:
    res = {}
    for l, data in variants.items():
        txt = ' '.join(j.text for j in data.texts)
        orig_len = len(txt)
        l_txt = list(filter(lambda x: x.lower() in alphabet[l], txt))
        res[l] = len(l_txt) / orig_len
    return max(res.items(), key=lambda x: x[1])[0]


@serve.deployment(ray_actor_options={"num_cpus": 0.1, "num_gpus": 0.2})
class OCRProcess:
    def __init__(self, launch_config=None, run_config=None):
        self.__launch_config = launch_config or dict(gpu=True)
        self.__run_config = run_config or dict(
            paragraph=True,
            # rotation_info=[90]
        )
        self.__readers = dict(
            ru=Reader(['ru'], **self.__launch_config),
            en=Reader(['en'], **self.__launch_config)
        )
        print("[OCR] loading")
        for l, i in self.__readers.items():
            try:
                print(f"[OCR] loading {l}")
                i.readtext(np.zeros((1920, 1080, 3), np.uint8))
            except:
                pass
        print("[OCR] loading done")
        self.__exec = ThreadPoolExecutor(2)

    def __call__(self, image, prefer_lang=None) -> OCROutput:
        langs = [prefer_lang] if prefer_lang else self.__readers.keys()
        variants = self.__exec.map(lambda l: self.solve(l, image), langs)
        variants = dict(zip(langs, variants))
        lang = choose_lang(variants)
        return variants[lang]

    def solve(self, lang, image) -> OCROutput:
        print(f"[OCR] start for {lang}")
        ts = time.time()
        if not (rd := self.__readers.get(lang, None)): return OCROutput()
        result = rd.readtext(image, **self.__run_config)
        result = OCROutput(
            lang=lang,
            texts=[OCRText(text=text, bbox=tuple(int(j) for j in [*pa, *pb])) for (pa, _, pb, _), text, *_ in result],
        )
        ts = time.time() - ts
        print(f"[OCR] done={len(result.texts)} time {ts * 1000:.0f}ms")
        return result


app = OCRProcess.bind()

# async def main():
#     app = OCRProcess()
#     print("1@")
#     im = cv2.imread(
#         "/home/petr/projects/mltests/dataset/out_image/0e5e7c91e225dd48e344d35c90e62fa7e867890268dd94df219d8b2eff0356aa.0.jpg")
#     while True:
#         print("###")
#         app(im)
#
#
# asyncio.run(main())
