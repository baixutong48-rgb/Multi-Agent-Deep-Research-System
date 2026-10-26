import asyncio
from typing import Protocol
from src.runtime.models import ResearchRun

class RunStore(Protocol):
    async def create(self,run:ResearchRun):
        ...

    async def get(self,run_id:str)->ResearchRun|None:
        ...

    async def update(self,run:ResearchRun):
        ...

class InMemoryRunStore:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.runs : dict[str,ResearchRun] = {}

    async def create(self,run:ResearchRun):
        async with self.lock:
            if run.run_id in self.runs:
                raise ValueError(f"Run 已存在: {run.run_id}")
            self.runs[run.run_id] = run.model_copy(deep=True)

    async def get(self,run_id:str)->ResearchRun|None:
        async with self.lock:
            run = self.runs.get(run_id)
            if run is None:
                return None
            return run.model_copy(deep=True)

    async def update(self,run:ResearchRun):
        async with self.lock:
            if run.run_id not in self.runs:
                raise ValueError(f"Run 不存在: {run.run_id}")
            self.runs[run.run_id] = run.model_copy(deep=True)
