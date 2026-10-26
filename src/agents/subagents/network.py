from langchain_core.tools import BaseTool
from src.agents.subagents.contracts import validate_subagent,ResearchSubAgents
from src.agents.subagents.prompts import NETWORK_RESEARCHER_DESCRIPTION,NETWORK_RESEARCHER_PROMPT

def create_network_researcher(search_tool:BaseTool)->ResearchSubAgents:
    if search_tool.name != 'web_search':
        raise ValueError("Network Researcher 需要 web_search 工具")

    agent:ResearchSubAgents = {
        "name": "network_researcher",
        "description": NETWORK_RESEARCHER_DESCRIPTION,
        "system_prompt": NETWORK_RESEARCHER_PROMPT,
        "tools": [search_tool],
    }
    validate_subagent(agent)
    return agent
