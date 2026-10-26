from typing import TypedDict
from langchain_core.tools import BaseTool

class ResearchSubAgents(TypedDict):
    name:str
    description:str
    system_prompt:str
    tools:list[BaseTool]

def validate_subagent(agent:ResearchSubAgents):
    required_fields = (
        'name','description','system_prompt','tools'
    )
    for field in required_fields:
        if field not in agent:
            raise ValueError(f'缺少必要字段:{field}')

    for field in ('name','description','system_prompt'):
        value = agent[field]
        if not isinstance(value,str) or not value.strip():
            raise ValueError(f'{value}字段不能为空')

    tools = agent['tools']
    if not isinstance(tools,list) or not tools:
        raise ValueError(f'{agent["name"]}至少需要一个工具')

    for tool in tools:
        if not isinstance(tool,BaseTool):
            raise TypeError(f'{agent['name']}包含无效工具')

    tool_names = [tool.name for tool in tools]

    if len(tool_names) != len(set(tool_names)):#这里用到了 Python 的 set——集合不允许重复元素
        raise ValueError(
            f"SubAgent {agent['name']} 存在重复工具名称"
        )