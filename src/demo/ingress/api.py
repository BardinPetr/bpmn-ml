from time import sleep

import requests
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from ray import serve
from starlette.responses import PlainTextResponse

import src.main

fastapi_app = FastAPI()


@serve.deployment
@serve.ingress(fastapi_app)
class APIIngress:
    @fastapi_app.get("/{name}")
    async def say_hi(self, name: str) -> PlainTextResponse:
        return PlainTextResponse(f"Hello {name}!")


app = APIIngress.bind()
serve.run(app)
sleep(100)
