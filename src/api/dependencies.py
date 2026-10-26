from dataclasses import dataclass
from fastapi import Request,WebSocket

from src.runtime.runner import ResearchRunner
from src.runtime.store import RunStore
from src.runtime.tasks import TaskRegistry

@dataclass(frozen=True)
class ApplicationRuntime:
    runner: ResearchRunner
    run_store: RunStore
    tasks: TaskRegistry

def get_runtime(connection:Request|WebSocket)->ApplicationRuntime:
    return connection.app.state.runtime