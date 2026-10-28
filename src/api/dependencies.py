from dataclasses import dataclass
from fastapi import Request,WebSocket
from src.tools.database.service import DatabaseService
from src.tools.search.client import TavilySearchClient

from src.runtime.runner import ResearchRunner
from src.runtime.store import RunStore
from src.runtime.tasks import TaskRegistry

@dataclass(frozen=True)
class ApplicationRuntime:
    runner: ResearchRunner
    run_store: RunStore
    tasks: TaskRegistry
    db_service:DatabaseService
    search_client:TavilySearchClient

    async def shutdown(self):
        try:
            await self.tasks.shutdown()
        finally:
            await self.db_service.close()
            await self.search_client.close()


def get_runtime(connection:Request|WebSocket)->ApplicationRuntime:
    return connection.app.state.runtime