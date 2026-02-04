from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class SubsystemType(str, Enum):
    DIAG2TXT = "d2t"
    TXT2DIAG = "t2d"


""" SUBMIT """


class TaskDataT2D(BaseModel):
    text: str
    props: Optional[Dict] = None


class TaskDataD2T(BaseModel):
    image: 'FileData'
    props: Dict


class SubmitRs(BaseModel):
    request_id: str = ""
    status: TaskStatus = TaskStatus.FAILURE
    total_tasks: int = 0


class InternalTaskBlock(BaseModel):
    request_id: str = ""
    tasks: List[TaskDataT2D | TaskDataD2T] = Field(default_factory=list)
    subsystem: SubsystemType = ""
    submitted_at: datetime = None


""" STATUS """


class FileData(BaseModel):
    data: bytes
    content_type: str = "application/octet-stream"
    filename: Optional[str] = None


class TaskResult(BaseModel):
    task_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    output_file_ids: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    spent_ms: Optional[int] = None
    files: Optional[List[FileData]] = None


class StatusRs(BaseModel):
    request_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    done_tasks: int = 0
    total_tasks: int = 0
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tasks: List[TaskResult] = Field(default_factory=list)
