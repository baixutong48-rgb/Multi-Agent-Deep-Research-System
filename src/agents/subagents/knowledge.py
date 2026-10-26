from langchain_core.tools import BaseTool

from src.agents.subagents.contracts import (
    ResearchSubAgents,
    validate_subagent,
)

from src.agents.subagents.prompts import (
    KNOWLEDGE_RESEARCHER_DESCRIPTION,
    KNOWLEDGE_RESEARCHER_PROMPT,
)


def create_knowledge_researcher(
    knowledge_tool: BaseTool,
) -> ResearchSubAgents:

    if knowledge_tool.name != "search_knowledge":
        raise ValueError(
            "Knowledge Researcher 需要 search_knowledge 工具"
        )

    agent: ResearchSubAgents = {
        "name": "knowledge_researcher",
        "description": KNOWLEDGE_RESEARCHER_DESCRIPTION,
        "system_prompt": KNOWLEDGE_RESEARCHER_PROMPT,
        "tools": [knowledge_tool],
    }

    validate_subagent(agent)

    return agent