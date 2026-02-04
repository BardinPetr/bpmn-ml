from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class OCRText:
    text: str
    bbox: Tuple[float, float, float, float]
    prob: float = 1.0


@dataclass
class OCRResult:
    lang: str = ""
    texts: List[OCRText] = field(default_factory=list)
