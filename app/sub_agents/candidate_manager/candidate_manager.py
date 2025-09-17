
from google.adk import Agent
from app.tools import db_tools
from . import prompt

MODEL = "gemini-2.5-flash"

candidate_manager_agent = Agent(
    model=MODEL,
    name="candidate_manager_agent",
    instruction=prompt.CANDIDATE_MANAGER_PROMPT,
    output_key="candidate_manager_output",
    tools=[db_tools.get_cv_by_id],
)
