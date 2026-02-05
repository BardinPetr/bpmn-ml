import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, Response, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from ray import serve
from starlette.staticfiles import StaticFiles

from src.ingress.api.model import TaskStatus, SubmitRs, StatusRs, InternalTaskBlock, SubsystemType, TaskDataT2D, \
    FileData, \
    TaskDataD2T
from src.ingress.task.task_manager import app as task_manager_app

fastapi_app = FastAPI()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
@serve.ingress(fastapi_app)
class APIIngress:
    def __init__(self, task_service_handle):
        self.task_service = task_service_handle

        fastapi_app.mount("/",
                          app=StaticFiles(directory=Path(__file__).parent.parent.resolve() / "mlclient" / "build",
                                          html=True),
                          name="static")

    @fastapi_app.post("/submit/d2t", response_model=SubmitRs)
    async def submit_task_2t(self,
                             files: List[UploadFile],
                             parameters: str = Form(...)) -> SubmitRs:
        props = json.loads(parameters)

        async def __load(file: UploadFile):
            return TaskDataD2T(image=FileData(data=await file.read(), content_type=file.content_type),
                               props=props)

        request_id = str(uuid.uuid4())
        submitted_at = datetime.now()
        await self.task_service.new_request.remote(InternalTaskBlock(
            request_id=request_id,
            submitted_at=submitted_at,
            tasks=await asyncio.gather(*[__load(i) for i in files]),
            subsystem=SubsystemType.DIAG2TXT,
        ))
        return SubmitRs(
            request_id=request_id,
            status=TaskStatus.PENDING,
            total_tasks=len(files)
        )

    @fastapi_app.post("/submit/t2d", response_model=SubmitRs)
    async def submit_task_2d(self, request: List[TaskDataT2D]) -> SubmitRs:
        request_id = str(uuid.uuid4())
        submitted_at = datetime.now()
        await self.task_service.new_request.remote(InternalTaskBlock(
            request_id=request_id,
            submitted_at=submitted_at,
            tasks=request,
            subsystem=SubsystemType.TXT2DIAG,
        ))
        return SubmitRs(
            request_id=request_id,
            status=TaskStatus.PENDING,
            total_tasks=len(request)
        )

    @fastapi_app.get("/status/{request_id}", response_model=StatusRs)
    async def get_status(self, request_id: str) -> StatusRs:
        status_obj = await self.task_service.get_result.remote(request_id)
        if status_obj is None:
            raise HTTPException(
                status_code=404,
                detail=f"Request {request_id} not found"
            )
        return status_obj

    @fastapi_app.get("/result/{request_id}/{file_id}")
    async def download_file(self, request_id: str, file_id: str):
        file_data: FileData = await self.task_service.get_output.remote(request_id, file_id)
        if file_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"File {file_id} not found for request {request_id}"
            )
        return Response(
            content=file_data.data,
            media_type=file_data.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_data.filename}"'
            }
        )


app = APIIngress.bind(task_manager_app)
