import datetime
from typing import Any, Protocol

from src.observability.events import TraceEventType
from src.observability.tracer import ResearchTracer
from src.runtime.context import bind_runtime_context
from src.runtime.identity import RuntimeIdentity
from src.runtime.models import ResearchRun, RunStatus
from src.runtime.store import RunStore
from src.observability.deepagents_adapter import DeepAgentTraceAdapter
from src.agents.factory import ResearchAgentFactory
from src.runtime.workspace import WorkspaceFactory

class ResearchAgent(Protocol):
    async def ainvoke(self,input:dict[str,Any],config:dict[str,Any]|None=None)->dict[str,Any]:
        ...

class ResearchRunner:
    def __init__(self,*,agent_factory:ResearchAgentFactory,workspace_factory: WorkspaceFactory,run_store:RunStore,tracer:ResearchTracer) -> None:
        self.agent_factory=agent_factory
        self.run_store=run_store
        self.tracer=tracer
        self.workspace_factory = workspace_factory

    async def execute(self,identity: RuntimeIdentity,query:str):
        run = await self.run_store.get(identity.run_id)
        if run is None:
            raise RuntimeError(f"Run 不存在: {identity.run_id}")
        adapter=DeepAgentTraceAdapter()
        with bind_runtime_context(identity):
            try:
                workspace = self.workspace_factory.create(identity)
                agent = self.agent_factory.create(workspace=workspace)
                run.status = RunStatus.RUNNING
                run.started = datetime.datetime.now(datetime.timezone.utc)
                await self.run_store.update(run)
                await self.tracer.emit(TraceEventType.RUN_STARTED)
                async for raw_event in agent.astream({
                    'messages':[{'role':'user','content':query}]
                },config={'configurable':{'thread_id':identity.thread_id}},stream_mode='updates',subgraphs=True):
                    adapted_events = adapter.adapt(raw_event)
                    for event in adapted_events:
                        await self.tracer.emit(
                            event_type=event.event_type,
                            actor=event.actor,
                            name=event.name,
                            metadata=event.metadata,
                    )

                final_result = self._extract_final_content( raw_event=raw_event,
                    current=final_content,)
                run.status = RunStatus.COMPLETED
                run.result = final_result
                run.completed_at = datetime.datetime.now(datetime.timezone.utc)
                await self.run_store.update(run)

                await self.tracer.emit(TraceEventType.RUN_COMPLETED)
            except Exception as exc:
                run.status = RunStatus.FAILED
                run.error = self._safe_error_message(
                    exc
                )
                run.completed_at = datetime.datetime.now(datetime.timezone.utc)

                await self.run_store.update(run)

                await self.tracer.emit(
                    TraceEventType.RUN_FAILED,
                    metadata={
                        "error_type": (
                            type(exc).__name__
                        )
                    },
                )

    async def create_run(self,*,identity: RuntimeIdentity,query: str,) -> ResearchRun:

        run = ResearchRun(
            run_id=identity.run_id,
            thread_id=identity.thread_id,
            query=query,
    )

        await self.run_store.create(run)
        return run

    @staticmethod
    def _extract_final_result(result: dict[str, Any],) -> str:

        messages = result.get("messages")

        if not messages:
            raise RuntimeError("Agent 没有返回消息")

        last_message = messages[-1]

        content = getattr(last_message,"content",None,)

        if content is None and isinstance(last_message,dict,):
            content = last_message.get("content")

        if not isinstance(content, str):
            raise RuntimeError("Agent 最终消息格式不正确")

        return content

    @staticmethod
    def _safe_error_message(exc: Exception,) -> str:
        return (
            "研究任务执行失败。"
            f"错误类型: {type(exc).__name__}"
        )

    @staticmethod
    def _extract_final_content(
    *,
    raw_event,
    current: str | None,
) -> str | None:
        if not isinstance(raw_event, tuple):
            return current

        namespace, update = raw_event

    # 只接受 Main Agent / root graph
        if namespace:
            return current

        model_update = update.get("model")

        if not model_update:
            return current

        for message in model_update.get("messages", []):
            if not isinstance(message, AIMessage):
                continue

        # tool call 阶段不是最终回答
            if message.tool_calls:
                continue

        if isinstance(message.content, str) and message.content:
            current = message.content

        return current
