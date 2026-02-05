from ray import serve

from src.renderer.renderbpmn import BPMNRenderer


@serve.deployment(ray_actor_options={"num_cpus": 1})
class BPMNRendererService:
    def __init__(self):
        self.__r = BPMNRenderer()

    async def __call__(self, code):
        return await self.__r.render_by_code(code)


app = BPMNRendererService.bind()
