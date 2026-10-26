import json
from langchain_core.tools import tool,BaseTool
from src.tools.knowledge.client import KnowledgeClient,KnowledgeServiceError

def create_knowledge_tool(client:KnowledgeClient)->BaseTool:

    @tool
    async def search_knowledge(query:str,top_k:int=5)->str:
        """
        检索企业内部知识库。
        当研究任务需要查询企业内部文档、制度、
        产品资料、技术文档或其他非结构化私有知识时使用。
        不用于互联网公开信息搜索，
        也不用于查询关系型数据库中的结构化业务数据。
        """
        try:
            response = await client.search(query=query,top_k=top_k)
            return json.dumps({
                'status':'success',
                'query':response.query,
                'documents':[
                    document.model_dump()
                    for document in response.documents
                ]
            },ensure_ascii=False)
        
        except KnowledgeServiceError as exc:
            return json.dumps({
                'status':'error',
                'messages':str(exc)
            },ensure_ascii=False)
    
    return search_knowledge