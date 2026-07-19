"""WebSocket endpoints for real-time agent progress."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()


@ws_router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time task message streaming."""
    await websocket.accept()

    try:
        # TODO: Subscribe to Redis channel task:{task_id}
        # For now, a placeholder that echoes back messages
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        pass
