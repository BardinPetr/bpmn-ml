import asyncio
import logging
from time import sleep

from ray import serve
from ray.serve.handle import DeploymentHandle
from starlette.requests import Request
from streamlit import starlette

logger = logging.getLogger()


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class Srv1:
    def __init__(self, nonce):
        self.nonce = nonce
        logger.warning("S1 init")

    def fun(self, x):
        logger.info(f"[S1{self.nonce}] I {x}")
        sleep(10)
        logger.info(f"[S1{self.nonce}] O {x}")
        return f"[1:{self.nonce}:{x}]"


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class Srv2:
    def __init__(self):
        logger.warning("S2 init")

    def fun(self, x):
        logger.info(f"[S2] I {x}")
        sleep(5)
        logger.info(f"[S2] O {x}")
        return f"[2:{x}]"


@serve.deployment(ray_actor_options={"num_cpus": 0.1})
class Srv3:
    def __init__(self, s1: DeploymentHandle[Srv1], s2: DeploymentHandle[Srv2]):
        self.s1 = s1
        self.s2 = s2
        logger.warning("S3 init")

    async def fun(self, x):
        logger.info(f"[S3] I {x}")
        a = self.s1.fun.remote(x)
        b = self.s2.fun.remote(x)
        logger.info(f"[S3] D {x}")
        a, b = await asyncio.gather(a, b)
        c = a + b
        c = f"[3:{c}]"
        logger.info(f"[S3] O {x}")
        return c



app = Srv3.bind(Srv1.bind(1), Srv2.bind())
