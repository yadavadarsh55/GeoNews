from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, crew, agent, task
from typing import List
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.mcp import MCPServerStdio
import os



geonews_mcp = MCPServerStdio(
                    command="uv", 
                    args=[
                            "run",
                            "--with",
                            "fastmcp,newsapi-python,feedparser,newspaper3k,lxml[html_clean]",
                            "fastmcp",
                            "run",
                            "src/geonews_flow/tools/mcpserver.py"
                        ],
                    env={
                        'NEWS_API_KEY' : os.environ.get('NEWS_API_KEY'),
                        'GMAIL_USER' : os.environ.get('GMAIL_USER'),
                        'GMAIL_PASS' : os.environ.get('GMAIL_PASS')
                    }
                )

@CrewBase
class PublishingCrew():
    """Crew for Publishing final Newsletter"""

    agents : List[BaseAgent]
    tasks : List[Task]


    @agent
    def newsletter_publisher(self) -> Agent:
        return Agent(
            config=self.agents_config['newsletter_publisher'],
            verbose=True,
            mcps=[geonews_mcp]
        )
    
    @task
    def publish_task(self) -> Task:
        return Task(
            config=self.tasks_config['publish_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential
        )