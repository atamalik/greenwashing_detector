from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from .tools.pdf_loader import PDFReportReader
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class GreenwashingDetector():
    """GreenwashingDetector crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def esg_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['esg_analyst'],
            tools=[PDFReportReader()],
            verbose=True
        )

    @agent
    def compliance_checker(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_checker'],
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def extract_esg_claims(self) -> Task:
        return Task(
            config=self.tasks_config['extract_esg_claims'],
        )

    @task
    def validate_claims(self) -> Task:
        return Task(
            config=self.tasks_config['validate_claims'],
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the GreenwashingDetector crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
