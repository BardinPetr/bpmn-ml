from dataclasses import field
from typing import List, Tuple

from pydantic import BaseModel


class OCRText(BaseModel):
    text: str
    bbox: Tuple[int, int, int, int]
    prob: float = 1.0


class OCROutput(BaseModel):
    lang: str = ""
    texts: List[OCRText] = field(default_factory=list)
