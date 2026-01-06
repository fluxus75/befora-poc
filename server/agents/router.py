from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RouteResult:
    route_to: str
    track_id: str


def route_symptom_track(chief_complaint: str | None, routing: dict[str, Any]) -> RouteResult:
    symptom_config = routing.get("symptom_track", {})
    tracks = symptom_config.get("tracks", [])
    default = symptom_config.get("default", {})
    normalized = (chief_complaint or "").replace(" ", "")
    for track in tracks:
        when = track.get("when", {})
        for token in when.get("any_contains", []):
            if token.replace(" ", "") in normalized:
                return RouteResult(route_to=track.get("to"), track_id=track.get("id"))
    return RouteResult(
        route_to=default.get("to", "Q1_1_CLARIFY"),
        track_id=default.get("id", "OTHER"),
    )
