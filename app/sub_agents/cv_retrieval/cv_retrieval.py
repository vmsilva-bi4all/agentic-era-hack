
from google.adk import Agent
from ..tools import db_tools
from . import prompt

MODEL = "gemini-2.5-pro"

cv_retrieval_agent = Agent(
    model=MODEL,
    name="cv_retrieval_agent",
    instruction=prompt.CV_RETRIEVAL_PROMPT,
    output_key="cv_retrieval_output",
    tools=[db_tools.get_cv_by_id],
)
