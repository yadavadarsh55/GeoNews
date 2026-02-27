import json
import datetime as dt
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router
from crewai.flow.persistence import persist
from .crews.drafting_crew.drafting_crew import DraftingCrew
from .crews.publishing_crew.publishing_crew import PublishingCrew

MAX_RETRY = 3

THRESHOLD_DATE = str(dt.date.today() - dt.timedelta(days=7))

class GeoNewsFlowState(BaseModel):

    date : str = ""
    content : str = ""
    feedback : str = "None"
    status : str = "PENDING"
    retry_count : int = 0


@persist()
class GeoNewsFlow(Flow[GeoNewsFlowState]):

    def draft_newsletter(self):
        response = DraftingCrew().crew().kickoff(inputs={
            'date': self.state.date,
            'feedback': self.state.feedback
        })

        
        try:
            data = json.loads(response.raw)
        except json.JSONDecodeError as e:
            self.state.status = "JSON_ERROR" 
            return self.state

        self.state.content = data["content"]
        self.state.feedback = data["feedback"]
        self.state.status = data["status"]

        return self.state

    @start()
    def start_draft_newsletter(self):
        return self.draft_newsletter()

    @router(start_draft_newsletter)
    def check_quality(self):
        
        if self.state.status == "APPROVED":
            return "ready_to_publish"
        
        elif self.state.status == "JSON_ERROR":
            return "failed"

        elif self.state.retry_count < 3:
            self.state.retry_count += 1
            return "retry"
        
        else:
            return "failed"

    @listen("retry")
    def retry_writing(self):
        return self.draft_newsletter()

    @listen("ready_to_publish")
    def publish_newsletter(self):
        
        result = PublishingCrew().crew().kickoff(inputs={
            'content': self.state.content,
            'recipient_emails_list': ["la8085978@gmail.com", "gupta.akshita299@gmail.com"] 
        })
        
        return result

    @listen("failed")
    def failed_workflow(self):
        print("--- [DEBUG] WORKFLOW FAILED ---", flush=True)


def kickoff():
    GeoNewsFlow().kickoff(inputs={"date": THRESHOLD_DATE})


def plot():
    flow = GeoNewsFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()