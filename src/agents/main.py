from typing import Sequence,Any

from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from deepagents import create_deep_agent

from src.agents.subagents.contracts import ResearchSubAgents
from src.prompts.main_agent import MAIN_AGENT_PROMPT

def create_deep_research_agent(
    model:BaseChatModel,
    subagents:Sequence[ResearchSubAgents],
    main_tools:Sequence[BaseTool],
    checkpointer:Any|None = None):
    _validate_main_agent_dependencies(subagents,main_tools)
    kwargs : dict[str,Any]={
        'model':model,
        'system_prompt':MAIN_AGENT_PROMPT,
        'tools':main_tools,
        'subagents':subagents,
    }
    if checkpointer is not None:
        kwargs['checkpointer'] = checkpointer

    return create_deep_agent(**kwargs)


def _validate_main_agent_dependencies(subagents:Sequence[ResearchSubAgents],main_tools:Sequence[BaseTool])->None:
    subagents_names = [
        subagent['name']
        for subagent in subagents
    ]
    if len(subagents_names) != len(set(subagents_names)):
        raise ValueError("Main Agent的SubAgent名称必须唯一")
    main_tools_names = [
        main_tool.name
        for main_tool in main_tools
    ]
    if len(main_tools_names) != len(set(main_tools_names)):
        raise ValueError("Main Agent的工具名称必须唯一")