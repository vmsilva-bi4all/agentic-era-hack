
from google.adk import Agent
from ..tools import db_tools
from . import prompt

MODEL = "gemini-2.5-pro"

job_matching_agent = Agent(
    model=MODEL,
    name="job_matching_agent",
    instruction=prompt.JOB_MATCHING_PROMPT,
    output_key="job_matching_output",
    tools=[db_tools.get_cv_by_id, db_tools.list_job_offers],
)
