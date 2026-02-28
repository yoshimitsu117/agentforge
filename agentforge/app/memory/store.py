"""AgentForge — Conversation Memory Store."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ConversationEntry:
    """A single entry in conversation memory."""

    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: dict = field(default_factory=dict)


class MemoryStore:
    """In-memory conversation store with session management.

    Stores conversation history per session, enabling agents
    to maintain context across multiple workflow runs.
    """

    def __init__(self):
        self._sessions: dict[str, list[ConversationEntry]] = {}

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict | None = None,
    ) -> None:
        """Add a message to a session's history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        entry = ConversationEntry(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self._sessions[session_id].append(entry)
        logger.debug(f"Memory: added {role} message to session {session_id}")

    def get_history(
        self, session_id: str, last_n: int | None = None
    ) -> list[dict]:
        """Get conversation history for a session.

        Args:
            session_id: Session identifier.
            last_n: If set, return only the last N messages.

        Returns:
            List of message dicts.
        """
        entries = self._sessions.get(session_id, [])
        if last_n is not None:
            entries = entries[-last_n:]
        return [asdict(e) for e in entries]

    def get_context_string(
        self, session_id: str, last_n: int = 10
    ) -> str:
        """Get conversation history as a formatted string."""
        history = self.get_history(session_id, last_n=last_n)
        parts = []
        for msg in history:
            parts.append(f"[{msg['role']}]: {msg['content'][:300]}")
        return "\n".join(parts)

    def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session."""
        self._sessions.pop(session_id, None)
        logger.info(f"Cleared memory for session {session_id}")

    def list_sessions(self) -> list[str]:
        """List all active session IDs."""
        return list(self._sessions.keys())

    @property
    def total_messages(self) -> int:
        return sum(len(entries) for entries in self._sessions.values())


# Global memory instance
memory = MemoryStore()
