from collections import defaultdict
from typing import Protocol,Any
from src.observability.events import TraceEvent,TraceEventType
import asyncio

class TraceStore(Protocol):

    async def create_event(self,*,run_id: str,event_type: TraceEventType,actor: str | None = None,name: str | None = None,
        metadata: dict | None = None,):
        ...

    async def list_events(self,run_id:str,*,after_sequence)->list[TraceEvent]:
        ...

class InMemoryTraceStore:
    def __init__(self) -> None:
        self.events : dict[str,list[TraceEvent]] = defaultdict(list)#键不存在时，创建 键和value=空列表
        self.sequences:dict[str,int] = defaultdict(int)#键不存在时，创建 键和value=0
        self.lock = asyncio.Lock()

    async def create_event(self,*,run_id: str,event_type: TraceEventType,actor: str | None = None,name: str | None = None,
        metadata: dict[str, Any] | None = None,):
        async with self.lock:
             self.sequences[run_id] += 1
             event = TraceEvent(
                run_id=run_id,
                sequence=self.sequences[run_id],
                event_type=event_type,
                actor=actor,
                name=name,
                metadata=metadata or {},
            )
             self.events[run_id].append(event)
             return event.model_copy(deep=True)

    async def list_events(self,run_id:str,*,after_sequence:int=0)->list[TraceEvent]:
        async with self.lock:
            return[
                event.model_copy(deep=True)
                for event in self.events.get(run_id,[])
                if event.sequence>after_sequence
            ]