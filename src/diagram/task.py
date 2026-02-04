import random
import time

from ray import serve
from ray.serve.task_consumer import task_consumer, task_handler

from src.ingress.task.task_model import DiagramAnalyzeTaskRq, DiagramAnalyzeTaskRs
from src.ingress.task.task_proc_config import TASK_PROCESSOR_CONFIG


@serve.deployment(ray_actor_options={"num_cpus": 2})
@task_consumer(task_processor_config=TASK_PROCESSOR_CONFIG)
class DiagramAnalyzerTask:
    def __init__(self):
        pass

    @task_handler(name="task_d2t")
    def task_d2t(self, rq: DiagramAnalyzeTaskRq) -> dict:
        r = random.random()
        print(f"<{r}")
        time.sleep(5)
        print(f">{r}")
        return dict(
            success=True,
            description="Task D2T",
            bpmn_xml="<>",
            visualization=[b'rq.image']
        )

