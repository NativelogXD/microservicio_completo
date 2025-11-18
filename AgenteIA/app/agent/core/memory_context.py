import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ConversationMessage:
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not self.timestamp:
            self.timestamp = time.time()


class MemoryContext:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._messages: List[ConversationMessage] = []

    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self._messages.append(ConversationMessage(role=role, content=content, metadata=metadata))
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_recent_messages(self, n: Optional[int] = None, count: Optional[int] = None) -> List[ConversationMessage]:
        c = count if count is not None else n if n is not None else 0
        if c <= 0:
            return []
        return self._messages[-c:]

    def get_context_for_llm(self, include_system: bool = False, max_messages_override: Optional[int] = None) -> List[Dict[str, str]]:
        limit = max_messages_override or self.max_messages
        msgs = self._messages[-limit:]
        out: List[Dict[str, str]] = []
        for m in msgs:
            out.append({"role": m.role.value, "content": m.content})
        return out