from server.agents.emergency import EmergencyDetector


def test_emergency_detector_matches_strong_red_flag() -> None:
    detector = EmergencyDetector("server/scenarios/emergency_keywords.json")
    match = detector.detect("갑자기 한쪽 팔에 힘이 안 들어요")

    assert match is not None
    assert match.match_type == "strong_red_flag"
    assert match.category == "neuro_stroke_like"


def test_emergency_detector_matches_fallback_trigger() -> None:
    detector = EmergencyDetector("server/scenarios/emergency_keywords.json")
    match = detector.detect("오늘 처음 겪는 어지럼이에요")

    assert match is not None
    assert match.match_type == "fallback_trigger"
    assert match.category == "acute_change"
