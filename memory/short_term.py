# memory/short_term.py

from typing import List, Dict, Any
from collections import deque


MAX_HISTORY = 10  # keep last 10 exchanges


class ShortTermMemory:
    """
    Stores conversation history for current session.
    Automatically trims to MAX_HISTORY exchanges.
    """

    def __init__(self):
        self.history  : deque         = deque(maxlen=MAX_HISTORY)
        self.context  : Dict[str, Any] = {}   # active company, year, etc.


    def add(self, role: str, content: str) -> None:
        """Add a message. role = 'user' or 'assistant'."""
        self.history.append({"role": role, "content": content})


    def get_history(self) -> List[Dict[str, str]]:
        """Return full conversation history as list."""
        return list(self.history)


    def set_context(self, key: str, value: str) -> None:
        """Store active context like company, year, section."""
        self.context[key] = value


    def get_context(self, key: str) -> Any:
        """Retrieve a context value."""
        return self.context.get(key, None)


    def get_full_context(self) -> Dict[str, Any]:
        """Return all stored context."""
        return self.context


    def clear(self) -> None:
        """Reset memory for new session."""
        self.history.clear()
        self.context.clear()


    def summary(self) -> str:
        """Return last 3 messages as a quick summary string."""
        recent = list(self.history)[-3:]
        return "\n".join(f"{m['role'].upper()}: {m['content']}" for m in recent)


# --- Quick test ---
if __name__ == "__main__":
    mem = ShortTermMemory()

    mem.add("user",      "Analyze Tesla revenue for 2024")
    mem.add("assistant", "Tesla revenue for 2024 was $81.4B")
    mem.add("user",      "Compare with last year")

    # auto-fills company from context
    mem.set_context("company", "Tesla")
    mem.set_context("year",    "2024")

    print("History:")
    for m in mem.get_history():
        print(f"  {m['role']}: {m['content']}")

    print(f"\nActive company : {mem.get_context('company')}")
    print(f"Active year    : {mem.get_context('year')}")
    print(f"\nSummary:\n{mem.summary()}")