from typing import Any

import httpx

class SearchServiceError(Exception):
    """搜索服务调用失败。"""

class TavilySearchClient:
    def __init__(self,api_key:str,timeout:float=15.0):
        if not api_key:
            raise ValueError('api_key不能为空')
        self.api_key = api_key
        self.timeout = timeout
        self.client =httpx.AsyncClient(timeout=self.timeout)

    async def search(self,query:str,max_results:int=5)->list[dict[str,Any]]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        }
        try:
            async with self.client:
                response = await self.client.post(
                    "https://api.tavily.com/search",
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as exc:
            raise SearchServiceError('网络搜索超时') from exc
        if isinstance(data,dict):
            results = data.get('results')
        return results

    async def close(self):
        await self.client.aclose()
            
