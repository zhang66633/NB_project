"""WebSocket endpoints for real-time agent progress."""

import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..config import get_settings
from ..services.redis_pubsub import RedisSubscriber

logger = logging.getLogger(__name__)
ws_router = APIRouter()


@ws_router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time task message streaming.

    Subscribes to Redis Pub/Sub channel ``task:{task_id}`` and forwards
    every published event to the connected frontend client.
    """
    await websocket.accept()
    settings = get_settings()

    # Send an initial connection-confirmation event
    await websocket.send_text(json.dumps({
        "event": "connected",
        "task_id": task_id,
    }, ensure_ascii=False))

    subscriber = RedisSubscriber(settings.redis_url)

    try:
        async for event_json in subscriber.subscribe(task_id):
            try:
                await websocket.send_text(event_json)
            except Exception:
                # Client disconnected — stop consuming
                break
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected for task %s", task_id)
    except asyncio.CancelledError:
        logger.info("WebSocket cancelled for task %s", task_id)
    except Exception:
        logger.exception("WebSocket error for task %s", task_id)
