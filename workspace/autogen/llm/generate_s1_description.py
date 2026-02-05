import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

from autogen.description_models import GBPMNDiagram

load_dotenv()


def generate_description(task):
    client = OpenAI(
        base_url=os.getenv("LLM_API"),
        api_key=os.getenv("LLM_KEY"),
    )
    try:
        completion = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=[
                {"role": "system", "content": open("bpmn.sys.prompt").read()},
                {"role": "user", "content": open("bpmn.prompt").read().replace("{process_description}", task)}
            ]
        )
        txt = completion.choices[0].message.content
        print(txt)
        return GBPMNDiagram.model_validate_json(txt)
    except Exception as e:
        print(e)
        return None


tasks = json.load(open('topics.json'))

for i in tasks:
    print(f"task: {i}")
    t = time.time()
    description: GBPMNDiagram = generate_description(i)
    if not description:
        print("failed")
        break
    print(description)
    print(time.time() - t)
    break
