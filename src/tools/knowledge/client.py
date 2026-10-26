from typing import Protocol
import httpx
from src.tools.knowledge.models import KnowledgeSearchResult,KnowledgeDocument

class KnowledgeServiceError(Exception):
    """企业知识服务调用失败。"""

class KnowledgeClient(Protocol):
    async def search(self,query:str,top_k:int=5)->KnowledgeSearchResult:
        ...

class HTTPKnowledgeClient:
    def __init__(self,base_url:str,api_key:str|None=None,timeout:float=20.0):
        self.base_url=base_url.rstrip('/')
        self.timeout = timeout
        self.api_key=api_key

    async def search(self,query:str,top_k:int=5)->KnowledgeSearchResult:
        headers={}
        if self.api_key:
            headers["Authorization"] = (f"Bearer {self._api_key}")

        payload={
            'query':query,
            'top_k':top_k
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f'{self.base_url}/search',
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as exc:
            raise KnowledgeServiceError("企业知识库请求超时") from exc

        try:
            documents = [
                KnowledgeDocument.model_validate(item)
                for item in data.get("documents", [])
            ]

        except (TypeError, ValueError) as exc:
            raise KnowledgeServiceError(
                "企业知识服务返回的数据格式不正确"
            ) from exc

        return KnowledgeSearchResult(
            query=query,
            document=documents
        )