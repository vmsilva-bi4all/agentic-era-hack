
from google.adk import Agent
from ..tools import db_tools
from . import prompt

MODEL = "gemini-2.5-pro"

job_offer_retrieval_agent = Agent(
    model=MODEL,
    name="job_offer_retrieval_agent",
    instruction=prompt.JOB_OFFER_RETRIEVAL_PROMPT,
    output_key="job_offer_retrieval_output",
    tools=[db_tools.list_job_offers],
)
