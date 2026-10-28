import asyncio
import re
from typing import Any

from sqlalchemy import text,inspect
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

class DatabaseQueryError(Exception):
    """数据库查询执行失败。"""

class UnsafeQueryError(DatabaseQueryError):
    """SQL 不满足只读安全策略。"""

class DatabaseService:
    def __init__(self,url:str,query_timeout:float=10.0,max_rows:int=100):
        self.engine:AsyncEngine = create_async_engine(
            url,
            pool_pre_ping=True
        )
        self.query_timeout=query_timeout
        self.max_rows=max_rows
    
    async def execute_readonly(self,sql:str)->list[dict[str,Any]]:
        self._validate_readonly(sql)
        try:
            async with self.engine.connect() as connection:
                results = await asyncio.wait_for(
                    connection.execute(text(sql)),
                    timeout=self.query_timeout
                )
                rows = results.mappings().fetchmany(self.max_rows)
                return [
                    dict(row)
                    for row in rows
                ]
        except asyncio.TimeoutError as exc:
            raise DatabaseQueryError('数据库查询超时') from exc

    async def close(self):
        await self.engine.dispose()


    @staticmethod
    def _validate_readonly(sql:str)->None:
        normalized = sql.strip()
        if not normalized:
            raise UnsafeQueryError('sql不能为空')
        if ';' in normalized.rstrip(';'):
            raise UnsafeQueryError('不允许执行多条sql')
        normalized = normalized.rstrip(';').strip()
        if not re.match(
            r"^(select|with)\b",
            normalized,
            flags=re.IGNORECASE
        ):
            raise UnsafeQueryError("数据库工具只允许只读查询")

        forbidden = re.compile(
            r"\b("
            r"insert|update|delete|drop|alter|truncate|"
            r"create|grant|revoke|merge|copy|call"
            r")\b",
            flags=re.IGNORECASE,
        )
        if forbidden.search(normalized):
            raise UnsafeQueryError("SQL 包含禁止执行的操作")

    async def get_schema(self):
        async with self.engine.connect() as connection:
            return await connection.run_sync(self._inspect_schema)

    @staticmethod
    def _inspect_schema(connection):
        inspector = inspect(connection)
        schema = {}
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            schema[table_name] = [
            {
                "name": column["name"],
                "type": str(column["type"]),
            }
            for column in columns
        ]

        return schema

