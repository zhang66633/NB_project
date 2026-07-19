"""Redis Pub/Sub service — decouples agent execution from WebSocket message delivery.

Architecture:
  Agent nodes (synchronous)  ──publish──▶  Redis channel  ──subscribe──▶  WebSocket endpoint

This keeps the LangGraph StateGraph nodes lightweight (fire-and-forget publish)
while the async WebSocket endpoint consumes events streamingly.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

import redis.asyncio as aioredis
import redis as sync_redis

from app.config import get_settings

logger = logging.getLogger(__name__)

# ── Event types ──────────────────────────────────────────────────────


class ProgressEvent:
    """Standard event envelope sent over Redis."""

    NODE_START = "node_start"
    NODE_END = "node_end"
    PROGRESS = "progress"
    ERROR = "error"

    def __init__(
        self,
        event: str,
        node: str,
        task_id: str,
        data: Optional[dict] = None,
    ):
        self.event = event
        self.node = node
        self.task_id = task_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.data = data or {}

    def to_json(self) -> str:
        return json.dumps(
            {
                "event": self.event,
                "node": self.node,
                "task_id": self.task_id,
                "timestamp": self.timestamp,
                "data": self.data,
            },
            ensure_ascii=False,
        )

    @staticmethod
    def channel_for(task_id: str) -> str:
        return f"task:{task_id}"


# ── Synchronous publisher (called from LangGraph nodes) ──────────────


class RedisPublisher:
    """Synchronous Redis publisher for use inside LangGraph nodes.

    Nodes run in a thread-pool (via asyncio.to_thread), so a sync client is
    cleaner than mixing asyncio loops.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[sync_redis.Redis] = None

    @property
    def client(self) -> sync_redis.Redis:
        if self._client is None:
            self._client = sync_redis.Redis.from_url(
                self.redis_url, decode_responses=True
            )
        return self._client

    def publish(self, task_id: str, event: str, node: str, data: Optional[dict] = None) -> int:
        """Publish an event to the task's channel.

        Returns the number of subscribers that received the message.
        """
        msg = ProgressEvent(event=event, node=node, task_id=task_id, data=data)
        channel = ProgressEvent.channel_for(task_id)
        try:
            return self.client.publish(channel, msg.to_json())
        except Exception:
            logger.warning("Failed to publish event to channel %s", channel, exc_info=True)
            return 0

    def node_start(self, task_id: str, node: str, data: Optional[dict] = None) -> int:
        """Shorthand for publishing a node_start event."""
        return self.publish(task_id, ProgressEvent.NODE_START, node, data)

    def node_end(self, task_id: str, node: str, data: Optional[dict] = None) -> int:
        """Shorthand for publishing a node_end event."""
        return self.publish(task_id, ProgressEvent.NODE_END, node, data)

    def progress(self, task_id: str, node: str, data: Optional[dict] = None) -> int:
        """Shorthand for publishing a progress event."""
        return self.publish(task_id, ProgressEvent.PROGRESS, node, data)

    def error(self, task_id: str, node: str, error_msg: str) -> int:
        """Shorthand for publishing an error event."""
        return self.publish(task_id, ProgressEvent.ERROR, node, {"message": error_msg})

    def close(self):
        if self._client:
            self._client.close()
            self._client = None


# ── Asynchronous subscriber (consumed by WebSocket) ──────────────────


class RedisSubscriber:
    """Async Redis subscriber that yields events as an async generator.

    Usage in a WebSocket endpoint:

        subscriber = RedisSubscriber(redis_url)
        async for event_json in subscriber.subscribe(task_id):
            await websocket.send_text(event_json)
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url

    async def subscribe(self, task_id: str) -> AsyncGenerator[str, None]:
        """Subscribe to a task channel and yield event JSON strings."""
        try:
            client = aioredis.Redis.from_url(
                self.redis_url, decode_responses=True
            )
            pubsub = client.pubsub()
            channel = ProgressEvent.channel_for(task_id)

            await pubsub.subscribe(channel)
            logger.info("Subscribed to Redis channel: %s", channel)

            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        yield message["data"]
            finally:
                await pubsub.unsubscribe(channel)
                await client.aclose()
        except Exception:
            logger.warning(
                "Redis subscriber for task %s disconnected", task_id, exc_info=True
            )
            # Yield nothing on connection failure — WebSocket will close cleanly


# ── Module-level publisher singleton ─────────────────────────────────

_publisher: Optional[RedisPublisher] = None


def get_publisher() -> RedisPublisher:
    """Get or create the global sync Redis publisher."""
    global _publisher
    if _publisher is None:
        settings = get_settings()
        _publisher = RedisPublisher(settings.redis_url)
    return _publisher


def shutdown_publisher():
    """Close the global publisher (call on app shutdown)."""
    global _publisher
    if _publisher:
        _publisher.close()
        _publisher = None
