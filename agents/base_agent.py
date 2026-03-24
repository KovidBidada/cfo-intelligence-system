# agents/base_agent.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from memory.short_term import ShortTermMemory


class BaseAgent(ABC):
    """
    Base class for all CFO agents.
    Every agent inherits this and implements run().
    """

    def __init__(self, name: str, memory: Optional[ShortTermMemory] = None):
        self.name   = name
        self.memory = memory or ShortTermMemory()


    @abstractmethod
    def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Execute the agent task.
        Must return a dict with at least:
        { "agent", "result", "status" }
        """
        pass


    def remember(self, role: str, content: str) -> None:
        """Save message to short-term memory."""
        self.memory.add(role, content)


    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history."""
        return self.memory.get_history()


    def get_context(self, key: str) -> Any:
        """Get a context value."""
        return self.memory.get_context(key)


    def set_context(self, key: str, value: str) -> None:
        """Set a context value."""
        self.memory.set_context(key, value)


    def success(self, result: Any) -> Dict[str, Any]:
        """Standard success response."""
        return {
            "agent" : self.name,
            "status": "success",
            "result": result,
        }


    def failure(self, error: str) -> Dict[str, Any]:
        """Standard failure response."""
        return {
            "agent" : self.name,
            "status": "error",
            "result": None,
            "error" : error,
        }


    def __repr__(self) -> str:
        return f"<Agent: {self.name}>"


# --- Quick test ---
if __name__ == "__main__":

    # Concrete test agent
    class TestAgent(BaseAgent):
        def run(self, query: str, context: Dict[str, Any] = {}) -> Dict[str, Any]:
            return self.success(f"Processed: {query}")

    agent = TestAgent(name="TestAgent")
    agent.set_context("company", "Tesla")

    print(agent.run("Analyze revenue"))
    print(f"Company context : {agent.get_context('company')}")
    print(f"History         : {agent.get_history()}")