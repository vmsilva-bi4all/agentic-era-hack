from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.candidate_manager.candidate_manager import candidate_manager_agent
from .sub_agents.opening_manager.opening_manager import opening_manager_agent
from .sub_agents.evaluator.evaluator import evaluator_agent

MODEL = "gemini-2.5-flash"

hr_coordinator = LlmAgent(
    name="hr_coordinator",
    model=MODEL,
    description=(
        "guide users through a structured process to manage human resources tasks. "
        "orchestrate a series of expert sub-agents to store and retrieve CVs and job offers, "
        "and find the best matches between them."
    ),
    instruction=prompt.HR_COORDINATOR_PROMPT,
    output_key="hr_coordinator_output",
    tools=[
        AgentTool(agent=candidate_manager_agent),
     #   AgentTool(agent=opening_manager_agent),
        AgentTool(agent=evaluator_agent),
    ],
)

root_agent = hr_coordinator
