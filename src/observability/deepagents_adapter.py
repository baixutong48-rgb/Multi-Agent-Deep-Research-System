from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage


@dataclass(frozen=True)
class AdaptedTraceEvent:
    event_type: str
    actor: str | None = None
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DeepAgentTraceAdapter:
    def __init__(self) -> None:
        self._delegations: dict[str, str] = {}

    def adapt(self,raw_event: tuple[tuple[str, ...], dict[str, Any]],
    ) -> list[AdaptedTraceEvent]:
        namespace, update = raw_event

        events: list[AdaptedTraceEvent] = []

        if not update:
            return events

        model_update = update.get("model")
        if model_update:
            events.extend(
                self._adapt_model_update(
                    namespace=namespace,
                    update=model_update,
                )
            )

        tools_update = update.get("tools")
        if tools_update:
            events.extend(
                self._adapt_tools_update(
                    namespace=namespace,
                    update=tools_update,
                )
            )

        return events

    def _adapt_model_update(self,*,namespace: tuple[str, ...],update: dict[str, Any],
    ) -> list[AdaptedTraceEvent]:
        events: list[AdaptedTraceEvent] = []

        for message in update.get("messages", []):
            if not isinstance(message, AIMessage):
                continue

            actor = self._resolve_actor(
                namespace=namespace,
                message_name=message.name,
            )

            for tool_call in message.tool_calls:
                event = self._adapt_tool_call(
                    actor=actor,
                    tool_call=tool_call,
                )

                if event is not None:
                    events.append(event)

            if message.content and not message.tool_calls:
                events.append(
                    AdaptedTraceEvent(
                        event_type="AGENT_MESSAGE",
                        actor=actor,
                        metadata={
                            "content": message.content,
                        },
                    )
                )

        return events

    def _adapt_tool_call(self,*,actor: str,tool_call: dict[str, Any],
    ) -> AdaptedTraceEvent | None:
        name = tool_call.get("name")
        args = tool_call.get("args", {})
        call_id = tool_call.get("id")

        if not name:
            return None

        if name == "task":
            subagent_type = args.get("subagent_type")

            if call_id and subagent_type:
                self._delegations[call_id] = subagent_type

            return AdaptedTraceEvent(
                event_type="SUBAGENT_STARTED",
                actor=subagent_type,
                name=subagent_type,
                metadata={
                    "call_id": call_id,
                    "description": args.get("description"),
                    "delegated_by": actor,
                },
            )

        return AdaptedTraceEvent(
            event_type="TOOL_STARTED",
            actor=actor,
            name=name,
            metadata={
                "call_id": call_id,
                "args": args,
            },
        )

    def _adapt_tools_update(self,*,namespace: tuple[str, ...],update: dict[str, Any],
    ) -> list[AdaptedTraceEvent]:
        events: list[AdaptedTraceEvent] = []

        for message in update.get("messages", []):
            if not isinstance(message, ToolMessage):
                continue

            if message.name == "task":
                subagent_type = self._delegations.pop(
                    message.tool_call_id,
                    None,
                )

                events.append(
                    AdaptedTraceEvent(
                        event_type="SUBAGENT_COMPLETED",
                        actor=subagent_type,
                        name=subagent_type,
                        metadata={
                            "call_id": message.tool_call_id,
                        },
                    )
                )
                continue

            events.append(
                AdaptedTraceEvent(
                    event_type="TOOL_COMPLETED",
                    actor=self._resolve_actor(
                        namespace=namespace,
                        message_name=None,
                    ),
                    name=message.name,
                    metadata={
                        "call_id": message.tool_call_id,
                    },
                )
            )

        return events

    @staticmethod
    def _resolve_actor(*,namespace: tuple[str, ...],message_name: str | None,
    ) -> str:
        if message_name:
            return message_name

        if not namespace:
            return "main_agent"

        return "subagent"