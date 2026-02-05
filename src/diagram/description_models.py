from enum import StrEnum
from typing import List, Tuple, Optional, Dict

from pydantic import BaseModel, Field


class GBPMNFlowType(StrEnum):
    MESSAGE = "message"
    SEQUENCE = "sequence"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class GBPMNElementType(StrEnum):
    TASK = "task"
    GATEWAY = "gateway"
    EVENT_START = "startEvent"
    EVENT_END = "endEvent"
    EVENT_CATCH = "intermediateCatchEvent"
    EVENT_THROW = "intermediateThrowEvent"
    VIRT_LANE = "__lane"
    VIRT_PROC = "__proc"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class GBPMNElementSubType(StrEnum):
    GATEWAY_EXCLUSIVE = "exclusiveGateway"
    GATEWAY_INCLUSIVE = "inclusiveGateway"
    GATEWAY_PARALLEL = "parallelGateway"
    GATEWAY_EVENT = "eventBasedGateway"

    EVENT_OTHER = "event"
    EVENT_MESSAGE = "messageEventDefinition"
    EVENT_TIMER = "timerEventDefinition"
    EVENT_ERROR = "errorEventDefinition"
    EVENT_CONDITIONAL = "conditionalEventDefinition"

    TASK_OTHER = "task"

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class GBPMNElement(BaseModel):
    id: str
    label: Optional[str] = None
    type: Optional[GBPMNElementType] = None
    subtype: Optional[GBPMNElementSubType] = None
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)


class GBPMNFlow(BaseModel):
    id: str
    label: Optional[str] = None
    type: Optional[GBPMNFlowType] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    line: List[Tuple[int, int]] = Field(default_factory=list)


class GBPMNLaneElement(GBPMNElement):
    process_id: str
    nested_ids: List[str] = Field(default_factory=list)


class GBPMNProcessElement(GBPMNElement):
    lanes_ids: List[str] = Field(default_factory=list)


class DiagramContents(BaseModel):
    elements: List[GBPMNElement]
    links: List[GBPMNFlow]

    def drop(self, uid):
        self.elements = [i for i in self.elements if i.id != uid]

    def add(self, element):
        self.elements.append(element)


""""""


class GBPMNLane(BaseModel):
    id: str
    label: Optional[str] = None
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)
    objects: List[GBPMNElement] = Field(default_factory=list)


class GBPMNProcess(BaseModel):
    id: str
    label: Optional[str] = None
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)
    lanes: List[GBPMNLane] = Field(default_factory=list)


class GBPMNDiagram(BaseModel):
    processes: List[GBPMNProcess] = Field(default_factory=list)
    flows: Dict[Tuple[str, str], GBPMNFlow] = Field(default_factory=dict)
    objects: Dict[str, GBPMNElement] = Field(default_factory=dict)
