import json
from langchain_core.tools import tool,BaseTool
from src.tools.search.client import TavilySearchClient,SearchServiceError

def create_search_tool(client:TavilySearchClient)->BaseTool:

    @tool
    async def web_search(query:str,max_results: int = 5)->str:
        """
        搜索互联网中的公开信息。
        适用于需要外部资料、最新信息、
        行业动态和公开事实验证的任务。
        不用于查询企业内部数据库或私有知识库。
        """
        try:
            results = await client.search(query=query,max_results=max_results)
            return json.dumps(results,ensure_ascii=False)

        except SearchServiceError as exc:
            return json.dumps({
                'status' : 'error',
                'messages':str(exc)
            },ensure_ascii=False)

    return web_search