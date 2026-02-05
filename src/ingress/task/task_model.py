from dataclasses import dataclass, field
from typing import List, Dict

from pydantic import BaseModel

from src.ingress.api.model import TaskResult, FileData, TaskStatus


class DiagramAnalyzeTaskRq(BaseModel):
    image: bytes


class DiagramAnalyzeTaskRs(BaseModel):
    success: bool = False
    description: str = ""
    files: List[FileData] = field(default_factory=list)
    info: Dict = field(default_factory=dict)

    def as_task_result(self) -> TaskResult:
        return TaskResult(
            status=TaskStatus.SUCCESS if self.success else TaskStatus.FAILURE,
            result=dict(description=self.description, **self.info),
            files=self.files
        )


@dataclass
class DiagramGenerateTaskRq:
    text: str


@dataclass
class DiagramGenerateTaskRs:
    success: bool = False
    bpmn_xml: str = ""
    image: bytes = b''
    visualization: List[bytes] = field(default_factory=list)

    def as_task_result(self) -> TaskResult:
        return TaskResult()
