from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from autogen.config.cai_tools import kickoff
from autogen.config.settings import settings
from autogen.description_models import GBPMNDiagram


@CrewBase
class DirectionCrew:
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analyst'],
            llm=settings.llm
        )

    @task
    def generate_bpmn(self) -> Task:
        return Task(
            config=self.tasks_config['generate_bpmn'],
            agent=self.business_analyst(),
            output_pydantic=GBPMNDiagram
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False
        )


def generate_diagram_description(process_description) -> GBPMNDiagram:
    return kickoff(
        DirectionCrew(),
        dict(process_description=process_description)
    ) or None

print(generate_diagram_description("but ticket"))