from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.serve.task_consumer import task_consumer, task_handler

from a import Srv3, Srv1, Srv2
from task_proc_config import TASK_PROCESSOR_CONFIG


@serve.deployment
@task_consumer(task_processor_config=TASK_PROCESSOR_CONFIG)
class Processor:
    def __init__(self, dh):
        self.dh = dh

    @task_handler(name="task1")
    def task1(self, data: str):
        res = self.dh.fun.remote("data").result()
        return {
            "status": "success",
            "result": res,
        }


app = Processor.bind(
    Srv3.bind(Srv1.bind(1), Srv2.bind())
)
