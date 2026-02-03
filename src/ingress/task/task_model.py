from dataclasses import dataclass, field
from typing import List

from src.ingress.api.model import TaskResult, FileData, TaskStatus, TaskDataT2D, TaskDataD2T


class DiagramAnalyzeTaskRq:
    image: str


@dataclass
class DiagramAnalyzeTaskRs:
    success: bool = False
    description: str = ""
    bpmn_xml: str = ""
    visualization: List[bytes] = field(default_factory=list)

    def as_task_result(self) -> TaskResult:
        return TaskResult(
            status=TaskStatus.SUCCESS if self.success else TaskStatus.FAILURE,
            result=dict(description=self.description),
            files=[
                FileData(data=self.bpmn_xml.encode(), content_type="application/xml", filename="bpmn.xml"),
                *(FileData(data=v, content_type="image/png", filename=f"out.{i}.png") for i, v in
                  enumerate(self.visualization))
            ]
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

