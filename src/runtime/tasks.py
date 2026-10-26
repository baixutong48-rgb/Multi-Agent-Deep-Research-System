import asyncio
from collections.abc import Coroutine
from typing import Any

class TaskRegistry:
    def __init__(self) -> None:
        self.tasks:dict[str,asyncio.Task[None]]={}

    def start(self,run_id:str,coroutine:Coroutine[Any,Any,None]):

        if run_id in self.tasks:
            raise ValueError(f"Run Task 已存在: {run_id}")

        task = asyncio.create_task(coroutine,name=f"research:{run_id}")
        self.tasks[run_id] = task
        task.add_done_callback(lambda completed:self.tasks.pop(run_id,None))

    async def shutdown(self):
        tasks = list(self.tasks.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks,return_exceptions=True)
        self.tasks.clear()