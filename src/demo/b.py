import asyncio

from fastapi import FastAPI
from pydantic import BaseModel
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.schema import TaskProcessorConfig
from ray.serve.task_consumer import instantiate_adapter_from_config, task_consumer, task_handler

from task_proc_config import TASK_PROCESSOR_CONFIG

fastapi_app = FastAPI()

class ScheduleRequest(BaseModel):
    request: str

@serve.deployment
@serve.ingress(fastapi_app)
class Main:
    def __init__(self, task_processor_config: TaskProcessorConfig, h):
        self.task_adapter = instantiate_adapter_from_config(task_processor_config)

    @fastapi_app.post("/process")
    async def task_submit(self, r: ScheduleRequest):
        task_result = self.task_adapter.enqueue_task_sync(
            task_name="task1",
            kwargs=dict(data=str(r.request)),
        )
        print(dict(data=str(r.request)))
        return {
            "task_id": task_result.id,
            "status": task_result.status,
        }

    @fastapi_app.get("/status/{task_id}")
    async def task_status(self, task_id: str):
        status = self.task_adapter.get_task_status_sync(task_id)
        return {
            "task_id": task_id,
            "status": status.status,
            "result": status.result if status.status == "SUCCESS" else None,
            "error": str(status.result) if status.status == "FAILURE" else None,
        }

app = Main.bind(TASK_PROCESSOR_CONFIG, None)
