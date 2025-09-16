
from google.adk import Agent
from ..tools import db_tools
from . import prompt

MODEL = "gemini-2.5-pro"

job_offer_storage_agent = Agent(
    model=MODEL,
    name="job_offer_storage_agent",
    instruction=prompt.JOB_OFFER_STORAGE_PROMPT,
    output_key="job_offer_storage_output",
    tools=[db_tools.add_job_offer],
)
