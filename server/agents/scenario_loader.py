import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ScenarioDefinition:
    scenario_id: str
    version: str
    nodes: dict[str, dict[str, Any]]
    start_node: str
    routing: dict[str, Any]
    globals: dict[str, Any]
    emergency: dict[str, Any]
    slots: dict[str, Any]
    policy: dict[str, Any]
    context: dict[str, Any]


def _validate_nodes(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    if not nodes:
        raise ValueError("Scenario nodes are empty.")
    nodes_by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            raise ValueError("Scenario node missing id.")
        if node_id in nodes_by_id:
            raise ValueError(f"Duplicate node id: {node_id}")
        nodes_by_id[node_id] = node
    return nodes_by_id


def _validate_transitions(nodes: dict[str, dict[str, Any]]) -> None:
    for node in nodes.values():
        for transition in node.get("transitions", []):
            target = transition.get("to")
            if not target:
                raise ValueError(f"Transition missing target in {node.get('id')}")
            if target in {"LAST_NODE"}:
                continue
            if target not in nodes:
                raise ValueError(
                    f"Transition target '{target}' not found from {node.get('id')}"
                )


def _load_json_with_comments(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    raw = re.sub(r"//.*", "", raw)
    return json.loads(raw)


def load_scenario(path: str | Path) -> ScenarioDefinition:
    scenario_path = Path(path)
    data = _load_json_with_comments(scenario_path)
    nodes_list = data.get("nodes")
    if not isinstance(nodes_list, list):
        raise ValueError("Scenario 'nodes' must be a list.")
    nodes = _validate_nodes(nodes_list)
    _validate_transitions(nodes)
    start_node = "START" if "START" in nodes else nodes_list[0]["id"]
    return ScenarioDefinition(
        scenario_id=data.get("scenario_id", scenario_path.stem),
        version=data.get("version", "unknown"),
        nodes=nodes,
        start_node=start_node,
        routing=data.get("routing", {}),
        globals=data.get("globals", {}),
        emergency=data.get("emergency", {}),
        slots=data.get("slots", {}),
        policy=data.get("policy", {}),
        context=data.get("context", {}),
    )
