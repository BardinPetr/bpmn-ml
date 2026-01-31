from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BPMNElement:
    id: str
    name: Optional[str] = None
    type: Optional[str] = None  # task, gateway, event, data
    subtype: Optional[str] = None  # subtype of type, example: for gateway it may be "exclusiveGateway"
    incoming: List[str] = field(default_factory=list)
    outgoing: List[str] = field(default_factory=list)
    bbox: Optional[Tuple[float, float, float, float]] = None  # x, y, w, h

    @property
    def bboxi(self):
        return [int(i) for i in self.bbox] if self.bbox else None

    @property
    def bboxc(self):
        if not self.bbox: return None
        x, y, w, h = self.bboxi
        return x + w // 2, y + h // 2


@dataclass_json
@dataclass
class BPMNFlow:
    id: str
    source_ref: str
    target_ref: str
    type: Optional[str] = None  # "sequence" flow / "message" flow
    name: Optional[str] = None  # human readable name for that link
    expression: Optional[str] = None  # human readable note / conditional expression for that link
    line: Optional[Tuple[float, float, float, float]] = None  # (x0,y0,x1,y1)


@dataclass_json
@dataclass
class BPMNProcess:
    id: str
    name: str
    participant_name: Optional[str] = None  # from colaboration info
    elements: List[BPMNElement] = field(default_factory=list)
    flows: List[BPMNmeFlow] = field(default_factory=list)


@dataclass_json
@dataclass
class BPMNDiagram:
    processes: List[BPMNProcess]
    interprocess_flows: List[BPMNFlow] = field(default_factory=list)  # for colaborations, messageflows and etc

    def save(self, path: str):
        with open(path, "w") as f:
            f.write(self.to_json())


def bpmd_classes_from_json(jsontext: str) -> BPMNDiagram:
    return BPMNDiagram.schema().loads(jsontext)
