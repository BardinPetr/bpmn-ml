import asyncio
import logging
from typing import Dict, Optional, List

import ray
from ray import serve, ObjectRef
from ray.serve.schema import TaskResult as RayTaskResult
from ray.serve.task_consumer import instantiate_adapter_from_config

from src.data.ray_store import ray_put, ray_get
from src.ingress.api.model import InternalTaskBlock, StatusRs, FileData, TaskStatus, TaskDataT2D, TaskDataD2T
from src.ingress.task.task_proc_config import TASK_PROCESSOR_CONFIG

logger = logging.getLogger()


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class TaskManager:
    def __init__(self):
        self.task_adapter = instantiate_adapter_from_config(TASK_PROCESSOR_CONFIG)
        self.tasks: Dict = {}

        test = b'asdasdad'
        th = ray_put(test)
        print(th)
        print("@")
        print(ray_get(th))

    async def task_from_rq(self, rq):
        if isinstance(rq, TaskDataT2D):
            return dict(text=rq.text)
        elif isinstance(rq, TaskDataD2T):
            data = ray.put(rq.image.data)
            print("!!!", data)
            return dict(image="rq.image.data")
        return None

    async def new_request(self, request: InternalTaskBlock):
        async def __proc(i):
            return self.task_adapter.enqueue_task_sync(
                task_name=f"task_{request.subsystem.value}",
                kwargs=dict(rq=await self.task_from_rq(i)),
            )
        task_handles = await asyncio.gather(*[__proc(i) for i in request.tasks])
        self.tasks[request.request_id] = [i.id for i in task_handles]
        logging.debug(
            f"[{request.request_id}] request tasks started: {len(request.tasks)}: {self.tasks[request.request_id]}")

    async def get_result(self, request_id: str) -> Optional[StatusRs]:
        if (request_tasks := self.tasks.get(request_id)) is None:
            return None
        tasks: List[RayTaskResult] = [
            self.task_adapter.get_task_status_sync(i)
            for i in request_tasks
        ]
        logging.debug(f"status rq {request_id} -> {[(i.task_id, i.status) for i in tasks]}")
        res = []
        for i in tasks:
            tr = i.result.as_task_result()
            tr.task_id = i.id
            tr.output_file_ids = [f"{i.id}+{fi}" for fi in range(len(tr.files))]
            tr.files = None
            res.append(tr)

        total = len(res)
        done_cnt = sum(int(i.status == TaskStatus.SUCCESS) for i in res)
        return StatusRs(
            request_id=request_id,
            status=TaskStatus.SUCCESS if done_cnt == total else TaskStatus.PROCESSING,
            done_tasks=done_cnt,
            total_tasks=total,
            tasks=res
        )

    async def get_output(self, request_id: str, file_id: str) -> Optional[FileData]:
        logging.debug(f"out rq {request_id} {file_id}")
        task_id, file_num = file_id.split("+")
        try:
            res: RayTaskResult = self.task_adapter.get_task_status_sync(task_id)
            return res.as_task_result().files[int(file_num)]
        except:
            return None


app = TaskManager.bind()
