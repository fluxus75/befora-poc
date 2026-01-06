from __future__ import annotations

import json
import re
import string
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class EmergencyMatch:
    match_type: str
    category: str
    trigger_id: str
    keyword: str


_PUNCTUATION = ".,!?/\\-()[]{}<>:;\"'`~@#$%^&*_+=|"
_PUNCTUATION_TABLE = str.maketrans({ch: " " for ch in _PUNCTUATION})


def _strip_punctuation(text: str) -> str:
    return text.translate(_PUNCTUATION_TABLE)


def normalize_text(text: str, rules: dict[str, Any], keep_spaces: bool = False) -> str:
    normalized = text
    if rules.get("strip_punctuation"):
        normalized = _strip_punctuation(normalized)
    if rules.get("trim_whitespace"):
        normalized = normalized.strip()
    if not rules.get("case_sensitive", True):
        normalized = normalized.lower()
    if rules.get("korean_spacing_variants") and not keep_spaces:
        normalized = normalized.replace(" ", "")
    return normalized


class EmergencyDetector:
    def __init__(self, keywords_path: str | Path):
        data = json.loads(Path(keywords_path).read_text(encoding="utf-8"))
        self.normalization = data.get("normalization", {})
        self.strong_red_flags = data.get("strong_red_flags", [])
        self.fallback_triggers = data.get("fallback_triggers", [])

    def detect(self, user_input: str) -> EmergencyMatch | None:
        normalized_input = normalize_text(user_input, self.normalization)
        spaced_input = normalize_text(user_input, self.normalization, keep_spaces=True)
        match = self._match_list(normalized_input, spaced_input, self.strong_red_flags)
        if match:
            return EmergencyMatch(
                match_type="strong_red_flag",
                category=match["category"],
                trigger_id=match["id"],
                keyword=match["keyword"],
            )
        match = self._match_list(normalized_input, spaced_input, self.fallback_triggers)
        if match:
            return EmergencyMatch(
                match_type="fallback_trigger",
                category=match["category"],
                trigger_id=match["id"],
                keyword=match["keyword"],
            )
        return None

    def _match_list(
        self,
        normalized_input: str,
        spaced_input: str,
        triggers: list[dict[str, Any]],
    ) -> dict[str, str] | None:
        for trigger in triggers:
            for keyword in trigger.get("keywords", []):
                if self._matches_keyword(keyword, normalized_input, spaced_input):
                    return {
                        "id": trigger.get("id", ""),
                        "category": trigger.get("category", ""),
                        "keyword": keyword,
                    }
        return None

    def _matches_keyword(
        self,
        keyword: str,
        normalized_input: str,
        spaced_input: str,
    ) -> bool:
        spaced_keyword = normalize_text(keyword, self.normalization, keep_spaces=True)
        if not spaced_keyword:
            return False
        if " " in spaced_keyword:
            tokens = [token for token in spaced_keyword.split(" ") if token]
            if not tokens:
                return False
            pattern = ".*".join(re.escape(token) for token in tokens)
            return re.search(pattern, spaced_input) is not None
        normalized_keyword = normalize_text(keyword, self.normalization)
        return normalized_keyword in normalized_input


class EmergencyFlowRunner:
    def __init__(self, flow_path: str | Path):
        data = json.loads(Path(flow_path).read_text(encoding="utf-8"))
        self.scripts = data.get("scripts", [])
        self._steps: list[dict[str, Any]] = []
        self._index = 0
        self._pending_question: dict[str, Any] | None = None

    def start(self, match: EmergencyMatch) -> None:
        script = self._select_script(match)
        self._steps = list(script.get("steps", [])) if script else []
        self._index = 0
        self._pending_question = None

    def is_active(self) -> bool:
        return bool(self._steps)

    def next(self, user_input: str, slot_setter: callable) -> tuple[str, bool]:
        if self._pending_question:
            self._save_answer(user_input, self._pending_question, slot_setter)
            self._pending_question = None
            self._index += 1

        messages: list[str] = []
        while self._index < len(self._steps):
            step = self._steps[self._index]
            step_type = step.get("type")
            if step_type == "message":
                text = step.get("text", "")
                if text:
                    messages.append(text)
                self._index += 1
                continue
            if step_type == "question":
                text = step.get("text", "")
                if messages and text:
                    text = "\n".join(messages + [text])
                elif messages:
                    text = "\n".join(messages)
                self._pending_question = step
                return text, False
            self._index += 1

        if messages:
            return "\n".join(messages), True
        return "", True

    def _select_script(self, match: EmergencyMatch) -> dict[str, Any] | None:
        def matches(script: dict[str, Any]) -> bool:
            use_when = script.get("use_when", {})
            if use_when.get("match_type") != match.match_type:
                return False
            categories = use_when.get("any_category", [])
            return not categories or match.category in categories

        for script in self.scripts:
            if matches(script):
                return script
        for script in self.scripts:
            if script.get("use_when", {}).get("match_type") == match.match_type:
                return script
        return self.scripts[0] if self.scripts else None

    def _save_answer(self, user_input: str, step: dict[str, Any], slot_setter: callable) -> None:
        slot = step.get("slot")
        expected = step.get("expected")
        value = self._extract_expected(user_input, expected)
        if slot:
            slot_setter(slot, value)

    @staticmethod
    def _extract_expected(user_input: str, expected: str | None) -> Any:
        text = user_input.strip()
        if not expected:
            return text or None
        if expected == "yes_no":
            lowered = text.lower()
            yes_tokens = ("네", "예", "응", "맞", "그래")
            no_tokens = ("아니", "아니요", "아뇨", "싫", "못")
            if any(token in lowered for token in yes_tokens):
                return True
            if any(token in lowered for token in no_tokens):
                return False
            return None
        if expected == "yes_no_or_free_text":
            value = EmergencyFlowRunner._extract_expected(text, "yes_no")
            return value if isinstance(value, bool) else (text or None)
        return text or None
