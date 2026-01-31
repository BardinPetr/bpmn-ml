import hashlib
import os
from typing import Tuple, List


def xhash(x: str) -> str:
    m = hashlib.sha256()
    m.update(x.encode("utf-8"))
    return m.hexdigest()

