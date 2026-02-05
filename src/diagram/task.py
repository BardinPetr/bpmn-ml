import random
import time

import cv2
import numpy as np
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
        try:
            print("!!!1")
            img = cv2.imdecode(np.frombuffer(rq['image'], np.uint8), cv2.IMREAD_COLOR)
            print("!!!2")
            r = random.random()
            time.sleep(1)
            return DiagramAnalyzeTaskRs(
                success=True,
                description="Task D2T",
                bpmn_xml="<>",
                visualization=[cv2.imencode(".png", img)[1].tobytes()],
            ).model_dump()
        except Exception as e:
            print(e)
            return dict(success=False)
