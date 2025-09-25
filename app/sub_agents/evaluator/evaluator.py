from google.adk import Agent
from . import prompt

MODEL = "gemini-2.5-pro"

evaluator_agent = Agent(
    model=MODEL,
    name="evaluator_agent",
    instruction=prompt.EVALUATOR_PROMPT,
    output_key="evaluator_output",
)
