
from google.adk import Agent
from app.sub_agents.candidate_manager.tools import candidate_manager_tools
from . import prompt

MODEL = "gemini-2.5-flash"

candidate_manager_agent = Agent(
    model=MODEL,
    name="candidate_manager_agent",
    instruction=prompt.CANDIDATE_MANAGER_PROMPT,
    output_key="candidate_manager_output",
    tools=[candidate_manager_tools.add_cv, candidate_manager_tools.get_cv],
)
