"""Thread-safe application state manager and real-time log event broadcaster.

Maintains live server status, background execution flags, user authentication info,
and server-sent events (SSE) log streaming queue.
"""

import asyncio
from datetime import datetime
from typing import Any


class AppStateManager:
    """Encapsulate runtime application state and log broadcasting."""

    def __init__(self, max_logs_history: int = 2500) -> None:
        """Initialize state parameters and lock primitives.

        :param max_logs_history: Maximum number of recent log lines retained in memory.
        """
        self.auth_status: str = "unknown"
        self.user_info: dict[str, Any] | None = None
        self.qr_img_base64: str | None = None
        self.qr_login_obj: Any = None
        self.task_running: bool = False
        self.task_type: str | None = None
        self.task_progress: dict[str, Any] | None = None

        self._max_logs_history = max_logs_history
        self._logs_buffer: list[str] = []
        self._subscribers: list[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    def log_event(self, message: str) -> None:
        """Append an event to the circular log buffer and broadcast to SSE subscribers.

        :param message: Human-readable log or progress text.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_formatted = f"[{timestamp}] {message}"
        self._logs_buffer.append(message_formatted)

        if len(self._logs_buffer) > self._max_logs_history:
            self._logs_buffer.pop(0)

        # Notify active streaming queues
        for subscriber_queue in list(self._subscribers):
            try:
                subscriber_queue.put_nowait(message_formatted)
            except asyncio.QueueFull:
                pass

    def get_recent_logs(self) -> list[str]:
        """Return a copy of recent log messages.

        :return: List of formatted timestamped log strings.
        """
        return list(self._logs_buffer)

    def subscribe_logs(self) -> asyncio.Queue:
        """Create and register a new event queue for SSE streaming.

        :return: asyncio.Queue receiving live string log messages.
        """
        subscriber_queue: asyncio.Queue = asyncio.Queue(maxsize=500)
        self._subscribers.append(subscriber_queue)
        return subscriber_queue

    def unsubscribe_logs(self, subscriber_queue: asyncio.Queue) -> None:
        """Remove a subscriber queue when client disconnects.

        :param subscriber_queue: Previously registered queue to remove.
        """
        if subscriber_queue in self._subscribers:
            self._subscribers.remove(subscriber_queue)

    def reset_auth(self) -> None:
        """Reset authentication properties to unauthorized defaults."""
        self.auth_status = "unauthorized"
        self.user_info = None
        self.qr_img_base64 = None
        self.qr_login_obj = None

    def set_task_started(self, task_type: str) -> None:
        """Mark background task as running.

        :param task_type: Identifier of the task (e.g., 'fetch' or 'analyze').
        """
        self.task_running = True
        self.task_type = task_type
        self.task_progress = None

    def set_task_finished(self) -> None:
        """Clear background task status flags upon completion."""
        self.task_running = False
        self.task_type = None
        self.task_progress = None


# Shared application state singleton
state_manager = AppStateManager()
