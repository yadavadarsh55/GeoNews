from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, crew, agent, task
from typing import List, Tuple, Any
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.mcp import MCPServerStdio
from pydantic import BaseModel, Field
import os, json, re


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

class ReviewSchema(BaseModel):
    content: str = Field(description="Markdown text containing the Approved newsletter content")
    status: str = Field(description="Status of the letter ie, APPROVED or REJECTED")
    feedback: str = Field(description="Feedback given by the reviewer Agent")

def validate_json_output(result) -> Tuple[bool, Any]:
    try:
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', result.raw)
        if match:
            cleaned_data = match.group(1).strip()
            return (True, cleaned_data)
        return (True, result.raw)
    except:
        return (False, result.raw) 

@CrewBase
class DraftingCrew():

    '''Crew for drafting the Newsletter'''

    agents : List[BaseAgent]
    tasks : List[Task]


    @agent
    def news_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['news_researcher'],
            verbose=True,
            mcps=[geonews_mcp]
        )
    
    @agent
    def news_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['news_analyst'],
            verbose=True
        )
    
    @agent
    def newsletter_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['newsletter_writer'],
            verbose=True
        )
    
    @agent
    def quality_assurance_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_assurance_editor'],
            verbose=True
        )

    @task
    def draft_content_task(self) -> Task:
        return Task(
            config=self.tasks_config['draft_content_task']
        )
    
    @task
    def analyze_content_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_content_task'],
        )
    
    @task
    def write_content_task(self) -> Task:
        return Task(
            config=self.tasks_config['write_content_task']
        )
    
    @task
    def review_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_task'],
            output_json=ReviewSchema,
            guardrail=validate_json_output,
            guardrail_max_retries=3
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )