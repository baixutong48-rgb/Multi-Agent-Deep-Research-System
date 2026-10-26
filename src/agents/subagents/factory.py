from dataclasses import dataclass

from langchain_core.tools import BaseTool

from src.agents.subagents.contracts import (
    ResearchSubAgents,
)
from src.agents.subagents.network import (
    create_network_researcher,
)
from src.agents.subagents.database import (
    create_database_researcher,
)
from src.agents.subagents.knowledge import (
    create_knowledge_researcher,
)

@dataclass(frozen=True)
class ResearchToolSet:
    """
    由应用组装层提供的研究工具集合。
    None 表示对应能力未启用。
    """
    web_search: BaseTool | None = None
    database_schema: BaseTool | None = None
    database_query: BaseTool | None = None
    knowledge_search: BaseTool | None = None


def create_research_subagents(tools: ResearchToolSet) -> list[ResearchSubAgents]:

    agents: list[ResearchSubAgents] = []
    if tools.web_search is not None:
        agents.append(
            create_network_researcher(
                tools.web_search
            )
        )

    # database_tools = (
    #     tools.database_schema,
    #     tools.database_query,
    # )

    # if all(tool is not None for tool in database_tools):
    #     assert tools.database_schema is not None
    #     assert tools.database_query is not None

    #     agents.append(
    #         create_database_researcher(
    #             schema_tool=tools.database_schema,
    #             query_tool=tools.database_query,
    #         )
    #     )

    # elif any(tool is not None for tool in database_tools):
    #     raise ValueError(
    #         "数据库研究能力配置不完整："
    #         "必须同时提供 Schema Tool 和 Query Tool"
    #     )

    # if tools.knowledge_search is not None:
    #     agents.append(
    #         create_knowledge_researcher(
    #             tools.knowledge_search
    #         )
    #     )

    names = [agent["name"] for agent in agents]

    if len(names) != len(set(names)):
        raise ValueError(
            "SubAgent 名称必须唯一"
        )

    return agents