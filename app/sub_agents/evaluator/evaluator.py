
from google.adk import Agent
from app.tools import db_tools
from . import prompt

MODEL = "gemini-2.5-flash"

evaluator_agent = Agent(
    model=MODEL,
    name="evaluator_agent",
    instruction=prompt.EVALUATOR_PROMPT,
    output_key="evaluator_output",
    tools=[db_tools.get_cv_by_id, db_tools.list_job_offers],
)
