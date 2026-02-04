from dataclasses import dataclass, field
from enum import IntEnum
from typing import Tuple, List


@dataclass
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

@dataclass
class DetectorLineType(IntEnum):
    MESSAGE = 2
    SEQUENCE = 5

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

@dataclass
class DetectorObject:
    type: DetectorObjectType
    bbox: Tuple[float, float, float, float]


@dataclass
class DetectorLine:
    type: DetectorLineType
    line: List[Tuple[float, float]]


@dataclass
class DetectorOutput:
    objects: List[DetectorObject] = field(default_factory=list)
    lines: List[DetectorLine] = field(default_factory=list)
