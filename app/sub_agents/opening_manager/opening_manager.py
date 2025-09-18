from google.adk import Agent
from app.tools import db_tools
from app.sub_agents.opening_manager.tools import openings_manager_tools
from . import prompt

MODEL = "gemini-2.5-flash"

opening_manager_agent = Agent(
    model=MODEL,
    name="opening_manager_agent",
    instruction=prompt.OPENING_MANAGER_PROMPT,
    output_key="opening_manager_output",
    tools=[
        openings_manager_tools.add_opening,
        openings_manager_tools.get_job_opening,
        openings_manager_tools.list_openings,
        openings_manager_tools.delete_opening,
    ],
)
