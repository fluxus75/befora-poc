from server.agents.router import route_symptom_track


def test_route_symptom_track_matches_keywords() -> None:
    routing = {
        "symptom_track": {
            "tracks": [
                {"id": "COGNITIVE", "when": {"any_contains": ["기억"]}, "to": "Q2A_1"},
                {"id": "DIZZINESS", "when": {"any_contains": ["어지"]}, "to": "Q2B_1"},
            ],
            "default": {"id": "OTHER", "to": "Q1_1_CLARIFY"},
        }
    }

    result = route_symptom_track("기억력이 나빠요", routing)
    assert result.track_id == "COGNITIVE"
    assert result.route_to == "Q2A_1"


def test_route_symptom_track_falls_back_to_default() -> None:
    routing = {
        "symptom_track": {
            "tracks": [
                {"id": "HEADACHE", "when": {"any_contains": ["두통"]}, "to": "Q2C_1"}
            ],
            "default": {"id": "OTHER", "to": "Q1_1_CLARIFY"},
        }
    }

    result = route_symptom_track("소화가 안 돼요", routing)
    assert result.track_id == "OTHER"
    assert result.route_to == "Q1_1_CLARIFY"
