from langchain_core.tools import BaseTool

from src.agents.subagents.contracts import (
    ResearchSubAgents,
    validate_subagent,
)

from src.agents.subagents.prompts import (
    DATABASE_RESEARCHER_DESCRIPTION,
    DATABASE_RESEARCHER_PROMPT,
)


def create_database_researcher(
    schema_tool: BaseTool,
    query_tool: BaseTool,
) -> ResearchSubAgents:

    if schema_tool.name != "get_database_schema":
        raise ValueError(
            "Database Researcher 需要 get_database_schema 工具"
        )

    if query_tool.name != "query_database":
        raise ValueError(
            "Database Researcher 需要 query_database 工具"
        )

    agent: ResearchSubAgents = {
        "name": "database_researcher",
        "description": DATABASE_RESEARCHER_DESCRIPTION,
        "system_prompt": DATABASE_RESEARCHER_PROMPT,
        "tools": [
            schema_tool,
            query_tool,
        ],
    }

    validate_subagent(agent)

    return agent