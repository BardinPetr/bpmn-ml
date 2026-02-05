from dataclasses import field
from enum import IntEnum
from typing import Tuple, List

from pydantic import BaseModel


class DetectorObjectType(IntEnum):
    EVENT = 0
    GATEWAY = 1
    MESSAGE_FLOW = 2
    LANE = 3
    PROCESS = 4
    SEQUENCE_FLOW = 5
    TASK = 6

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class DetectorLineType(IntEnum):
    MESSAGE = 2
    SEQUENCE = 5

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class DetectorObject(BaseModel):
    type: DetectorObjectType
    bbox: Tuple[int, int, int, int]


class DetectorLine(BaseModel):
    type: DetectorLineType
    line: List[Tuple[int, int]]


class DetectorOutput(BaseModel):
    objects: List[DetectorObject] = field(default_factory=list)
    lines: List[DetectorLine] = field(default_factory=list)
