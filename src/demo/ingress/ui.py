import gradio as gr
from fastapi import FastAPI
from ray import serve

localray()


@serve.deployment
class ChildDeployment:
    def __call__(self, y):
        return "Hello from the child deployment! " + y


def fastapi_factory():
    app = FastAPI()

    handler = serve.get_deployment_handle("ChildDeployment", app_name="default")

    async def run(x):
        return await handler.remote(x)

    builder = lambda: gr.Interface(run, "textbox", "textbox")
    gio = builder()

    gr.mount_gradio_app(app, gio, path="/")

    return app


@serve.deployment
@serve.ingress(fastapi_factory)
class ParentDeployment:
    def __init__(self, child):
        self.child = child


serve.run(ParentDeployment.bind(ChildDeployment.bind()))
