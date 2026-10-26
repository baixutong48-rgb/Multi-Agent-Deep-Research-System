from typing import Any

from src.observability.events import (
    TraceEvent,
    TraceEventType,
)

from src.observability.store import TraceStore

from src.runtime.context import (
    get_runtime_context,
)

class ResearchTracer:

    def __init__(self,store: TraceStore,) -> None:
        self.store = store

    async def emit(self,event_type: TraceEventType,*,actor: str | None = None,name: str | None = None,metadata: dict[str, Any] | None = None,
    ) -> TraceEvent:

        context = get_runtime_context()
        return await self.store.create_event(
            run_id=context.run_id,
            event_type=event_type,
            actor=actor,
            name=name,
            metadata=metadata,
        )