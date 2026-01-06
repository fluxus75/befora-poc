from pathlib import Path

from server.agents.dsl_runner import DSLScenarioRunner


def test_yes_no_extractor_uses_custom_tokens() -> None:
    scenario_path = Path(__file__).resolve().parent.parent / "scenarios" / "scenario.json"
    runner = DSLScenarioRunner(scenario_path)
    extractor = {
        "type": "yes_no",
        "yes": ["괜찮", "가능"],
        "no": ["바쁘", "안 돼"],
    }

    assert runner._extract_value("지금은 괜찮아요", extractor) is True
    assert runner._extract_value("지금은 좀 바쁘네요", extractor) is False


def test_yes_no_or_free_text_falls_back_to_text() -> None:
    scenario_path = Path(__file__).resolve().parent.parent / "scenarios" / "scenario.json"
    runner = DSLScenarioRunner(scenario_path)
    extractor = {
        "type": "yes_no_or_free_text",
        "yes": ["괜찮", "가능"],
        "no": ["바쁘", "안 돼"],
    }

    assert runner._extract_value("가능해요", extractor) is True
    assert runner._extract_value("다른 내용입니다", extractor) == "다른 내용입니다"
