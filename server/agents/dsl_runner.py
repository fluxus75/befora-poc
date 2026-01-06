from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from server.agents.base import ScenarioResponse
from server.agents.emergency import EmergencyDetector, EmergencyFlowRunner, EmergencyMatch
from server.agents.router import route_symptom_track
from server.agents.scenario_loader import ScenarioDefinition, load_scenario
from server.services.slot_manager import SlotManager


@dataclass
class _TransitionResult:
    next_node: str
    updates: dict[str, Any]


class DSLScenarioRunner:
    def __init__(
        self,
        scenario_path: str | Path,
        emergency_keywords_path: str | Path | None = None,
        emergency_flow_path: str | Path | None = None,
    ):
        self.scenario: ScenarioDefinition = load_scenario(scenario_path)
        self.slot_manager = SlotManager(
            initial=dict(self.scenario.slots),
            allowed=set(self.scenario.slots.keys()),
        )
        self.current_node = self.scenario.start_node
        self.last_node: str | None = None
        self._temp_vars: dict[str, Any] = {}
        self._retry_count = 0

        self._emergency_detector: EmergencyDetector | None = None
        self._emergency_flow: EmergencyFlowRunner | None = None
        self._active_emergency: EmergencyMatch | None = None
        if emergency_keywords_path:
            self._emergency_detector = EmergencyDetector(emergency_keywords_path)
        if emergency_flow_path:
            self._emergency_flow = EmergencyFlowRunner(emergency_flow_path)

    def process(self, user_input: str) -> ScenarioResponse:
        text_input = user_input.strip()
        if self._active_emergency:
            return self._process_emergency(text_input)

        if not text_input:
            prompt, node_id, done = self._advance_until_question(self.current_node)
            self.current_node = node_id
            return ScenarioResponse(
                text=prompt,
                current_node=node_id,
                is_complete=done,
                is_emergency=False,
                slots=self.slot_manager.as_dict(),
            )

        if self._emergency_detector and self.scenario.emergency.get("enabled", True):
            match = self._emergency_detector.detect(text_input)
            if match:
                return self._start_emergency(match)

        node = self._get_node(self.current_node)
        if node.get("type") == "question":
            self._extract_slots(text_input, node)
        transition = self._evaluate_transitions(node)
        self._apply_updates(transition.updates)
        self.last_node = self.current_node
        self.current_node = transition.next_node
        prompt, node_id, done = self._advance_until_question(self.current_node)
        self.current_node = node_id
        return ScenarioResponse(
            text=prompt,
            current_node=node_id,
            is_complete=done,
            is_emergency=False,
            slots=self.slot_manager.as_dict(),
        )

    def get_state(self) -> dict:
        return {
            "current_node": self.current_node,
            "last_node": self.last_node,
            "slots": self.slot_manager.as_dict(),
            "temp_vars": dict(self._temp_vars),
            "emergency_active": self._active_emergency is not None,
        }

    def reset(self) -> None:
        self.current_node = self.scenario.start_node
        self.last_node = None
        self.slot_manager.reset(self.scenario.slots)
        self._temp_vars = {}
        self._active_emergency = None
        self._retry_count = 0

    def _process_emergency(self, user_input: str) -> ScenarioResponse:
        if not self._active_emergency or not self._emergency_flow:
            return ScenarioResponse(
                text="",
                current_node=self.current_node,
                is_complete=True,
                is_emergency=True,
                slots=self.slot_manager.as_dict(),
            )
        text, done = self._emergency_flow.next(user_input, self.slot_manager.set)
        if done:
            self._active_emergency = None
        return ScenarioResponse(
            text=text,
            current_node="EMERGENCY_FLOW",
            is_complete=done,
            is_emergency=True,
            slots=self.slot_manager.as_dict(),
        )

    def _start_emergency(self, match: EmergencyMatch) -> ScenarioResponse:
        self._active_emergency = match
        if self._emergency_flow:
            self._emergency_flow.start(match)
            return self._process_emergency("")
        return ScenarioResponse(
            text="",
            current_node="EMERGENCY_FLOW",
            is_complete=True,
            is_emergency=True,
            slots=self.slot_manager.as_dict(),
        )

    def _advance_until_question(self, node_id: str) -> tuple[str, str, bool]:
        messages: list[str] = []
        current = node_id
        while True:
            node = self._get_node(current)
            node_type = node.get("type")
            if node_type == "system":
                current = self._next_node_from_transitions(node).next_node
                continue
            if node_type == "message":
                text = node.get("text", "")
                if text:
                    messages.append(text)
                current = self._next_node_from_transitions(node).next_node
                continue
            if node_type == "router":
                current = self._route_node(node)
                continue
            if node_type == "end":
                return ("\n".join(messages) if messages else node.get("text", "")), current, True
            if node_type == "question":
                prompt = node.get("text", "")
                if messages and prompt:
                    prompt = "\n".join(messages + [prompt])
                elif messages:
                    prompt = "\n".join(messages)
                return prompt, current, False
            return "\n".join(messages), current, False

    def _route_node(self, node: dict[str, Any]) -> str:
        router_name = node.get("router")
        if router_name == "symptom_track":
            chief_complaint = self.slot_manager.get("chief_complaint")
            route = route_symptom_track(chief_complaint, self.scenario.routing)
            self._temp_vars["route_to"] = route.route_to
            if node.get("set_slot"):
                self._apply_updates(node["set_slot"])
            transition = self._evaluate_transitions(node)
            self._apply_updates(transition.updates)
            return transition.next_node
        transition = self._evaluate_transitions(node)
        self._apply_updates(transition.updates)
        return transition.next_node

    def _get_node(self, node_id: str) -> dict[str, Any]:
        return self.scenario.nodes[node_id]

    def _next_node_from_transitions(self, node: dict[str, Any]) -> _TransitionResult:
        transitions = node.get("transitions", [])
        if not transitions:
            return _TransitionResult(next_node=node.get("id", ""), updates={})
        first = transitions[0]
        return _TransitionResult(next_node=first.get("to"), updates=first.get("set", {}))

    def _evaluate_transitions(self, node: dict[str, Any]) -> _TransitionResult:
        for transition in node.get("transitions", []):
            condition = transition.get("when")
            if condition is None or self._eval_condition(condition):
                next_node = transition.get("to")
                if next_node == "LAST_NODE":
                    next_node = self.last_node or node.get("id")
                return _TransitionResult(
                    next_node=next_node,
                    updates=transition.get("set", {}),
                )
        return _TransitionResult(next_node=node.get("id"), updates={})

    def _eval_condition(self, condition: str) -> bool:
        expr = condition.strip()
        if expr == "default":
            return True

        equals_match = re.match(r"^(\w+)\s*==\s*(.+)$", expr)
        if equals_match:
            name = equals_match.group(1)
            raw_value = equals_match.group(2).strip()
            if raw_value.lower() == "true":
                return self._get_value(name) is True
            if raw_value.lower() == "false":
                return self._get_value(name) is False
            if raw_value.startswith("'") and raw_value.endswith("'"):
                expected = raw_value.strip("'")
                return self._get_value(name) == expected
            return self._get_value(name) == raw_value

        contains_match = re.match(r"^(\w+)\s+containsAny\((.+)\)$", expr)
        if contains_match:
            name = contains_match.group(1)
            raw_list = contains_match.group(2)
            try:
                normalized = raw_list.replace("'", '"')
                candidates = json.loads(normalized)
            except json.JSONDecodeError:
                candidates = []
            value = self._get_value(name) or ""
            return any(token in str(value) for token in candidates)

        return False

    def _get_value(self, name: str) -> Any:
        if name in self._temp_vars:
            return self._temp_vars[name]
        return self.slot_manager.get(name)

    def _apply_updates(self, updates: dict[str, Any]) -> None:
        if updates:
            self.slot_manager.update(updates)

    def _extract_slots(self, user_input: str, node: dict[str, Any]) -> None:
        extractors = node.get("extractors", [])
        for extractor in extractors:
            slot = extractor.get("slot")
            if not slot:
                continue
            value = self._extract_value(user_input, extractor)
            if value is not None:
                self.slot_manager.set(slot, value)

    def _extract_value(self, user_input: str, extractor: dict[str, Any]) -> Any:
        ext_type = extractor.get("type")
        text = user_input.strip()
        if ext_type == "free_text":
            return text or None
        if ext_type == "yes_no":
            return self._extract_yes_no(text, extractor)
        if ext_type == "yes_no_or_free_text":
            result = self._extract_yes_no(text, extractor)
            if isinstance(result, bool):
                return result
            return text or None
        if ext_type == "choice":
            normalized = text.replace(" ", "")
            for choice in extractor.get("choices", []):
                for synonym in choice.get("synonyms", []):
                    if synonym.replace(" ", "") in normalized:
                        return choice.get("value")
            return None
        if ext_type == "contains_any":
            source = extractor.get("source")
            source_value = self.slot_manager.get(source, "")
            for token in extractor.get("any", []):
                if token in str(source_value):
                    return True
            return False
        if ext_type == "number_0_10":
            match = re.search(r"\d+", text)
            if not match:
                return None
            value = int(match.group())
            return max(0, min(10, value))
        return None

    def _extract_yes_no(self, text: str, extractor: dict[str, Any]) -> bool | None:
        lowered = text.lower()
        yes_tokens = extractor.get("yes") or ("네", "예", "응", "맞", "그래")
        no_tokens = extractor.get("no") or ("아니", "아니요", "아뇨", "싫", "못")
        for token in yes_tokens:
            if str(token).lower() in lowered:
                return True
        for token in no_tokens:
            if str(token).lower() in lowered:
                return False
        return None
