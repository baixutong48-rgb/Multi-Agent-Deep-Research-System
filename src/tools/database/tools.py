import json
from src.tools.database.service import DatabaseQueryError, DatabaseService
from langchain_core.tools import BaseTool,tool

def create_database_query_tool(service:DatabaseService)->BaseTool:

    @tool
    async def query_database(sql:str):
        """
        查询企业结构化数据库。
        仅允许执行只读 SQL 查询。
        当研究任务需要查询企业内部结构化数据、
        统计数据、业务记录或关系型数据时使用。
        不用于互联网搜索，也不用于查询非结构化知识库。
        """
        try:
            rows = await service.execute_readonly(sql=sql)
            return json.dumps({
                'status':'success',
                'row_count':len(rows),
                'rows':rows
            },ensure_ascii=False)
        except DatabaseQueryError as exc:
            return json.dumps({
                'status':'error',
                'messages':exc
            },ensure_ascii=False)
    return query_database

def create_database_schema_tool(service: DatabaseService,) -> BaseTool:

    @tool("get_database_schema")
    async def get_database_schema() -> str:
        """
        获取企业数据库的表结构信息。
        当需要编写数据库查询但尚不了解可用表、
        字段名称和字段类型时使用。
        """

        try:
            schema = await service.get_schema()
            return json.dumps(
                {
                    "status": "success",
                    "schema": schema,
                },
                ensure_ascii=False,
            )
        except DatabaseQueryError as exc:
            return json.dumps(
                {
                    "status": "error",
                    "message": str(exc),
                },
                ensure_ascii=False,
            )
    return get_database_schema
