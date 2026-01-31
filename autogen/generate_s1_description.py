import json

from autogen.description_models import GBPMNDiagram
from autogen.gen_struct_crew.crew import generate_diagram_description
from rich import print

tasks = json.load(open('topics.json'))

for i in tasks:
    print(f"task: {i}")
    description: GBPMNDiagram = generate_diagram_description(i)
    if not description:
        print("failed")
        break

    print(description)
    break
