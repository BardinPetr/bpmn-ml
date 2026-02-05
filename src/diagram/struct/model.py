from dataclasses import field
from enum import IntEnum
from typing import Tuple, List

from pydantic import BaseModel


class DetectorObjectType(IntEnum):
    EVENT_END = 0
    GATEWAY_EVENT_BASED = 1
    GATEWAY_EXCLUSIVE = 2
    GATEWAY_INCLUSIVE = 3
    MESSAGE_FLOW = 4
    EVENT_CATCH = 5
    EVENT_THROW = 6
    LANE = 7
    GATEWAY_PARALLEL = 8
    PROCESS = 9
    SEQUENCE_FLOW = 10
    EVENT_START = 11
    TASK = 12

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class DetectorLineType(IntEnum):
    MESSAGE = int(DetectorObjectType.MESSAGE_FLOW.value)
    SEQUENCE = int(DetectorObjectType.SEQUENCE_FLOW.value)

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
