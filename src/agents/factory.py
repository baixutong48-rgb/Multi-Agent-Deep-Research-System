from collections.abc import Sequence
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from src.agents.main import create_deep_research_agent
from src.agents.subagents.contracts import ResearchSubAgents
from src.tools.files.tools import (
    create_read_file_tool,
    create_write_markdown_file_tool,
)
from src.tools.files.workspace import Workspace

class ResearchAgentFactory:
    """
    为单次 Research Run 创建 Main Agent。
    Application-scoped dependencies:
    - model
    - subagents
    - checkpointer
    Run-scoped dependency:
    - workspace
    """
    def __init__(self,*,model: BaseChatModel,subagents:Sequence[ResearchSubAgents],checkpointer: Any | None = None,) -> None:
        self._model = model
        self._subagents = tuple(subagents)
        self._checkpointer = checkpointer

    def create(self,*,workspace: Workspace):
        read_file_tool = create_read_file_tool(workspace)

        write_markdown_tool = create_write_markdown_file_tool(workspace)

        return create_deep_research_agent(
            model=self._model,
            subagents=self._subagents,
            main_tools=[
                read_file_tool,
                write_markdown_tool,
            ],
            checkpointer=self._checkpointer,
        )