from dataclasses import dataclass
from typing import Protocol


@dataclass
class ScenarioResponse:
    text: str
    current_node: str
    is_complete: bool
    is_emergency: bool
    slots: dict


class ScenarioRunner(Protocol):
    def process(self, user_input: str) -> ScenarioResponse:
        """Process user input and return a response."""

    def get_state(self) -> dict:
        """Return current scenario state for debugging or storage."""

    def reset(self) -> None:
        """Reset scenario to initial state."""
