
from google.adk import Agent
from ..tools import db_tools
from . import prompt

MODEL = "gemini-2.5-pro"

cv_storage_agent = Agent(
    model=MODEL,
    name="cv_storage_agent",
    instruction=prompt.CV_STORAGE_PROMPT,
    output_key="cv_storage_output",
    tools=[db_tools.add_cv],
)
