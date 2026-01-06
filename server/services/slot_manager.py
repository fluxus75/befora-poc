from dataclasses import dataclass, field
from typing import Any


@dataclass
class SlotManager:
    _slots: dict[str, Any] = field(default_factory=dict)
    _allowed: set[str] | None = None

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
        allowed: set[str] | None = None,
    ) -> None:
        self._slots = dict(initial or {})
        self._allowed = allowed

    def get(self, key: str, default: Any = None) -> Any:
        return self._slots.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if self._allowed is not None and key not in self._allowed:
            return
        self._slots[key] = value

    def update(self, updates: dict[str, Any]) -> None:
        for key, value in updates.items():
            self.set(key, value)

    def as_dict(self) -> dict[str, Any]:
        return dict(self._slots)

    def reset(self, initial: dict[str, Any] | None = None) -> None:
        self._slots = dict(initial or {})
