import asyncio
import string
import time
from typing import Dict

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


@serve.deployment(ray_actor_options={"num_cpus": 0.5})
class OCRProcess:

    def __init__(self, launch_config=None, run_config=None):
        self.__launch_config = launch_config or dict(gpu=False)
        self.__run_config = run_config or dict(
            paragraph=True
        )
        self.__readers = dict(
            ru=Reader(['ru'], **self.__launch_config),
            en=Reader(['en'], **self.__launch_config)
        )

    async def __call__(self, image) -> OCROutput:
        langs = self.__readers.keys()
        variants = await asyncio.gather(*[self.solve(lang, image) for lang in langs])
        variants = dict(zip(langs, variants))
        lang = choose_lang(variants)
        return variants[lang]

    async def solve(self, lang, image) -> OCROutput:
        ts = time.time()
        if not (rd := self.__readers.get(lang, None)): return OCROutput()
        result = rd.readtext(image, **self.__run_config)
        result = OCROutput(
            lang=lang,
            texts=[OCRText(text=text, bbox=tuple(int(j) for j in [*pa, *pb])) for (pa, _, pb, _), text, *_ in result],
        )
        ts = time.time() - ts
        print(f"[OCR] done={len(result.texts)} ts{ts * 1000:.0f}ms")
        return result


app = OCRProcess.bind()
