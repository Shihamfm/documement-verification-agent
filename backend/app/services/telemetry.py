import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Set, Any, AsyncGenerator, Optional
import sys
from pathlib import Path
for _p in Path(__file__).resolve().parents:
    if (_p / 'backend').is_dir() and (_p / 'pyproject.toml').is_file():
        if str(_p) not in sys.path:
            sys.path.insert(0, str(_p))
        break

from backend.app.core.logger import logger


class TelemetryBroadcaster:
    """In-memory event hub for Server-Sent Events (SSE) and WebSockets."""

    def __init__(self) -> None:
        # job_id -> set of asyncio.Queue
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, job_id: str) -> asyncio.Queue:
        """Register a subscriber queue for a specific job."""
        async with self._lock:
            if job_id not in self._subscribers:
                self._subscribers[job_id] = set()
            q: asyncio.Queue = asyncio.Queue()
            self._subscribers[job_id].add(q)
            logger.debug(f"Client subscribed to job {job_id} telemetry. Total listeners: {len(self._subscribers[job_id])}")
            return q

    async def unsubscribe(self, job_id: str, q: asyncio.Queue) -> None:
        """Unregister a subscriber queue."""
        async with self._lock:
            if job_id in self._subscribers and q in self._subscribers[job_id]:
                self._subscribers[job_id].remove(q)
                if not self._subscribers[job_id]:
                    del self._subscribers[job_id]

    async def emit_event(
        self,
        job_id: str,
        stage_name: str,
        status: str,
        progress: int,
        metadata: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Broadcasts a telemetry stage update event to all active listeners."""
        event_payload = {
            "job_id": job_id,
            "stage_name": stage_name,
            "status": status,
            "progress_percentage": progress,
            "metadata": metadata or {},
            "error_message": error_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        async with self._lock:
            queues = list(self._subscribers.get(job_id, []))

        for q in queues:
            try:
                await q.put(event_payload)
            except Exception as e:
                logger.warning(f"Error publishing to SSE queue for job {job_id}: {e}")

    async def sse_event_generator(self, job_id: str, initial_state: Optional[Dict[str, Any]] = None) -> AsyncGenerator[str, None]:
        """Async generator yielding SSE formatted strings for FastAPI StreamingResponse."""
        q = await self.subscribe(job_id)
        try:
            # Send initial state immediately so client gets status on refresh
            if initial_state:
                yield f"data: {json.dumps(initial_state)}\n\n"

            while True:
                try:
                    # Timeout periodically to send keep-alive comment
                    event = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    # If job terminal state, close generator
                    if event.get("stage_name") == "done" or event.get("status") in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat ping to prevent connection drops
                    yield ": ping\n\n"
        finally:
            await self.unsubscribe(job_id, q)


telemetry_hub = TelemetryBroadcaster()
