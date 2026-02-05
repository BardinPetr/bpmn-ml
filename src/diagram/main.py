import time

import cv2
import numpy as np
from ray import serve
from ray.serve.task_consumer import task_consumer, task_handler

from src.diagram.executor import app as executor_app
from src.ingress.task.task_proc_config import TASK_PROCESSOR_CONFIG


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
@task_consumer(task_processor_config=TASK_PROCESSOR_CONFIG)
class DiagramAnalyzerTask:
    def __init__(self, executor):
        self.executor = executor

    @task_handler(name="task_d2t")
    def task_d2t(self, rq) -> dict:
        try:
            print(f"TASK BEGIN")
            t = time.time()
            img = cv2.imdecode(np.frombuffer(rq['image'], np.uint8), cv2.IMREAD_COLOR)
            res = self.executor.remote(
                img,
                do_visualize=rq.get('visualize', False),
                lang=rq.get('language', None)
            ).result()
            print(f"TASK END {(time.time() - t) * 1000:.0f}ms")
            return res.model_dump()
        except Exception as e:
            print(f"Task Error: {e}")
            return dict(success=False)
        finally:
            pass


app = DiagramAnalyzerTask.bind(executor_app)
