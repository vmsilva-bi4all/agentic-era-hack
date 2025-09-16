
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.cv_storage.cv_storage import cv_storage_agent
from .sub_agents.job_offer_storage.job_offer_storage import job_offer_storage_agent
from .sub_agents.cv_retrieval.cv_retrieval import cv_retrieval_agent
from .sub_agents.job_offer_retrieval.job_offer_retrieval import job_offer_retrieval_agent
from .sub_agents.job_matcher.job_matcher import job_matching_agent

MODEL = "gemini-2.5-pro"

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
        AgentTool(agent=cv_storage_agent),
        AgentTool(agent=job_offer_storage_agent),
        AgentTool(agent=cv_retrieval_agent),
        AgentTool(agent=job_offer_retrieval_agent),
        AgentTool(agent=job_matching_agent),
    ],
)

root_agent = hr_coordinator
