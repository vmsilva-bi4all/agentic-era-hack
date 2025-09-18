from google.adk import Agent
from app.sub_agents.evaluator.tools import evaluator_tools
from . import prompt

MODEL = "gemini-2.5-pro"

evaluator_agent = Agent(
    model=MODEL,
    name="evaluator_agent",
    instruction=prompt.EVALUATOR_PROMPT,
    output_key="evaluator_output",
    tools=evaluator_tools,
)
