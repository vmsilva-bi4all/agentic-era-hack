
from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-flash"

opening_manager_agent = Agent(
    model=MODEL,
    name="opening_manager_agent",
    instruction=prompt.OPENING_MANAGER_PROMPT,
    output_key="opening_manager_output",
    tools=[],
)
