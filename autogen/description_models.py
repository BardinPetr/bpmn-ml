from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GBPMNElementType(str, Enum):
    TASK = "task"
    GATEWAY = "gateway"
    EVENT = "event"
    DATA = "data"


class GBPMNElement(BaseModel):
    """ Diagram element """
    id: str = Field(description="Unique identifier")
    name: str = Field(description="Name of element")
    type: GBPMNElementType = Field(description="type of BPMN process element")
    subtype: Optional[str] = Field(description="Subtype of element, meaning variations of events and gateways")
    actor_id: str = Field(description="Actor identifier referencing GBPMNActor")


class GBPMNFlow(BaseModel):
    """ Link between diagram elements """
    name: str
    source_id: str = Field(description="Unique identifier of link source element referencing GBPMNElement")
    target_id: str = Field(description="Unique identifier of link destination element referencing GBPMNElement")
    type: Optional[str] = Field(description='"sequence" flow or "message" flow')


class GBPMNProcess(BaseModel):
    """ Process """
    name: str
    elements: List[GBPMNElement]
    sequence_flows: List[GBPMNFlow]


class GBPMNActor(BaseModel):
    """ Process actor """
    name: str


class GBPMNDiagram(BaseModel):
    """ BPMN diagram """
    name: str
    processes: List[GBPMNProcess]
    message_flows: List[GBPMNFlow]
    actors: List[GBPMNActor]
