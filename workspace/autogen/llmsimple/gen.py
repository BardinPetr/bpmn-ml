import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

from autogen.description_models import GBPMNDiagram

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_API"),
    api_key=os.getenv("LLM_KEY"),
)
messages = [
    {"role": "system", "content": open("bpmn.sys.prompt").read()},
    {"role": "user", "content": open("bpmn.prompt").read()}
]


def interact():
    try:
        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=messages
        )
        txt = completion.choices[0].message.content
        print(txt)
        return GBPMNDiagram.model_validate_json(txt)
    except Exception as e:
        print(e)
        return None


while True:
    t = time.time()
    description: GBPMNDiagram = interact()
    if not description:
        print("failed")
        continue
    print(description)
    print(time.time() - t)
