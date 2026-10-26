from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.api.dependencies import get_runtime

router = APIRouter()

@router.websocket("/research/{run_id}/stream")
async def research_stream(websocket: WebSocket,run_id: str,
) -> None:
    runtime = get_runtime(websocket)

    run = await runtime.run_store.get(run_id)

    if run is None:
        await websocket.close(
            code=4404,
            reason="Research run not found",
        )
        return

    after_sequence = _parse_after_sequence(websocket)

    await websocket.accept()

    last_sequence = after_sequence

    try:
        while True:
            events = await runtime.trace_store.list_after(
                run_id=run_id,
                after_sequence=last_sequence,
            )

            for event in events:
                await websocket.send_json(
                    event.model_dump(mode="json")
                )

                last_sequence = event.sequence

            run = await runtime.run_store.get(run_id)

            if run is None:
                await websocket.close(
                    code=1011,
                    reason="Research run disappeared",
                )
                return

            if _is_terminal(run.status):
                await websocket.close(code=1000)
                return

            events = await runtime.trace_store.wait_for_events(
                run_id=run_id,
                after_sequence=last_sequence,
            )

            for event in events:
                await websocket.send_json(
                    event.model_dump(mode="json")
                )

                last_sequence = event.sequence

    except WebSocketDisconnect:
        return


def _parse_after_sequence(websocket: WebSocket) -> int:
    value = websocket.query_params.get(
        "after_sequence",
        "0",
    )

    try:
        sequence = int(value)
    except ValueError:
        return 0

    return max(sequence, 0)

def _is_terminal(status) -> bool:
    value = getattr(status, "value", status)

    return value in {
        "completed",
        "failed",
        "cancelled",
    }